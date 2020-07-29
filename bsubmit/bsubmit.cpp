/*
 * Copyright International Business Machines Corp, 2020.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <pwd.h>
#include <grp.h>

#include <cstdlib>
#include <iostream>
#include <cstring>
#include <string>
#include <fstream>
#include <sstream>
#include <vector>


const bool BSUB_DEBUG = false;

std::string getClusterName()
{
    std::string cname, readline;
    FILE * fp = popen("lsid", "r");
    if (fp != NULL) {
        char buffer[4096];
        std::string namepre = "My cluster name is ";
        while(fgets(buffer, sizeof(buffer) - 1, fp) != NULL) {
            readline = buffer;
            size_t pos = readline.find(namepre);
            if (pos !=  std::string::npos) {
                cname = readline.substr(pos + namepre.length());
                while ((pos = cname.find('\n')) != std::string::npos) {
                    cname.erase(pos);
                }
                break;
            }
        }
    }

    pclose(fp);
    return cname;
}

std::string getMappingFilePath()
{
    std::string filepath;
    char buf[1024];

    char *confdir = getenv("LSF_ENVDIR");
    if (confdir == NULL) {
        // try uniform path
        memset(buf, 0, sizeof(buf));
        int count = readlink("/etc/lsf.conf", buf, sizeof(buf) - 1);
        if (count > 0) {
            char * pos = strstr(buf, "/lsf.conf");
            if (pos != NULL) {
                *pos = '\0';
                confdir = buf;
            }
        }
    }
    if (confdir != NULL) {
        filepath = confdir;
        filepath.append("/lsf.usermapping");
    }
    return filepath;
}



void strtrim(std::string & str)
{
    size_t pos;
    while ((pos = str.find("\t")) != std::string::npos) {
        str.replace(pos, 1, " ");
    }

    str.erase(0, str.find_first_not_of(" "));
    str.erase(str.find_last_not_of(" ") + 1);

    while ((pos = str.find(", ")) != std::string::npos) {
        str.replace(pos, 2, ",");
    }
    while ((pos = str.find(" ,")) != std::string::npos) {
        str.replace(pos, 2, ",");
    }
    while ((pos = str.find(" =")) != std::string::npos) {
        str.replace(pos, 2, "=");
    }
    while ((pos = str.find("= ")) != std::string::npos) {
        str.replace(pos, 2, "=");
    }
    while ((pos = str.find("  ")) != std::string::npos) {
        str.replace(pos, 2, " ");
    }
}


void split(std::vector<std::string> & tokens, const std::string & str, char delim = ' ')
{
    std::stringstream ss(str);
    std::string token;
    while (getline(ss, token, delim)) {
        strtrim(token);
        if (!token.empty()) {
            tokens.push_back(token);
        }
    }
}


bool userMatch(std::string user, std::string ug)
{
    if (user.compare(ug) == 0) {
        return true;
    }

    struct passwd * pw = getpwnam(user.c_str());
    if(pw == NULL){
        return false;
    }

    int ngroups = 0;
    getgrouplist(pw->pw_name, pw->pw_gid, NULL, &ngroups);
    gid_t groups[ngroups];
    getgrouplist(pw->pw_name, pw->pw_gid, groups, &ngroups);

    for (int i = 0; i < ngroups; i++){
        struct group * gr = getgrgid(groups[i]);
        if(gr == NULL){
            continue;
        }
        if (ug.compare(gr->gr_name) == 0) {
            return true;
        }
    }

    return false;
}

std::vector<uid_t> getClusterAdmin(std::string clustername)
{
    std::vector<uid_t> adminuids;

    std::string clustercmd = "lsclusters -l " + clustername;
    FILE * fp = popen(clustercmd.c_str(), "r");
    if (fp != NULL) {
        char buffer[4096];
        std::string adminpre = "LSF administrators: ";
        std::string readline;
        while(fgets(buffer, sizeof(buffer) - 1, fp) != NULL) {
            readline = buffer;
            size_t pos = readline.find(adminpre);
            if (pos !=  std::string::npos) {
                std::string adminstr = readline.substr(pos + adminpre.length());
                while ((pos = adminstr.find('\n')) != std::string::npos) {
                    adminstr.erase(pos);
                }
                std::vector<std::string> nametokens;
                split(nametokens, adminstr, ' ');
                for (int i = 0; i < nametokens.size(); i++) {
                    struct passwd *pw = getpwnam(nametokens[i].c_str());
                    if (pw == NULL) {
                        continue;
                    }
                    adminuids.push_back(pw->pw_uid);
                }
                break;
            }
        }
    }

    pclose(fp);
    return adminuids;
}

bool fileExists(std::string fpath)
{
    struct stat st;
    return (stat(fpath.c_str(), &st) == 0);
}


bool fileHasCorrectAttr(std::string fpath, std::vector<uid_t> owners)
{
    bool validowner = false, validmode = false;
    struct stat st;

    if (stat(fpath.c_str(), &st) != -1){
        for (int i = 0; i < owners.size(); i++) {
            if (st.st_uid == owners[i]) {
                validowner = true;
                break;
            }
        }
        if (((st.st_mode & S_IRWXU) == (S_IRUSR | S_IWUSR)) &&
            ((st.st_mode & S_IRWXG) == S_IRGRP) &&
            ((st.st_mode & S_IRWXO) == S_IROTH)) {
            validmode = true;
        }
    }

    return (validowner && validmode);
}

bool verifyUserMapping(std::string fpath, std::string execName)
{
    bool result = false;

    struct passwd * userpsw = getpwuid(getuid());
    if (userpsw == NULL) {
        return false;
    }
    std::string userName = userpsw->pw_name;

    std::ifstream ifs;
    ifs.open(fpath.c_str(), std::ifstream::in);
    if (!ifs.is_open()) {
        std::cout << "Failed to open user mapping file in " << fpath << std::endl;
        return false;
    }

    std::string buf;
    while (getline(ifs, buf)) {
        strtrim(buf);
        if (buf.empty() || buf[0] == '#') {
            continue;
        }

        std::vector<std::string> tokens;
        split(tokens, buf);
        if (tokens.size() != 2) {
            continue;
        }

        std::vector<std::string> userTokens, execTokens;
        split(userTokens, tokens[0], ',');
        split(execTokens, tokens[1], ',');
        bool matchUser = false, matchExec = false;

        for(int i = 0; i < userTokens.size(); ++i) {
            if (userMatch(userName, userTokens[i])) {
                matchUser = true;
                break;
            }
        }
        if (matchUser) {
            for (int j = 0; j < execTokens.size(); ++j) {
                if (userMatch(execName, execTokens[j])) {
                    matchExec = true;
                    break;
                }
            }
        }

        if (matchUser && matchExec) {
            result = true;
            break;
        }
    }

    ifs.close();
    return result;
}


void runcmd(std::string cmd)
{
    std::string readline;
    FILE * fp = popen(cmd.c_str(), "r");
    if (fp != NULL) {
        char buffer[4096];
        while(fgets(buffer, sizeof(buffer) - 1, fp) != NULL) {
            std::cout << buffer;
        }
    }

    pclose(fp);
}

int changeUser(char * execUser)
{

    if (geteuid() != 0) {
        std::cout << "This program must be run with root privileges." << std::endl;
        return -1;
    }

    struct passwd * execpsw = getpwnam(execUser);
    if (execpsw == NULL) {
        std::cout << "The user name " << execUser << " is not valid." << std::endl;
        return -1;
    }
    uid_t execuid = execpsw->pw_uid;

    std::string clustername = getClusterName();
    if (clustername.empty()) {
        //std::cout << "Cannot get LSF cluster name" << std::endl;
        return -1;
    }

    std::vector<uid_t> admins = getClusterAdmin(clustername);
    if (admins.size() < 1) {
        //std::cout << "Cannot get cluster admins" << std::endl;
        return -1;
    }

    std::string mappingfile = getMappingFilePath();
    if (mappingfile.empty()) {
        std::cout << "The LSF environment is not ready. Source the LSF environment to resolve this issue." << std::endl;
        return -1;
    }

    if (!fileExists(mappingfile)) {
        std::cout << "The user mapping file " << mappingfile << " does not exist." << std::endl;
        return -1;
    }

    if (!fileHasCorrectAttr(mappingfile, admins)) {
        std::cout << "User mapping file must be owned by the LSF administrators with '644' permissions." << std::endl;
        return -1;
    }
    
    if (verifyUserMapping(mappingfile, execUser)) {
        setuid(execuid);
    } else {
        std::cout << "Failed to submit the job as user " << execUser << std::endl;
        return -1;
    }
    if (BSUB_DEBUG)
        std::cout << "now uid is " << getuid() << std::endl;

    return 0;
}

int main(int argc, char **argv)
{
    std::string usage("Usage: bsubmit [--user <username>] <bsub options and commands>");

    if (argc < 2) {
        std::cout << usage << std::endl;
        return -1;
    }

    int pos = 0;
    if (strcmp(argv[1], "--user") == 0) {
        if (argc < 4) {
            std::cout << usage << std::endl;
            return -1;
        }
        if (changeUser(argv[2]) != 0) {
            return -1;
        }
        pos = 3;
    } else {
        pos = 1;
    }

    std::string bsubcmd = "bsub";
    for (int i = pos; i < argc; i++) {
        bsubcmd.append(" ");
        bsubcmd.append(argv[i]);
    }
    runcmd(bsubcmd);

    return 0;
}

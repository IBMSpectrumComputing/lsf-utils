# Copyright International Business Machines Corp, 2021
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import json
import inspect
import subprocess

from errbot import BotPlugin, botcmd


class LSF(BotPlugin):
    """
    LSF plugin supports talking with your LSF cluster
    """

    config = None
    jobs = {}

    def monitor_jobs(self):
        # TODO: perforamnce concern if too many jobs
        for jobid, username in list(self.jobs.items()):
            cmd = ['bjobs', '-o', 'STAT', '-noheader'] + [jobid]

            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            outs, _ = proc.communicate()
            if len(outs) > 0:
                status = outs.decode('utf-8').rstrip()
                if status == 'DONE' or status == 'EXIT':
                    del self.jobs[jobid]

                    # for a user in a group, the user name is postfixed at the last `/`
                    # get the user name and notify the user directly when job is finished
                    start_pos = username.rfind('/')
                    if start_pos >= 0:
                        username = username[start_pos+1:]

                    result = 'Notification: job <' + jobid + '> is ' + str(status)
                    self.send(self.build_identifier('@' + username), f'\`\`\`{result}\`\`\`')


    def activate(self):
        super().activate()
        self.start_poller(5, self.monitor_jobs)

    ###########################################################################
    # command line without permission control
    ###########################################################################
    @botcmd(split_args_with=None)
    def lsfkc(self, msg, args):
        return 'https://www.ibm.com/support/knowledgecenter/SSWRJV_10.1.0/lsf_welcome/lsf_kc_get_started.html'

    ###########################################################################
    # command line allowed by users in allowlist
    ###########################################################################
    @botcmd(split_args_with=None)
    def lsid(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = ['lsid'] + args
        return exec_LSF_cmd(cmd)

    # TODO: register more notification conditions
    @botcmd(split_args_with=None)
    def register(self, msg, args):
        jobid = args[0]
        user = args[1]

        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        if not jobid.isnumeric():
            return 'Registration failed. Error: the job id is not valid'
        if not user.startswith('@'):
            return 'Registration failed. Error: the target user name should be prefixed with `@` '

        # TODO: check if job is finished already
        cmd = ['bjobs', '-o', 'JOBID', '-noheader'] + [jobid]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        outs, _ = proc.communicate()
        if len(outs) > 0:
            jid = outs.decode('utf-8').rstrip()
            if jid != jobid:
                return 'Registration failed. Error: job <' + jobid + '> is not an existing job in LSF.'
        self.jobs[jobid] = user

        self.log.debug('register notification for job <' + jobid + '> to user ' + str(msg.frm))

        result = 'Job <' + jobid + '> is registered to be notified <' + user[1:] + '> when it is finished.'
        return f'\`\`\`{result}\`\`\`'

    @botcmd(split_args_with=None)
    def bsub(self, msg, args):
        username = str(msg.frm)[1:]
        if not self.is_allowed(username):
            return default_reject_message

        for arg in args:
            if arg.startswith('-user'):
                return 'Error: you are not allowed to user `-user` option'

        realuser = self.get_mapped_user(username)
        if realuser != username:
            cmd = ['bsub', '-user', realuser] + args
        else:
            cmd = ['bsub'] + args

        message = exec_LSF_cmd(cmd)

        # record job information for monitoring
        result = re.search(r'<(\d*)>', message)
        if result:
            jobid = result.group(1)
            self.jobs[jobid] = str(msg.frm)

        return message

    @botcmd(split_args_with=None)
    def bjobs(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        # TODO: maybe more access control to query jobs
        cmd = ['bjobs'] + args
        return exec_LSF_cmd(cmd)

    # TODO: optimize code
    @botcmd(split_args_with=None)
    def bacct(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bapp(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def battr(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bbot(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bchkpnt(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bclusters(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bdata(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bentags(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bgadd(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bgdel(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bgmod(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bgpinfo(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bhist(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bhosts(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bhpart(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bimages(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bjdepinfo(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bjgroup(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bkill(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def blcstat(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def blhosts(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def blimits(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def blinfo(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def blkill(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def blparams(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def blstat(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bltasks(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def blusers(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bmgroup(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bmig(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bmod(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bparams(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bpeek(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bpost(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bqueues(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bread(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def brequeue(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bresize(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bresources(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def brestart(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bresume(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def brlainfo(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def brsvjob(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def brsvs(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def brsvsub(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bsla(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bslots(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bstage(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bstatus(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bstop(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bswitch(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def btop(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bugroup(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def busers(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def lsacct(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def lsclusters(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def lshosts(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def lsinfo(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def lsload(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def lsloadadj(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def lsmake(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def lspasswd(self, msg, args):
        if not self.is_allowed(str(msg.frm)[1:]):
            return default_reject_message

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    ###########################################################################
    # command line allowed by the administrator user
    ###########################################################################
    @botcmd(split_args_with=None)
    def badmin(self, msg, args):
        if not self.is_admin(str(msg.frm)[1:]):
            return 'Error: you are not allowed to manage LSF'

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bconf(self, msg, args):
        if not self.is_admin(str(msg.frm)[1:]):
            return 'Error: you are not allowed to configure LSF'

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def brsvadd(self, msg, args):
        if not self.is_admin(str(msg.frm)[1:]):
            return 'Error: you are not allowed to manage AR in LSF'

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def brsvdel(self, msg, args):
        if not self.is_admin(str(msg.frm)[1:]):
            return 'Error: you are not allowed to manage AR in LSF'

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def brsvmod(self, msg, args):
        if not self.is_admin(str(msg.frm)[1:]):
            return 'Error: you are not allowed to manage AR in LSF'

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def brun(self, msg, args):
        if not self.is_admin(str(msg.frm)[1:]):
            return 'Error: you are not allowed to run a job forcely in LSF'

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def lsadmin(self, msg, args):
        if not self.is_admin(str(msg.frm)[1:]):
            return 'Error: you are not allowed to manage LSF'

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def lsfshutdown(self, msg, args):
        if not self.is_admin(str(msg.frm)[1:]):
            return 'Error: you are not allowed to shutdown LSF'

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def bladmin(self, msg, args):
        if not self.is_admin(str(msg.frm)[1:]):
            return 'Error: you are not allowed to manage LS'

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def lsgrun(self, msg, args):
        if not self.is_admin(str(msg.frm)[1:]):
            return 'Error: you are not allowed remote execution in LSF'

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    @botcmd(split_args_with=None)
    def lsrun(self, msg, args):
        if not self.is_admin(str(msg.frm)[1:]):
            return 'Error: you are not allowed remote execution in LSF'

        cmd = [inspect.getframeinfo(inspect.currentframe()).function] + args
        return exec_LSF_cmd(cmd)

    ###########################################################################
    # permission checking functions
    ###########################################################################
    def is_admin(self, user):
        if self.config == None:
           self.config = load_config(self.log)

        # none security mode: allows everyone to execute LSF command
        if self.config == None:
            return True

        if 'administrator' in self.config:
            return user == self.config['administrator']

        return False

    def is_allowed(self, user):
        if self.config == None:
           self.config = load_config(self.log)

        # none security mode: allows everyone to execute LSF command
        if self.config == None:
            return True

        if 'administrator' in self.config:
            return user == self.config['administrator']

        if 'allowlist' in self.config:
            return user in self.config['allowlist']

        return False

    def get_mapped_user(self, user):
        if self.config == None:
           self.config = load_config(self.log)

        # none security mode: uses submission user
        if self.config == None:
            return user

        if 'usermap' in self.config:
            for usermap in self.config['usermap']:
                if user in usermap:
                    return usermap[user]

        # if there is no mapped user, use submission user
        return user


# helper functions
def exec_LSF_cmd(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        outs, errs = proc.communicate(timeout=5)
    except TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()

    result = outs.decode('utf-8')

    return f'\`\`\`{result}\`\`\`'

def load_config(log):
    path = os.getenv('LSF_PLUGIN_TOP')
    if path is None:
        log.debug('LSF chatops robot is running in non-security mode')
        return None

    log.debug('LSF chatops robot is running in security mode')

    cfile = os.path.join(path, 'config.json')
    with open(cfile) as f:
        config = json.load(f)

    return config

default_reject_message = 'Error: you are not allowed to communicate with LSF'

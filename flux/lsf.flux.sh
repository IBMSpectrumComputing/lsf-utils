#!/bin/bash

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

################################################################################
#
# configure a location to a shared directory
# the location stores flux configuration files accessed by all Flux member nodes
################################################################################

LSF_FLUX_SHARE_DIR=${HOME}/shared/

if [ "${LSB_JOBID}" == "" ]; then
    echo "[warning] this script should be run as a job in LSF."
fi

WORKERS=$(echo ${LSB_HOSTS} | tr ' ' '\n'| uniq | sed 1d | xargs)
if [ "${WORKERS}" == "" ]; then
    echo "[info] the Flux cluster with a single node is starting."
    flux start

    echo "[info] bye!"
    exit
fi

# a flux cluster across hosts
LSF_FLUX_TOP=${LSF_FLUX_SHARE_DIR}/.lsf.flux/${LSB_JOBID}

echo "[info] generating Flux key for communication."
mkdir -p ${LSF_FLUX_TOP} 
flux keygen ${LSF_FLUX_TOP}/key


echo "[info] preparing configuration file for the Flux cluster."
mkdir -p ${LSF_FLUX_TOP}/config/
cat <<EOF > ${LSF_FLUX_TOP}/config/cluster.toml

[bootstrap]
curve_cert="${LSF_FLUX_TOP}/key"

hosts = [
    { host = "$(hostname)", bind = "tcp://0.0.0.0:9001", connect = "tcp://$(hostname):9001"},
EOF

# add computing nodes to the flux cluster
IFS=' ' read -ra HOSTS <<< "${WORKERS}"
for host in ${HOSTS[@]}
do
    echo "    { host = \"${host}\" }," >> ${LSF_FLUX_TOP}/config/cluster.toml
done

# end of the configure file
echo "]" >> ${LSF_FLUX_TOP}/config/cluster.toml


echo "[info] starting Flux brokers on nodes ${WORKERS}."
blaunch -no-wait -z "${WORKERS}" flux broker -c ${LSF_FLUX_TOP}/config/

echo "[info] the Flux cluster with multiple nodes is starting in the job <${LSB_JOBID}>."
flux broker -c ${LSF_FLUX_TOP}/config/

echo "[info] cleaning generated files"
rm -rf ${LSF_FLUX_TOP}

echo "[info] bye!"


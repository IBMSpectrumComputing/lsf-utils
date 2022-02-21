#!/bin/python3
#
# Copyright International Business Machines Corp, 2022
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

from airflow.plugins_manager import AirflowPlugin
from airflow.executors.base_executor import BaseExecutor

import subprocess
import re

class LSFExecutor(BaseExecutor):
    def __init__(self):
        self.jobs = {}
        self.queues = {}

        super().__init__()

    def start(self): 
        self.log.info("[ LSF ] starting LSF executor")

        q = run_cmd(['bqueues', '-o', 'QUEUE_NAME', '-noheader'], self.log)
        if q == None:
            self.log.warning("LSF: there is no queue found")
            return

        self.queues = {q: True for q in q.strip('\n').split('\n')}

        self.log.info(f"[ LSF ] there are {len(self.queues)} queues: {','.join(self.queues)}")

    def execute_async(self, key, command, queue=None, executor_config=None):
        self.log.info("[ LSF ] executing async(). key = %s command = %s queue = %s config = %s" % (key, command, queue, executor_config))

        self.validate_command(command)

        options=['-J', f'{key.dag_id}-{key.task_id}-{key.run_id}']

        # the queue name is setting when it is an LSF queue name
        if self.queues.get(queue) != None:
            options.extend(['-q', queue])

        jobid = bsub(options, command, self.log)
        if (int(jobid) > 0):
            self.jobs[jobid] = key

    def sync(self):
        self.log.info("LSF: executing sync()")

        # TODO: bjobs job_ids instead of multiple bjobs. It may be all in one or sub set of jobs by one request
        for jid in list(self.jobs.keys()):
            stat = bjobs(jid, self.log)
            if stat is None:
                del self.jobs[jid]
                continue

            if stat == 'DONE':
                self.success(self.jobs[jid])
                del self.jobs[jid]
            if stat == 'EXIT':
                self.fail(self.jobs[jid])
                del self.jobs[jid]

    def end(self):
        self.log.info("LSF: executing end()")

        for jid in list(self.jobs.keys()):
            bkill(jid, self.log)
            del self.jobs[jid]

        self.heartbeat()

    def terminate(self):
        self.log.info("LSF: executing terminate()")

        for jid in self.jobs.keys():
            bkill(jid, self.log)
            del self.jobs[jid]

def bkill(jobid, log):
    cmd = ["bkill", "-C", "job is killed because airflow is ended", jid]
    log.info(f'[ LSF ] request: {cmd}')

    run_cmd(cmd, log)

def bjobs(jobid, log):
    cmd = ['bjobs', '-o', 'stat', '-noheader', jobid]
    log.info(f'[ LSF ] request: {cmd}')

    reply = run_cmd(cmd, log)
    log.info(f'[ LSF ] reply: {reply}')

    stat = reply
    if reply is not None:
        stat = reply.strip()

    return stat

def bsub(options, cmd, log):
    # DEBUG: submit to local host for test
    bsub_cmd = ['bsub', '-m', 'scurvily1']
    bsub_cmd.extend(options)
    bsub_cmd.extend(cmd)
    log.info(f'[ LSF ] request: {bsub_cmd}')

    message = run_cmd(bsub_cmd, log)
    log.info(f'[ LSF ] reply: {message}')

    # record job information for monitoring
    jobid = '0'
    result = re.search(r'<(\d*)>', message)
    if result:
        jobid = result.group(1)
    else:
        log.info(f'[ LSF ] error: failed to get jobid {message}')

    return jobid 


def run_cmd(cmd, log):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        outs, errs = proc.communicate(timeout=5)
        log.info(f'[ LSF ] stdout: {outs}')
        log.info(f'[ LSF ] stderr: {errs}')
    except TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
    
    result = outs.decode('utf-8')
    return result


# Defining the plugin class
class LSFExecutorPlugin(AirflowPlugin):
    name = "LSF"
    executors = [LSFExecutor]


# DEBUG: test only
if __name__ == '__main__':
    e = LSFExecutor()
    e.start()

    cmd = ['sleep', '9527']
    jid = bsub([], cmd, e.log)

    stat = bjobs(jid, e.log)
    e.log.info(f'status is <{stat}>')

    bkill(jid, e.log)


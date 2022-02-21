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

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator


with DAG('process_text',
        description = 'say hi instead of hello from a text file',
        schedule_interval = None,
        start_date = datetime(2022, 1, 13),
        catchup = False) as dag:

    the_end = DummyOperator(task_id = 'the_end',)
    
    file_name = '/tmp/airflow_lsf_demo.txt'
    generate_text_file = BashOperator(
        task_id = 'generate_text_file',
        bash_command = f'echo "Hello, Airflow in LSF!" > {file_name}',
    )

    say_hi = BashOperator(
        task_id = 'say_hi',
        bash_command = f'sed -i s/Hello/Hi/ {file_name}',
    )
    
    generate_text_file >> say_hi
    
    wait_and_let_go = BashOperator(
        task_id = 'wait_and_let_go',
        bash_command = 'sleep 30',
    )
    wait_and_let_go >> say_hi
    
    say_hi >> the_end

if __name__ == "__main__":
   dag.cli()

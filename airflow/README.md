# LSF Executor for Airflow

## How to use it 
copy lsf executor plugin into `plugins` directory
```
$ cp lsf_executor/lsf.py $AIRFLOW_HOME/plugins/
```

configure `lsf.LSFExecutor` to use LSF as executor of Airflow.
```
$ vim $AIRFLOW_HOME/airflow.cfg
executor = lsf.LSFExecutor
```

copy the example workflow into `dags` directory
```
$ cp examples/process_text.py $AIRFLOW_HOME/dags/
```

Now, you can trigger `process_text.py` workflow in the Airflow and run tasks in `LSF` cluster as jobs.


# LSF Flux Cluster Job

Use `lsf.flux.sh` script to create a light weighted job management Flux cluster for your own.
The [Flux](https://flux-framework.readthedocs.io/en/latest/) cluster manages resouces
allocated by `LSF` based on job's resource requirement.

## Usage

Submit the script as an interactive job to get a shell with Flux cluster deployed.
```bash
$ bsub -Is ./lsf.flux.sh
```

## Example

Create a Flux cluster in an `LSF` job with 2 nodes: 1 core on linux01 and 2 cores on linux02.
```bash
$ bsub -R '1*{affinity[core(1)]} + 1*{affinity[core(2)]}' -m 'linux01! linux02' -Is ./lsf.flux.sh 
Job <320> is submitted to default queue <interactive>.
<<Waiting for dispatch ...>>
<<Starting on linux01>>
[info] generating Flux key for communication.
[info] preparing configuration file for the Flux cluster.
[info] starting Flux brokers on nodes linux02.
[info] the Flux cluster with multiple nodes is running in job <320>.
lsfadmin@linux01:~/shared/test$ flux resource list
     STATE NNODES   NCORES    NGPUS NODELIST
      free      2        3        0 linux01,linux02
 allocated      0        0        0 
      down      0        0        0 
lsfadmin@linux01:~/shared/test$ flux mini submit sleep 9999
ƒ27fJYEVm
lsfadmin@linux01:~/shared/test$ flux mini submit sleep 9999
ƒ28LWmEnj
lsfadmin@linux01:~/shared/test$ flux mini submit sleep 9999
ƒ28s2vTGT
lsfadmin@linux01:~/shared/test$ flux mini submit sleep 9999
ƒ29MwgSzT
lsfadmin@linux01:~/shared/test$ flux jobs
       JOBID USER     NAME       ST NTASKS NNODES  RUNTIME NODELIST
   ƒ29MwgSzT lsfadmin sleep      PD      1      -        - -
   ƒ28s2vTGT lsfadmin sleep       R      1      1   5.914s linux02
   ƒ28LWmEnj lsfadmin sleep       R      1      1   7.110s linux01
   ƒ27fJYEVm lsfadmin sleep       R      1      1   8.634s linux02
```


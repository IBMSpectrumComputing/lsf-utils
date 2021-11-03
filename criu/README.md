# LSF checkpoint with CRIU

## Usage

To prepare checkpoint environment for [CRIU](https://criu.org/Main_Page),
echkpnt scripts should be downloaded and copy to your `LSF` environment.
```
$ cp echkpnt.criu erestart.criu $LSF_SERVERDIR
```

To use `CRIU` checkpoint method:
1. submit a job with method `criu`
```
$ bsub -k '/usr/local/work/chkpnt/ method=criu' ./counter
Job <477> is submitted to default queue <normal>.
```

2. checkpoint the job with killing
```
$ bchkpnt -k 477
Job <477> is being checkpointed
```

3. restart the checkpointed job
```
$ brestart /usr/local/work/chkpnt/ 477
Job <478> is submitted to queue <normal>.
```
## Debug
By default, `CRIU` checkpoint scripts log debug information to `/tmp` directory.
```
$ cat /tmp/lsf-job-477.cr.log
2021-11-02 19:09:27,035 lsf-criu-checkpoint[2670944]: start checkpointing ......
2021-11-02 19:09:27,035 lsf-criu-checkpoint[2670944]: ['-c', '-k', '-d', '477.tmp', '2669404']
2021-11-02 19:09:27,044 lsf-criu-checkpoint[2670944]: job process id: 2669408
2021-11-02 19:09:27,044 lsf-criu-checkpoint[2670944]: ['criu', 'dump', '-D', '/usr/local/work/chkpnt//477', '-t', '2669408', '--shell-job']
2021-11-02 19:09:27,864 lsf-criu-checkpoint[2670944]: b''
2021-11-02 19:09:27,864 lsf-criu-checkpoint[2670944]: b'Warn  (compel/arch/x86/src/lib/infect.c:340): Will restore 2669410 with interrupted system call\n'
2021-11-02 19:09:27,865 lsf-criu-checkpoint[2670944]: leave checkpointing ...
```


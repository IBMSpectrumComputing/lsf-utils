# LSF Event Archive Utility (`eventarchive.sh`)

A hardened, portable utility for IBM Spectrum LSF cluster administrators to safely archive or prune historical event log files (`lsb.events.*`).

---

## Features

- **2-Step Evacuation & Compression**:
  - **Step 1 (Fast Evacuation)**: Quickly moves all eligible event files out of the live `$LSF_LOGDIR` into the backup directory, immediately freeing disk space on the active LSF master daemon.
  - **Step 2 (Batch Compression)**: Compresses all uncompressed event files in the backup directory with `gzip`.
- **Oldest-First Processing**: Processes files in descending numerical order (highest/oldest sequence number first, e.g., `.25` $\rightarrow$ `.10` $\rightarrow$ `.1`).
- **Zero Collision Overwrite Risk**: Names archived files as `lsb.events.<YYYYMMDD_HHMMSS>.<X>.gz` to ensure natural chronological sorting and eliminate overwrite risks across annual log rotations.
- **Race Condition & Rotation Protection**:
  - Strictly excludes the active `lsb.events` and staging `lsb.events.0` files.
  - Detects if an active LSF event switch starts mid-operation and aborts remaining file moves safely.
  - Checks file existence right before moving to gracefully handle LSF cascade renames.
- **POSIX Portable**: Works seamlessly on Linux, AIX, macOS, and BSD systems (`/bin/sh`).
- **Dry-Run Preview**: Supports `-n` mode to test and preview actions without modifying files.

---

## Usage

```sh
./eventarchive.sh [OPTIONS]
```

### Options

| Flag | Parameter | Description | Default |
| :--- | :--- | :--- | :--- |
| `-d` | `DAYS` | Days of events to retain in logdir (integer $\ge 5$) | `30` |
| `-a` | `Y \| N` | `Y` = Archive and compress, `N` = Purge/delete | `Y` |
| `-b` | `BACKUP_PATH` | Destination directory for archived files | `$LSF_TOP/event_backup` |
| `-l` | `LOGDIR` | LSF log directory containing `lsb.events.*` | `$LSF_TOP/work/lsfpc/logdir` |
| `-n` | *(none)* | Dry-run mode (display planned operations without moving/deleting files) | `Disabled` |
| `-h` | *(none)* | Display help message and exit | |

> **Note**: This script does not use file locking and is intended to run sequentially (e.g. from a single cron job). Do not run multiple concurrent instances against the same directories.

---

## Examples

### 1. Dry-run to preview actions
```sh
./eventarchive.sh -l /opt/ibm/lsf/work/cluster1/logdir -b /nfs/lsf_backup -d 30 -n
```

### 2. Archive files older than 60 days
```sh
./eventarchive.sh -l /opt/ibm/lsf/work/cluster1/logdir -b /nfs/lsf_backup -d 60 -a Y
```

### 3. Purge files older than 90 days (without archiving)
```sh
./eventarchive.sh -l /opt/ibm/lsf/work/cluster1/logdir -d 90 -a N
```

---

## Running Automated Tests

An automated test suite is included in `test_eventarchive.sh` to validate input validation, safe archiving, purging, race condition handling, and file ordering:

```sh
sh test_eventarchive.sh
```

---

## License

Copyright International Business Machines Corp, 2020, 2026.
Licensed under the Apache License, Version 2.0.

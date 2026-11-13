#!/bin/sh
# Copyright International Business Machines Corp, 2020, 2026.
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
#----------------------------------------------------------
# Script to backup or prune LSF Events Files
#----------------------------------------------------------
#
# This script archives or prunes LSF Events files older than
# a specified number of days.
#
# NOTE: This script does not use file locking and is intended
# to run sequentially (e.g. from a single cron job). Do not
# run multiple concurrent instances against the same directories.
#
# Author: Larry Adams, IBM Inc., September 26th, 2012
# Hardened: IBM Bob, 2026
#----------------------------------------------------------

set -eu

# ==========================================================
# USER CONFIGURATION
# Edit these default values for your environment, or override
# them at runtime via command-line arguments or environment variables.
# ==========================================================
LSF_TOP="${LSF_TOP:-/usr/share/symphony/lsf/lsfpc}"
LSF_LOGDIR="${LSF_LOGDIR:-$LSF_TOP/work/lsfpc/logdir}"
BACKUP_PATH="${BACKUP_PATH:-$LSF_TOP/event_backup}"
DAYS="${DAYS:-30}"
ARCHIVE="${ARCHIVE:-Y}"
# ==========================================================

PROGNAME="$(basename "$0")"
DRY_RUN=0

usage() {
  cat <<EOF
Usage: $PROGNAME [OPTIONS]

Archive or prune IBM Spectrum LSF event files older than a specified number of days.

Options:
  -d DAYS         Days of events to retain in logdir (integer >= 5, default: ${DAYS})
  -a Y|N          Archive files ('Y') or purge/delete files ('N') (default: ${ARCHIVE})
  -b BACKUP_PATH  Destination directory for archived files (default: ${BACKUP_PATH})
  -l LOGDIR       LSF log directory containing lsb.events.* files (default: ${LSF_LOGDIR})
  -n              Dry-run mode (display planned operations without modifying files)
  -h              Show this help message

Note: Run sequentially. This script does not lock against concurrent executions.
EOF
  exit 1
}

log() {
  printf "[%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

error_exit() {
  log "FATAL: $1" >&2
  exit "${2:-1}"
}

# Parse CLI options (overrides script defaults directly without side-effects)
while getopts "d:a:b:l:nh" opt; do
  case "$opt" in
    d) DAYS="$OPTARG" ;;
    a) ARCHIVE="$(echo "$OPTARG" | tr '[:lower:]' '[:upper:]')" ;;
    b) BACKUP_PATH="$OPTARG" ;;
    l) LSF_LOGDIR="$OPTARG" ;;
    n) DRY_RUN=1 ;;
    h|*) usage ;;
  esac
done

# Validate Days
case "$DAYS" in
  ''|*[!0-9]*) error_exit "Days must be a positive integer." 2 ;;
esac

if [ "$DAYS" -lt 5 ]; then
  error_exit "Days cannot be less than 5." 2
fi

# Validate Archive mode
if [ "$ARCHIVE" != "Y" ] && [ "$ARCHIVE" != "N" ]; then
  error_exit "Archive option must be 'Y' or 'N'." 2
fi

# Validate LSF Log Directory (Fail explicitly, no guessing)
if [ -z "$LSF_LOGDIR" ]; then
  error_exit "LSF_LOGDIR is not configured. Please set LSF_LOGDIR in script or pass -l <path>." 4
fi

if [ ! -d "$LSF_LOGDIR" ]; then
  error_exit "Event file location not found: $LSF_LOGDIR. Please verify LSF_LOGDIR configuration." 4
fi

if [ ! -w "$LSF_LOGDIR" ]; then
  error_exit "LSF log directory is not writeable: $LSF_LOGDIR. Cannot remove event files." 5
fi

# Initial check: Verify an active event switch is not in progress before proceeding
if [ -e "${LSF_LOGDIR}/lsb.events.0" ]; then
  error_exit "Found lsb.events.0 file, which indicates an events switch is in process. Try again later..." 6
fi

# Validate Backup Path when archiving
if [ "$ARCHIVE" = "Y" ]; then
  if [ -z "$BACKUP_PATH" ]; then
    error_exit "BACKUP_PATH is not configured. Please set BACKUP_PATH in script or pass -b <path>." 4
  fi

  if [ ! -d "$BACKUP_PATH" ]; then
    if [ "$DRY_RUN" -eq 1 ]; then
      log "DRY-RUN: Would create backup directory: $BACKUP_PATH"
    else
      mkdir -p "$BACKUP_PATH" || error_exit "Failed to create event backup path: $BACKUP_PATH. Check permissions." 3
    fi
  fi

  if [ "$DRY_RUN" -eq 0 ] && [ ! -w "$BACKUP_PATH" ]; then
    error_exit "Backup path is not writeable: $BACKUP_PATH" 5
  fi
fi

#----------------------------------------------------------
# Perform Archive or Prune
#----------------------------------------------------------
if [ "$ARCHIVE" = "N" ]; then
  log "NOTE: Removing LSF Events files older than $DAYS days from $LSF_LOGDIR"
else
  log "NOTE: Evacuating LSF Events files older than $DAYS days from $LSF_LOGDIR to $BACKUP_PATH"
fi

batch_ts="$(date '+%Y%m%d_%H%M%S')"

# Item 1 hardening: Explicitly exclude active lsb.events and staging lsb.events.0
# Also exclude any existing .gz files from matching, and sort descending (oldest LSF files first: .25 -> .1)
file_list="$(find "$LSF_LOGDIR" -maxdepth 1 -type f -name 'lsb.events.*' ! -name 'lsb.events' ! -name 'lsb.events.0' ! -name '*.gz' -mtime "+$DAYS" 2>/dev/null | awk -F/ '{split($NF, a, "."); printf "%010d\t%s\n", a[length(a)], $0}' | sort -nr | cut -f2- || true)"

#----------------------------------------------------------
# Step 1: Evacuate or purge files (Oldest first)
#----------------------------------------------------------
if [ -n "$file_list" ]; then
  printf "%s\n" "$file_list" | while IFS= read -r src_file; do
    [ -n "$src_file" ] || continue

    # Item 2 hardening: Verify file existence immediately before processing
    # Handles race condition where LSF rotated or renamed files mid-run
    if [ ! -f "$src_file" ]; then
      log "WARNING: File disappeared or was renamed by LSF, skipping: $src_file"
      continue
    fi

    # Item 2 hardening: Re-verify lsb.events.0 has not appeared mid-run
    if [ -e "${LSF_LOGDIR}/lsb.events.0" ]; then
      log "WARNING: Found lsb.events.0 mid-operation (event switch in progress). Aborting remaining operations for safety."
      break
    fi

    filename="$(basename "$src_file")"

    if [ "$ARCHIVE" = "N" ]; then
      if [ "$DRY_RUN" -eq 1 ]; then
        log "DRY-RUN: Would remove $src_file"
      else
        log "Removing old event file: $filename"
        rm -f "$src_file"
      fi
    else
      # Format: lsb.events.<YYYYMMDD_HHMMSS>.<X>
      seq_num="${filename#lsb.events.}"
      dest_base="lsb.events.${batch_ts}.${seq_num}"
      dest_file="${BACKUP_PATH}/${dest_base}"

      if [ "$DRY_RUN" -eq 1 ]; then
        log "DRY-RUN: Would move $src_file -> $dest_file"
      else
        log "Evacuating: $filename -> $dest_base in $BACKUP_PATH"
        mv "$src_file" "$dest_file"
      fi
    fi
  done
else
  log "No event files older than $DAYS days found in $LSF_LOGDIR."
fi

#----------------------------------------------------------
# Step 2: Compress uncompressed event files in Backup directory
#----------------------------------------------------------
if [ "$ARCHIVE" = "Y" ]; then
  uncompressed_files="$(find "$BACKUP_PATH" -maxdepth 1 -type f -name 'lsb.events.*' ! -name '*.gz' 2>/dev/null || true)"
  if [ -n "$uncompressed_files" ]; then
    log "NOTE: Compressing uncompressed event files in $BACKUP_PATH"
    printf "%s\n" "$uncompressed_files" | while IFS= read -r f; do
      [ -f "$f" ] || continue
      if [ "$DRY_RUN" -eq 1 ]; then
        log "DRY-RUN: Would gzip $f"
      else
        log "Compressing: $(basename "$f")"
        gzip "$f"
      fi
    done
  fi
fi

log "Operation completed."

#!/bin/bash

# Use workflow script to run jobs in group. Assumes environment configuration
# has already been done by calling script (submit.sh).

cd "$(dirname $0)"

if [ -n "$CODAR_WORKFLOW_KILL_ON_PARTIAL_FAILURE" ]; then
    extra_args="--kill-on-partial-failure"
else
    extra_args=""
fi

start=$(date +%s)

# Main application run
"$CODAR_WORKFLOW_SCRIPT" --runner=$CODAR_WORKFLOW_RUNNER \
 --max-procs=$CODAR_CHEETAH_GROUP_MAX_PROCS \
 --producer-input-file=fobs.json \
 --log-file=codar.FOBrun.log \
 --status-file=codar.workflow.status.json \
 --log-level=$CODAR_CHEETAH_WORKFLOW_LOG_LEVEL

end=$(date +%s)
echo $(($end - $start)) > codar.cheetah.walltime.txt

# TODO: Post processing
#"{post_processing}" "{group_directory}"

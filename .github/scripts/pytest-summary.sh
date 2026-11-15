#!/usr/bin/env bash
# Write the outcome of a pytest run to the job summary and fail when the run
# cannot be trusted.
#
# usage: pytest-summary.sh LOG MIN_TESTS LABEL REPRODUCE
#
#   LOG        file with the output of `pytest | tee LOG`
#   MIN_TESTS  floor for passed + skipped + xfailed + xpassed
#   LABEL      job name shown in the summary heading
#   REPRODUCE  command that reruns this job locally
#
# It also records the seed that pytest-randomly printed ("Using
# --randomly-seed=1234"), and the command that reruns the same order.
#
# The exit status of pytest already fails the step that ran it. This check
# catches what a zero exit status hides: a run that collected fewer tests than
# before (a module that stopped being collected, a decorator that made tests
# vanish, a marker that deselected too much) or a log without a summary line.
#
# Adapted from noWorkflow's .github/scripts/pytest-summary.sh.
set -u

log=$1
min_tests=$2
label=$3
reproduce=$4
summary=${GITHUB_STEP_SUMMARY:-/dev/stdout}

line=""
if [ -f "$log" ]; then
  # "===== 338 passed, 5 skipped, 4 warnings in 1.81s =====", possibly with
  # " (0:01:15)" after the duration.
  line=$(grep -E '^=+ .* in [0-9.]+s( \([0-9:]+\))? =+$' "$log" | tail -n 1 || true)
fi

# pytest-randomly prints "Using --randomly-seed=1234" in the header.
seed=""
if [ -f "$log" ]; then
  seed=$(grep -oE -m1 'randomly-seed=[0-9]+' "$log" | grep -oE '[0-9]+$' || true)
fi

count=0
for kind in passed skipped xfailed xpassed; do
  n=$(grep -oE "[0-9]+ $kind" <<<"$line" | grep -oE '^[0-9]+' || true)
  count=$((count + ${n:-0}))
done

problem=""
if [ -z "$line" ]; then
  problem="no pytest summary line in $log"
elif grep -qE '[0-9]+ (failed|errors?)[, ]' <<<"$line"; then
  problem="the run has failures or errors"
elif [ "$count" -lt "$min_tests" ]; then
  problem="$count tests, below the floor of $min_tests (MIN_TESTS in the workflow)"
fi

{
  echo "### pytest ($label)"
  echo
  echo "- tests: $count (floor $min_tests)"
  echo "- summary: \`${line:-missing}\`"
  [ -n "$seed" ] && echo "- random order, seed: $seed"
  [ -n "$problem" ] && echo "- **failed:** $problem"
  echo
  echo "Reproduce locally:"
  echo '```'
  echo "$reproduce"
  echo '```'
  if [ -n "$seed" ]; then
    echo
    echo "Same order as this run:"
    echo '```'
    echo "$reproduce --randomly-seed=$seed"
    echo '```'
  fi
} >>"$summary"

if [ -n "$problem" ]; then
  echo "::error title=pytest ($label)::$problem"
  exit 1
fi

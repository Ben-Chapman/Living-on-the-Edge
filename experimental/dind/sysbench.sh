#!/bin/sh

###
# Wrapper script for sysbench dind testing
###

GREP_STRING="events.*(avg/stddev)"
# CPU Test
for test in cpu memory threads; do
  # The grep'ing, sed'ing and cut'ing transforms:
  # events (avg/stddev):           92755103.0000/0.00
  # into 92755103.0000,0.00
  echo -e "\nRunning $test test..."
  RES=$(sysbench $test run \
  | egrep ${GREP_STRING} \
  | sed -e 's|/|,|g' \
  | cut -d: -f2 |xargs)
  echo "$(hostname),$test,${RES}"
done

# Fileio testing
# sysbench fileio prepare --file-total-size=5G > /dev/null 2>&1

# sysbench fileio run --file-test-mode=rndrw --file-rw-ratio=2.5 --file-total-size=5G --threads=4

# sysbench fileio cleanup > /dev/null 2>&1

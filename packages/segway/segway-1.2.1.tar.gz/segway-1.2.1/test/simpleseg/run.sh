#!/usr/bin/env bash

## run.sh: test segway

## $Revision: -1 $

set -o nounset -o pipefail -o errexit

if [ $# != 0 ]; then
    echo usage: "$0"
    exit 2
fi

TMPDIR="$(mktemp -dp . "test-$(date +%Y%m%d).XXXXXX")"

echo >&2 "entering directory $TMPDIR"
cd "$TMPDIR"

if [ "${SEGWAY_TEST_CLUSTER_OPT:-}" ]; then
    cluster_arg="--cluster-opt=$SEGWAY_TEST_CLUSTER_OPT"
else
    cluster_arg="--cluster-opt="
fi

set -x

SEGWAY_RAND_SEED=1498730685 segway "$cluster_arg" \
    --include-coords="../include-coords.bed" \
    --tracks-from="../tracks.txt" --num-labels=4 \
    train "../simpleseg.genomedata" traindir

segway "$cluster_arg" --include-coords="../include-coords.bed" \
    identify "../simpleseg.genomedata" traindir identifydir

cd ..

../compare_directory.py ../simpleseg/touchstone ../simpleseg/${TMPDIR#"./"}

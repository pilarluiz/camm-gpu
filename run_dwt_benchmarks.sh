#!/usr/bin/env bash
# Per-benchmark sequential run: launch via run_simulations.py, wait via
# monitor_func_test.py (which also dumps a stats file), then save the
# L1D-window trace.csv as trace-<bench>.csv.
set -e
cd "$(dirname "$0")"

NAME=$1

./util/job_launching/run_simulations.py \
    -B rodinia-3.1:hotspot-rodinia-3.1:1 \
    -C A100-SASS \
    -T ./hw_run/rodinia-3.1/11.0 \
    -N rodinia-3.1-$NAME

./util/job_launching/monitor_func_test.py \
    -N rodinia-3.1-$NAME -v

./util/job_launching/get_stats.py -N rodinia-3.1-$NAME | tee stats-rodinia-3.1-$NAME.csv

mv trace.csv "trace-rodinia-3.1-$NAME.csv"


./util/job_launching/run_simulations.py \
    -B parboil:parboil-sgemm:0 \
    -C A100-SASS \
    -T ./hw_run/parboil/11.0 \
    -N parboil-$NAME

./util/job_launching/monitor_func_test.py \
    -N parboil-$NAME -v

./util/job_launching/get_stats.py -N parboil-$NAME | tee stats-parboil-$NAME.csv

mv trace.csv "trace-parboil-$NAME.csv"


./util/job_launching/run_simulations.py \
    -B polybench:polybench-2DConvolution:0 \
    -C A100-SASS \
    -T ./hw_run/polybench/11.0/ \
    -N polybench-$NAME

./util/job_launching/monitor_func_test.py \
    -N polybench-$NAME -v

./util/job_launching/get_stats.py -N polybench-$NAME | tee stats-polybench-$NAME.csv

mv trace.csv "trace-polybench-$NAME.csv"


./util/job_launching/run_simulations.py \
    -B rodinia_2.0-ft \
    -C A100-SASS \
    -T ./hw_run/rodinia_2.0-ft/9.1 \
    -N rodinia_2.0-ft-$NAME

./util/job_launching/monitor_func_test.py \
    -N rodinia_2.0-ft-$NAME -v

./util/job_launching/get_stats.py -N rodinia_2.0-ft-$NAME | tee stats-rodinia_2.0-ft-$NAME.csv

mv trace.csv "trace-rodinia_2.0-ft-$NAME.csv"

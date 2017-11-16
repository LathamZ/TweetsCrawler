#! /bin/bash

exit_f() {
    ./summary.sh stop
    exit
}

stop_cur_cand() {
    ./crawl.sh $CAND stop
    echo `date` Stop crawl $CAND >> $LOG_FILE
}

trap exit_f SIGINT
trap stop_cur_cand SIGINT
trap exit_f SIGKILL
trap stop_cur_cand SIGKILL

CANDS=`cat ./candidates`
LOG_FILE=rotate_crawl.log
./summary.sh start
while true
do
    for CAND in $CANDS; do
        echo `date` Start crawl $CAND >> $LOG_FILE
        ./crawl.sh $CAND start
        sleep 1800 # 30 mins per candidate
        ./crawl.sh $CAND stop
        echo `date` Finish crawl $CAND >> $LOG_FILE
    done
done

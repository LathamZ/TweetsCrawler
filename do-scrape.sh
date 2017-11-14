#! /bin/bash
HOME=/Users/lathamz/Development/tweets_crawler
ENV=/Users/lathamz/ENV

stop_f() {
    ./stop-all.sh
    echo
    cat last_summary.log
    deactivate
    echo Stop at `date`
    exit
}

unexpect_stop_f() {
    echo
    echo
    echo !!!Stop unexpectedly...
    echo
    sleep 1
    stop_f
}

start_f() {
    source $ENV/bin/activate
    cd $HOME
    echo Start at `date`
    ./start-all.sh
}

wait_f() {
    echo ===================
    counter=1
    while [ $counter -le 6 ]
    do
        sleep 300 # 5mins
        alives=`ps -ef | grep spider | grep -v grep | wc -l`
        echo `expr $counter \* 5` mins elapsed, \
            Alive  count $alives
        ((counter++))
    done
    echo ===================
}

trap unexpect_stop_f SIGINT

start_f
wait_f
stop_f



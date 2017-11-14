#! /bin/bash
BIN=$(cd $(dirname ${0})>/dev/null;pwd)
ACTION=$1

cd $BIN

if [[ $ACTION == "start" ]]; then
    echo Start summary
    nohup python summary.py > logs/summary_nohup.log 2>&1 & 
    echo $! > $BIN/pids/summary.pid
else
	if [[ -f $BIN/pids/summary.pid ]]; then
        echo Stop summary
    	pid=`cat $BIN/pids/summary.pid`
    	kill -9 $pid
    	rm -f $BIN/pids/summary.pid
	fi
fi

#! /bin/bash

BIN=$(cd $(dirname ${0})>/dev/null;pwd)
cd $BIN

ACTION=$1
ID=rotate

if [[ $ACTION == "start" ]]; then
    echo Start $ID
    nohup ./single-rotate-start.sh > logs/${ID}.log 2>&1 &
    echo $! > $BIN/pids/${ID}.pid
else
	if [[ -f $BIN/pids/${ID}.pid ]]; then
        echo Stop $ID
    	pid=`cat $BIN/pids/${ID}.pid`
    	kill -9 $pid
    	rm -f $BIN/pids/${ID}.pid
        echo Stop all spiders
        pkill -f spider.py
        echo spiders: `ps -ef | grep spider.py | grep -v grep | wc -l`
        echo done
	fi
fi

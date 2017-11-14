#! /bin/bash

BIN=$(cd $(dirname ${0})>/dev/null;pwd)
ID=$1
ACTION=$2

cd $BIN

if [ ! -d "pids" ]; then
    mkdir pids
fi

if [ ! -d "logs" ]; then
    mkdir logs
fi

if [[ $ACTION == "start" ]]; then
    echo Start crawling $ID
    nohup python spider.py $ID > logs/${ID}_nohup.log 2>&1 & 
    echo $! > $BIN/pids/${ID}.pid
else
	if [[ -f $BIN/pids/${ID}.pid ]]; then
        echo Stop crawling $ID
    	pid=`cat $BIN/pids/${ID}.pid`
    	kill -9 $pid
    	rm -f $BIN/pids/${ID}.pid
	fi
fi





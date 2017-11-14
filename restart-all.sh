echo Restarting...
echo ===
./stop-all.sh

TMP=tmpfile
for LOG_FILE in `ls *.log`; do
    tail -n 100 $LOG_FILE > $TMP
    cat $TMP > $LOG_FILE
done
rm -f $TMP

echo ===
./start-all.sh

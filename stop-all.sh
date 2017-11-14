CANDS=`cat ./candidates`
for CAND in $CANDS; do
   ./crawl.sh $CAND stop
done

echo
./summary.sh start
sleep 0.5
echo ...
sleep 0.5
echo ...
sleep 0.5
./summary.sh stop
sleep 0.5

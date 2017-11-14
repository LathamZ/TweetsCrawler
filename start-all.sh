CANDS=`cat ./candidates`
for CAND in $CANDS; do
    ./crawl.sh $CAND start
done

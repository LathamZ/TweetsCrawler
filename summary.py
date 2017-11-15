import logging
import time
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))
from tweets_crawler import db as DB

def doSummary(candidates):
	while True:
		msg = "\nSummary:\n"
		db = DB.DB()
		total = 0
		for cand in candidates:
                        cand = cand.strip()
                        if cand == "": continue
                        pattern = cand.strip() + "*"
                        count = db.count(pattern)
                        total += count
                        msg += "\t Tweets of " + cand + ": " + str(count) + "\n"
                msg += "\t===================================\n"
		msg += "\t Total: " + str(total) + "\n"
		logging.info(msg)
                with open('last_summary.log', 'w') as f:
                    f.write(msg)
		time.sleep(60*30)




if __name__ == "__main__":
    log_format = "%(asctime)s - %(message)s"
    logging.basicConfig(filename = 'summary.log',level=logging.INFO, format = log_format)

    candidates = None
    with open('candidates') as f:
    	candidates = f.readlines()

    doSummary(candidates)

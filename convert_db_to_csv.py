
import sqlite3
import code
import datetime
import csv
import matplotlib.pyplot as mpl

conn = sqlite3.connect('odds.db', detect_types=sqlite3.PARSE_DECLTYPES)
c = conn.cursor()
with open('odds.csv', 'wb') as f:
  writer = csv.writer(f)
  writer.writerow(['timestamp', 'event_id', 'event_name', 'market_id', 'market_name', 'runner_id', 'runner_name', 'type', 'size', 'price'])
  writer.writerows(c.execute('SELECT * FROM odds'))
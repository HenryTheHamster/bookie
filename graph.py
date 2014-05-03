import sqlite3
import code
import datetime
import matplotlib.pyplot as mpl

conn = sqlite3.connect('odds.db', detect_types=sqlite3.PARSE_DECLTYPES)
c = conn.cursor()
t = ('RHAT',)
# c.execute('SELECT * FROM odds WHERE symbol=?', t)


c.execute('SELECT * FROM odds')
rows = c.fetchall()
# # for r in c.fetchall()
# for row in c.execute('SELECT * FROM odds'):
#   data[event_id][market_id][runner_id][type] << (timestamp, prices
# code.interact(local=locals())
def plot(event_id, market_id, runner_id, type):
  x = []
  y = []
  if type == 'BACK':
    for row in c.execute('SELECT timestamp AS "[timestamp]", MAX(price) FROM odds WHERE event_id=? AND market_id=? AND runner_id=? AND type=? GROUP BY timestamp', (event_id, market_id, runner_id, type)):
      x.append(datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'))
      y.append(row[1])
  else:
    for row in c.execute('SELECT timestamp AS "[timestamp]", MIN(price) FROM odds WHERE event_id=? AND market_id=? AND runner_id=? AND type=? GROUP BY timestamp', (event_id, market_id, runner_id, type)):
      x.append(datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'))
      y.append(row[1])
  mpl.plot(x, y)
  # code.interact(local=locals())


plot(27182868, 2.100938811, 39987, 'BACK')
mpl.show()


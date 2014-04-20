
#!/usr/bin/env python
 
import requests
import json
import code
import os
import sys
import sqlite3
import time
import datetime

app_key = "o8xGmCwZ4GuHjoWa"

endpoint = "https://api-au.betfair.com/exchange/betting/rest/v1.0"




def betfair(command, paramaters, headers):
  url = endpoint + "/" + command + "/"
  response = requests.post(url, data=json.dumps(paramaters), headers=headers)
  return json.loads(response.text)


catalog_filter = {'filter': {'eventTypeIds': [61420], #AFL, Politics
                             'marketTypeCodes': []}}




login = requests.post('https://identitysso.betfair.com/api/certlogin', data='username=sharkishki&password=ila2530rsmV', cert=("#{Dir.pwd}/client-2048.crt", "#{Dir.pwd}/client-2048.key"), headers={'X-Application': app_key, 'Content-Type': 'application/x-www-form-urlencoded'})
if login.status_code == 200:

  conn = sqlite3.connect('odds.db')

  sql = conn.cursor()

  # Create table
  sql.execute('''CREATE TABLE IF NOT EXISTS odds (timestamp text, event_id integer, event_tame text, market_id integer, market_name text, runner_id integer, runner_name text, type text, size real, price real )''')


  resp_json = login.json()

  

  session_token = resp_json['sessionToken']

  headers = { 'X-Application' : app_key, 'X-Authentication' : session_token ,'content-type' : 'application/json' }

  catalogs = betfair('listMarketCatalogue', {'filter': {'eventTypeIds': [61420], 'marketTypeCodes': ['MATCH_ODDS'] }, 'maxResults': 1000, 'marketProjection': ['EVENT', 'RUNNER_DESCRIPTION']}, headers ) + betfair('listMarketCatalogue', {'filter': {'textQuery': 'australian','eventTypeIds': [2378961] }, 'maxResults': 1000, 'marketProjection': ['EVENT', 'RUNNER_DESCRIPTION']}, headers )
  books = betfair('listMarketBook', {'marketIds': [c['marketId'] for c in catalogs], 'priceProjection': {'priceData': ['EX_BEST_OFFERS']} }, headers )

  runner_ids = {r[0]['selectionId']:r[0]['runnerName'] for r in [c['runners'] for c in catalogs]}

  # code.interact(local=locals())   
  markets = {c['marketId']:c['marketName'] for c in catalogs}
  events = {c['event']['id']:c['event']['name'] for c in catalogs}
  event_ids = {c['marketId']:c['event']['id'] for c in catalogs}
  # runners = {c['runners'][:c['marketName'] for c in catalogs}
  runners = {}
  for c in catalogs: runners.update({r['selectionId']:r['runnerName'] for r in c['runners']})
  timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
  for b in books:
    for r in b['runners']:
      
      event_id = event_ids[b['marketId']]
      event_name = events[event_id]
      market_id = b['marketId']
      market_name = markets[market_id]
      runner_id = r['selectionId']
      runner_name = runners[runner_id]
      for p in r['ex']['availableToBack']:
        sql.execute("INSERT INTO odds VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (timestamp, event_id, event_name, market_id, market_name, runner_id, runner_name, 'BACK', p['size'], p['price']))
        conn.commit()
      for p in r['ex']['availableToLay']:
        sql.execute("INSERT INTO odds VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (timestamp, event_id, event_name, market_id, market_name, runner_id, runner_name, 'LAY', p['size'], p['price']))
        conn.commit()
      
  
  



  conn.close()
  logout = requests.post('https://identitysso.betfair.com/api/logout', headers={'X-Application': app_key, 'X-Authentication':session_token, 'Content-Type': 'application/json'})



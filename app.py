
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


catalog_filter = {'filter': {'eventTypeIds': [61420], #AFL
                             'marketTypeCodes': []}}

 
login = requests.post('https://identitysso.betfair.com/api/certlogin', data='username=sharkishki&password=ila2530rsmV', cert=('client-2048.crt', 'client-2048.key'), headers={'X-Application': app_key, 'Content-Type': 'application/x-www-form-urlencoded'})
if login.status_code == 200:

  conn = sqlite3.connect('odds.db')

  sql = conn.cursor()

  # Create table
  sql.execute('''CREATE TABLE IF NOT EXISTS odds (date text, data text)''')


  resp_json = login.json()



  session_token = resp_json['sessionToken']

  headers = { 'X-Application' : app_key, 'X-Authentication' : session_token ,'content-type' : 'application/json' }

  catalogs = betfair('listMarketCatalogue', {'filter': {'eventTypeIds': [61420], 'marketTypeCodes': ['MATCH_ODDS'] }, 'maxResults': 1000, 'marketProjection': ['EVENT', 'RUNNER_DESCRIPTION']}, headers )
  books = betfair('listMarketBook', {'marketIds': [c['marketId'] for c in catalogs], 'priceProjection': {'priceData': ['EX_BEST_OFFERS']} }, headers )

  runnerIds = {r[0]['selectionId']:r[0]['runnerName'] for r in [c['runners'] for c in catalogs]}

  # code.interact(local=locals())   
  events = {c['event']['id']:c['event']['name'] for c in catalogs}
  event_ids = {c['marketId']:c['event']['id'] for c in catalogs}
  # runners = {c['runners'][:c['marketName'] for c in catalogs}
  runners = {}
  for c in catalogs: runners.update({r['selectionId']:r['runnerName'] for r in c['runners']})
  
  data = {c['event']['id']:{'name':c['event']['name'], 'match_odds':{}} for c in catalogs}

  for b in books:
    for r in b['runners']:
      data[event_ids[b['marketId']]]['match_odds'][runners[r['selectionId']]] = {'available_to_back':{'price': r['ex']['availableToBack'][0]['price'], 'size': r['ex']['availableToBack'][0]['size']}, 'available_to_lay':{'price': r['ex']['availableToLay'][0]['price'], 'size': r['ex']['availableToLay'][0]['size']}}

  sql.execute("INSERT INTO odds VALUES (?,?)", (datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), json.dumps(data)))
  conn.commit()
  conn.close()
  logout = requests.post('https://identitysso.betfair.com/api/logout', headers={'X-Application': app_key, 'X-Authentication':session_token, 'Content-Type': 'application/json'})



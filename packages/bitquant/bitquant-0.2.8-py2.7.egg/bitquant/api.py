import sql
import tools

import json
import numpy as np
from pandas.io.json import json_normalize
from pandas import DataFrame, to_datetime
from urllib import urlopen

#|Request class for exchange API data
class request(object):

	def __init__(self, exchange, symbol, limit='', since='', typ='trades'):
		self.values = {'exchange':exchange, 'symbol':symbol,
			       'limit':limit, 'since':since, 'typ':typ}		
		self.cmd = self.commands()[exchange][symbol]
		self.stmt = ''

	#|GET API request and return DataFrame
	def get(self):
		if self.stmt == '':
			self.build_stmt()
		response = urlopen(self.stmt)
		response = json.load(response)
		if self.values['typ'] == 'quandl':
			df = self.df_quandl(response)
		else: 
			df = self.df_trades(response)
		df = tools.standard_columns(df)
		if 'exchange' not in df:
			df['exchange'] = self.values['exchange']
		if 'symbol' not in df:
			df['symbol'] = self.values['symbol']
		return df

	#|Get data and insert into SQL database
	def to_sql(self):
		df = self.get()
		if self.values['typ'] == 'trades':
			sql.df_to_sql(df, 'trades')
		else:
			sql.df_to_sql(df, 'price')
		return df
	
	#|Build statement for API request
	def build_stmt(self):
		self.stmt = ''		
		if self.values['typ'] == 'trades':
			self.stmt += self.cmd['url']
			self.stmt += str('/') + self.cmd['trades']
			if 'market' in self.cmd.keys():
				self.values['market'] = ''
				self.add_parameter('market')
			if self.values['limit'] <> '' and 'limit' in self.cmd.keys():
				self.add_parameter('limit')
			if self.values['since'] <> '' and 'since' in self.cmd.keys():
				self.add_parameter('since')
		if self.values['typ'] == 'quandl' and 'quandl' in self.cmd.keys():
			self.stmt += 'https://www.quandl.com/api/v1/datasets/%s.json'\
					% self.cmd['quandl']

	#|Add a parameter to the API request statement
	def add_parameter(self, parameter):
		if self.stmt.find('?') == -1:
			self.stmt += str('?') + self.cmd[parameter] + str(self.values[parameter])
		else:
			self.stmt += str('&') + self.cmd[parameter] + str(self.values[parameter])
		
	#|Individual command dictionary for exchange/symbols
	def commands(self):

		cmd = {'bitfinex':{'btcusd':{'url':'https://api.bitfinex.com/v1',
			   		     'trades':'trades/btcusd','limit':'limit_trades=',
					     'quandl':'BCHARTS/BITFINEXUSD','bchart':'bitfinexUSD'},
				   'ltcusd':{'url':'https://api.bitfinex.com/v1',
					     'trades':'trades/ltcusd','limit':'limit_trades='}},
		       'bitstamp':{'btcusd':{'url':'https://www.bitstamp.net/api',
					     'trades':'transactions','quandl':'BCHARTS/BITSTAMPUSD',
					     'bchart':'bitstampUSD'}},
		       'coinbase':{'btcusd':{'url':'https://api.exchange.coinbase.com',
					     'trades':'products/BTC-USD/trades','limit':'limit=',
					     'since':'after='}},
		       'btce':{'btcusd':{'url':'https://btc-e.com/api/3',
					 'trades':'trades/btc_usd','limit':'limit=',
					 'quandl':'BCHARTS/BTCEUSD','bchart':'btceUSD'},
			       'ltcusd':{'url':'https://btc-e.com/api/3',
					 'trades':'trades/ltc_usd','limit':'limit='}},
		       'btcchina':{'btccny':{'url':'https://data.btcchina.com',
					     'trades':'data/historydata','limit':'limit=',
					     'since':'since=','market':'market=btccny',
					     'bchart':'btcnCNY'},
				   'ltccny':{'url':'https://data.btcchina.com',
					     'trades':'data/historydata','limit':'limit=',
					     'since':'since=','market':'market=ltccny'}},
		       'okcoin':{'btcusd':{'url':'https://www.okcoin.com/api/v1',
					   'trades':'trades.do','since':'since=',
			    		   'market':'symbol=btc_usd'},
				 'ltcusd':{'url':'https://www.okcoin.com/api/v1',
					   'trades':'trades.do','since':'since=',
			    		   'market':'symbol=ltc_usd'},
				 'btccny':{'url':'https://www.okcoin.cn/api/v1',
					   'trades':'trades.do','since':'since=',
			    		   'market':'symbol=btc_cny'},
				 'ltccny':{'url':'https://www.okcoin.cn/api/v1',
					   'trades':'trades.do','since':'since=',
			    		   'market':'symbol=ltc_cny'}}}
					    
		return cmd

	#|Convert Quandl API response to DataFrame
	def df_quandl(self, response):
		data = response['data']
		headers = response['column_names']
		df = DataFrame(data, columns=headers)
		df['timestamp'] = df['Date'].apply(tools.dateconv)
		df['freq'] = 'd'
		df['source'] = 'quandl'
		df = tools.date_index(df.drop('Date', axis=1))
		return df

	#|Convert Exchange API response to DataFrame
	def df_trades(self, response):
		if self.values['exchange'] == 'btce':
			for col in response:
				response = response[col]
		df = json_normalize(response)
		if self.values['exchange'] == 'coinbase':
			df['time'] = to_datetime(df['time'], utc=0)
			df['timestamp'] = df['time'].astype(np.int64) // 10**9
		return df


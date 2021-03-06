import re
import json
import requests
from jsonrpc import ServiceProxy
import whattomine
import config
import constant


#Compute net worth using exchange info
exchange=whattomine.exchange();
exchange.load('config/exchange.json');
exchange.update();


btc_usd=0;
try:
	coindesk_request=requests.get("http://api.coindesk.com/v1/bpi/currentprice.json",timeout=5);
	coindesk_btc=json.loads(coindesk_request.content);
	btc_usd=coindesk_btc['bpi']['USD']['rate_float'];
except:
	print('failed to get btc price');

total_sent_btc=0;
print('Sending to exchange');
for port in config.scan_ports:
	access=ServiceProxy({'url':config.scan_api%port,'username':config.wallet_username,'password':config.wallet_password},timeout=5);
	try:
		info=access.help();
		for coin in constant.wallets_key:
			if info.find(constant.wallets_key[coin])>0:
				if coin in config.exchange_addr:
					d=0.00;
					done_sending=False;
					v=access.getbalance();
					while not(done_sending) and v-d>0:
						try:
							access.sendfrom('',config.exchange_addr[coin],v-d);
							done_sending=True;
						except:
							d=d*1.5+0.01;
					
					if v>0:
							if not(coin in constant.multi_algo_coins):
								print('%s: sent %f'%(coin,v-d));
								total_sent_btc=total_sent_btc+(v-d)*exchange.tickers[coin];
								break;
							else:
								info2=access.getinfo();
								print('%s-%s: sent %f'%(coin,info2['pow_algo'],v-d));
								total_sent_btc=total_sent_btc+(v-d)*exchange.tickers[coin];
								break;
					else:
						if not (coin in constant.multi_algo_coins):
							print('%s: not enough balance %f'%(coin,v));
						else:
							print('%s: not enough balance %f'%(coin,info2['pow_algo'],v))
				else:
					print('%s: missing exchange address'%(coin));
		
	except:
		pass;

print('Total sent:\t\t%f BTC'%total_sent_btc);
print('\t\t\t%f USD'%(total_sent_btc*btc_usd));

# wotwrapper
# A module for connecting to the Wot operating environment

import re
import websocket
import time
import requests
import thread
import json

def connect(path, objectToWrap, sendDataFunction, delay):
	def onMessage(message, send):
		print message
		try:
			msg = json.loads(message)
		except:
			print "Error: Not JSON: {0}".format(message)
			return
		if hasattr(objectToWrap, msg[1]):
			try:
				methodToCall = getattr(objectToWrap, msg[1])
				resp = methodToCall(*msg[2:])
				send(resp)
			except:
				print "Error with message:".format(msg)
	wot = Wot.connect(path, onMessage)
	thread.start_new_thread(wot.subscribe, ())
	time.sleep(2)
	while True:
		wot.publish(sendDataFunction())
		time.sleep(delay)


class Wot(object):
	def connect(path, callback):

		class WotHTTP(Wot):
			def __init__(self, path, callback):
				super(WotHTTP, self).__init__(path, callback)
				self.getpath = "http://{0}/{1}/{2}/{3}/{4}".format(self.parts['host'], self.parts['vhost'], self.parts['in_exchange'], self.parts['in_key'], self.parts['in_queue'])
				self.putpath = "http://{0}/{1}/{2}/{3}".format(self.parts['host'], self.parts['vhost'], self.parts['out_exchange'], self.parts['out_key'])
				x=requests.post(self.getpath, headers={'Authorization': "Bearer {0}".format(self.parts['token'])})
			def subscribe(self):
				time.sleep(2)
				while True:
					x = requests.get(self.getpath, headers={'Authorization': "Bearer {0}".format(self.parts['token'])}).text
					if x != '': self.on_message(self, x)
					time.sleep(1)
			def publish(self, message):
				requests.put(self.putpath, data=json.dumps(message), headers={'Authorization': "Bearer {0}".format(self.parts['token'])})

		class WotWS(Wot):
			def __init__(self, path, callback):
				super(WotWS, self).__init__(path, callback)
				#websocket.enableTrace(True)
				self.ws = websocket.WebSocketApp(self.path, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)
				#ws.on_open = self.on_open
			def subscribe(self):
				self.ws.run_forever()
			def publish(self, message):
				self.ws.send(json.dumps(message))

		## Add New Protocol Classes Here ##

		if re.match('http', path): return WotHTTP(path, callback)
		if re.match('ws', path): return WotWS(path, callback)
		assert 0, "Invalid Wot path: " + path

	connect = staticmethod(connect)

	def __init__(self, path, callback):
		self.callback = callback
		self.path = path
		parts = re.match('(http|ws):\/\/([^\/]+)\/([^\/]+)\/([^\/]+)\/([^\/]+)\/([^\/]+)\/([^\/]+)\/([^\/]+)\/([^\/]+)',path)
		self.parts = {
			'host': parts.group(2),
			'vhost': parts.group(3),
			'in_exchange': parts.group(4),
			'in_key': parts.group(5),
			'in_queue': parts.group(6),
			'out_exchange': parts.group(7),
			'out_key': parts.group(8),
			'token': parts.group(9)
		}
	def on_message(self, connection, message):
		self.callback(message, self.publish)
	def publish(self, message): pass
	def on_error(self): pass
	def on_close(self, foo): pass

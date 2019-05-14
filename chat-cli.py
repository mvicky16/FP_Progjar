import socket
import os
import json

TARGET_IP = "127.0.0.1"
TARGET_PORT = 8889

	
class ChatClient:
	def __init__(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_address = (TARGET_IP, TARGET_PORT)
		self.sock.connect(self.server_address)
		self.tokenid = ""

	def proses(self, cmdline):
		j = cmdline.split(" ")
		try:
			command = j[0].strip()
			if (command == 'auth'):
				username = j[1].strip()
				password = j[2].strip()
				return self.login(username, password)
			elif (command == 'send'):
				usernameto = j[1].strip()
				message = ""
				for w in j[2:]:
					message = "{} {}" . format(message, w)
				return self.sendmessage(usernameto, message)
			elif (command == 'inbox'):
				return self.inbox()
			elif (command == 'logout'):
				return self.logout()
			elif (command == 'menu'):
				print '************************ Menu ************************'
				print '*  action   		   | command  		     *'
				print '*==========================|=========================*'
				print '*  Login     		   |  auth username password *'
				print '*  Logout  		   |  logout  		     *'
				print '*  Send personal message   |  send username message  *'
				print '*  Send personal img/file  |  send username filename *'
				print '*  Open inbox  		   |  inbox  	             *'
				print '*  Send group message      |  sendgroup message      *'
				print '*  Send group img/file     |  sendgroup filename     *'
				print '******************************************************'
			else:
				return "*Command not found, type `menu` to see all commands"
		except IndexError:
			return "*Command format wrong, type `menu` to see all commands"

	def sendstring(self, string):
		try:
			self.sock.sendall(string)
			receivemsg = ""
			while True:
				data = self.sock.recv(10)
				if (data):
					receivemsg = "{}{}" . format(receivemsg, data)
					if receivemsg[-4:] == "\r\n\r\n":
						return json.loads(receivemsg)
		except:
			self.sock.close()

	def logout(self):
		if (self.tokenid == ""):
			return "Already logged out"
		string = "logout {} \r\n" . format(self.tokenid)
		result = self.sendstring(string)
		if result['status'] == 'OK':
			self.tokenid = ""
			return "Log out successful"
		else:
			return "Unexpected Error(?)"

	def login(self, username, password):
		if(self.tokenid != ""):
			return "You already logged in"
		string = "auth {} {} \r\n" . format(username, password)
		result = self.sendstring(string)
		if result['status'] == 'OK':
			self.tokenid = result['tokenid']
			return "username {} logged in, token {} " .format(username, self.tokenid)
		else:
			return "Error, {}" . format(result['message'])

	def sendmessage(self, usernameto="xxx", message="xxx"):
		if (self.tokenid == ""):
			return "Error, not authorized"
		string = "send {} {} {} \r\n" . format(
			self.tokenid, usernameto, message)
		result = self.sendstring(string)
		if result['status'] == 'OK':
			return "message sent to {}" . format(usernameto)
		else:
			return "Error, {}" . format(result['message'])

	def inbox(self):
		if (self.tokenid == ""):
			return "Error, not authorized"
		string = "inbox {} \r\n" . format(self.tokenid)
		result = self.sendstring(string)
		if result['status'] == 'OK':
			return "{}" . format(json.dumps(result['messages']))
		else:
			return "Error, {}" . format(result['message'])


if __name__ == "__main__":
	cc = ChatClient()
	while True:
		cmdline = raw_input("Command {}:" . format(cc.tokenid))
		print cc.proses(cmdline)

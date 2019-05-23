import sys
import os
import json
import uuid
import datetime
from Queue import *
import glob

class Chat:
	def __init__(self):
		self.groupid = 0
		self.sessions={}
		self.users = {}
		self.groups = {}
		self.users['messi'] = {'nama': 'Lionel Messi', 'negara': 'Argentina',
							   'password': 'surabaya', 'incoming': {}, 'outgoing': {}}
		self.users['henderson'] = {'nama': 'Jordan Henderson', 'negara': 'Inggris',
								   'password': 'surabaya', 'incoming': {}, 'outgoing': {}}
		self.users['lineker'] = {'nama': 'Gary Lineker', 'negara': 'Inggris',
								 'password': 'surabaya', 'incoming': {}, 'outgoing': {}}

	def proses(self, data, connection):
		j=data.strip().split(" ")

		try:
			command=j[0]
			if (command=='auth'):
				username=j[1]
				password=j[2]
				print "auth {}" . format(username)
				return self.auth(username,password)

			elif (command=='send'):
				sessionid = j[1]
				usernameto = j[2]
				message=""
				for w in j[3:]:
					message="{} {}" . format(message,w)
				usernamefrom = self.sessions[sessionid]['username']
				print "send message from {} to {}" . format(usernamefrom,usernameto)
				return self.send_message(sessionid,usernamefrom,usernameto,message)

			elif (command=='inbox'):
				sessionid = j[1]
				username = self.sessions[sessionid]['username']
				print "{} {}" . format(command, username)
				return self.get_inbox(username)

			elif (command=='logout'):
				sessionid = j[1]
				username = self.sessions[sessionid]['username']
				print "{} {}" . format(command, username)
				return self.logout(sessionid)

			elif (command=='create_group'):
				sessionid = j[1]
				group_name = j[2]
				print "{} {}" . format(command, group_name)
				return self.create_group(group_name, sessionid)

			elif (command=='join_group'):
				sessionid = j[1]
				group_name = j[2]
				print "{} {}" . format(command, group_name)
				return self.join_group(group_name, sessionid)

			elif (command=='list_group'):
				sessionid = j[1]
				group_name = j[2]
				print "{} {}" . format(command, group_name)
				return self.list_group_user(group_name, sessionid)

			elif (command=='leave_group'):
				sessionid = j[1]
				group_name = j[2]
				print "{} {}" . format(command, group_name)
				return self.leave_group(group_name, sessionid)

			elif (command == 'inbox_group'):
				sessionid = j[1]
				group_name = j[2]
				print "{} {}" . format(command, group_name)
				return self.inbox_group(group_name, sessionid)

			elif (command == 'send_group'):
				sessionid = j[1]
				group_name = j[2]
				message = ""
				for w in j[3:]:
					message="{} {}" . format(message,w)
				print "{} {} {}" . format(command, group_name, message)
				return self.send_group(group_name, sessionid, message)

			elif (command=='send_file'):
				sessionid = j[1]
				usernameto = j[2]
				filename = j[3]
				usernamefrom = self.sessions[sessionid]['username']
				print "send_file from {} to {}" . format(usernamefrom, usernameto)
				return self.send_file(sessionid, usernamefrom, usernameto, filename, connection)

			else:
				return {'status': 'ERROR', 'message': 'Protokol tidak ditemukan'}

		except IndexError:
			return {'status': 'ERROR', 'message': 'IndexError on Protokol'}

	def auth(self,username,password):
		if (username not in self.users):
			return { 'status': 'ERROR', 'message': 'User tidak ada' }
 		if (self.users[username]['password']!= password):
			return { 'status': 'ERROR', 'message': 'Password salah' }
		tokenid = str(uuid.uuid4())
		self.sessions[tokenid]={ 'username': username, 'userdetail':self.users[username]}
		return { 'status': 'OK', 'tokenid': tokenid }

	def get_user(self,username):
		if (username not in self.users):
			return False
		return self.users[username]

	def send_message(self,sessionid,sender,receiver,message):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session tidak ditemukan'}
		index_sender = self.get_user(sender)
		index_receiver = self.get_user(receiver)

		if (index_sender==False or index_receiver==False):
			return {'status': 'ERROR', 'message': 'User tidak ditemukan'}

		message = { 'msg_from': index_sender['nama'], 'msg_to': index_receiver['nama'], 'msg': message }
		outqueue_sender = index_sender['outgoing']
		inqueue_receiver = index_receiver['incoming']
		try:
			outqueue_sender[sender].put(message)
		except KeyError:
			outqueue_sender[sender]=Queue()
			outqueue_sender[sender].put(message)
		try:
			inqueue_receiver[sender].put(message)
		except KeyError:
			inqueue_receiver[sender]=Queue()
			inqueue_receiver[sender].put(message)
		return {'status': 'OK', 'message': 'Pesan terkirim'}

	def get_inbox(self,username):
		index_sender = self.get_user(username)
		incoming = index_sender['incoming']
		messages={}
		for users in incoming:
			messages[users]=[]
			while not incoming[users].empty():
				messages[users].append(index_sender['incoming'][users].get_nowait())

		return {'status': 'OK', 'messages': messages}

	def logout(self,tokenid):
		self.sessions[tokenid]=None
		return { 'status': 'OK', 'message': 'Berhasil logout' }

	def create_group(self,group_name,sessionid):
		while(True):
			if group_name not in self.groups:
				break
		index_admin = self.sessions[sessionid]['username']
		self.groups[group_name] = {'group_name':group_name, 'users':[]}
		self.groups[group_name]['users'].append(index_admin)
		return {'status':'OK', 'messages': self.groups[group_name]}

	def join_group(self,group_name,sessionid):
		username = self.sessions[sessionid]['username']
		if(group_name not in self.groups):
			return {'status':'Err', 'message':'Group tidak ditemukan'}

		if username not in self.groups[group_name]['users']:
			self.groups[group_name]['users'].append(username)
			return {'status':'OK', 'message':'Berhasil masuk group'}

		return {'status':'Err', 'message':'Anda sudah menjadi anggota'}

	def list_group_user(self,group_name,sessionid):
		if (group_name not in self.groups):
			return {'status':'Err', 'message':'Group tidak ditemukan'}

		username = self.sessions[sessionid]['username']
		if username not in self.groups[group_name]['users']:
			return {'status':'Err', 'message':'Bukan anggota grup'}

		return {'status':'OK', 'message':self.groups[group_name]['users']}

	def leave_group(self,group_name,sessionid):
		index_sender = self.sessions[sessionid]['username']
		if(group_name not in self.groups):
			return {'status':'Err', 'message':'Group tidak ditemukan'}

		if index_sender in self.groups[group_name]['users']:
			self.groups[group_name]['users'].remove(index_sender)
			return {'status':'OK', 'message':'Anda keluar group [{}]' . format(group_name)}

		return {'status':'Err', 'message':'Anda bukan anggota group'}

	def inbox_group(self,group_name,sessionid):
		if (group_name not in self.groups):
			return {'status':'Err', 'message':'Group tidak ditemukan'}

		username = self.sessions[sessionid]['username']
		if username not in self.groups[group_name]['users']:
			return {'status':'Err', 'message':'Bukan anggota grup'}

		return {'status':'OK', 'message':self.groups[group_name]['incoming']}

	def send_group(self, group_name, sessionid, message):
		if(group_name not in self.groups):
			return {'status':'Err', 'message':'Group tidak ditemukan'}

		username = self.sessions[sessionid]['username']
		if username not in self.groups[group_name]['users']:
			return {'status':'Err', 'message':'Bukan anggota grup'}

		now = datetime.datetime.now()
		try:
			self.groups[group_name]['incoming'].append({'from':username, 'message':message, 'created_at':now.strftime("%H:%M")})
		except:
			return {'status':'Err', 'message':'Tidak bisa mengirim ke group'}

		return {'status':'OK', 'message':'Pesan terkirim ke group'}

	def send_file(self, sessionid, username_from, username_dest, filename, connection):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		s_fr = self.get_user(username_from)
		s_to = self.get_user(username_dest)

		if (s_fr==False or s_to==False):
			return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

		try:
			if not os.path.exists(username_dest):
				os.makedirs(username_dest)
				print "dir created"
			with open(os.path.join(username_dest, filename), 'wb') as file:
				while True:
					data = connection.recv(1024)
					print data
					if(data[-4:] == 'DONE'):
						data = data[:-4]
						file.write(data)
						break
					file.write(data)
				file.close()
		except IOError:
			raise

		message = { 'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': 'sent/received {}' . format(filename) }
		outqueue_sender = s_fr['outgoing']
		inqueue_receiver = s_to['incoming']
		try:
			outqueue_sender[username_from].put(message)
		except KeyError:
			outqueue_sender[username_from]=Queue()
			outqueue_sender[username_from].put(message)
		try:
			inqueue_receiver[username_from].put(message)
		except KeyError:
			inqueue_receiver[username_from]=Queue()
			inqueue_receiver[username_from].put(message)

		return {'status': 'OK', 'message': 'File sent'}

	def download_file(self, sessionid, filename, connection):
		username = self.sessions[sessionid]['username']
		print "{} download {}" . format(username, filename)

		try:
			file = open(os.path.join(username, filename), 'rb')
		except IOError:
			return {'status': 'Err', 'message': 'File tidak ditemukan'}
			
		result = connection.sendall("OK")
		while True:
			data = file.read(1024)
			if not data:
				result = connection.sendall("DONE")
				break
			connection.sendall(data)
		file.close()
		return

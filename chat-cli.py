import socket
import os
import json
import datetime

TARGET_IP = "127.0.0.1"
TARGET_PORT = 8887

class ChatClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (TARGET_IP,TARGET_PORT)
        self.sock.connect(self.server_address)
        self.tokenid=""

    def proses(self,cmdline):
        j=cmdline.strip().split(" ")

        try:
            command=j[0]
            if (command=='auth'):
                username=j[1]
                password=j[2]
                return self.auth(username,password)

            elif (command=='logout'):
                return self.logout()

            elif (command=='send'):
                usernameto = j[1]
                message=""
                for w in j[2:]:
                    message="{} {}" . format(message,w)
                return self.sendmessage(usernameto,message)

            elif (command == 'send_file'):
                usernameto = j[2]
                filename = j[1]
                return self.send_file(usernameto, filename)

            elif (command=='inbox'):
                return self.inbox()

            elif (command == 'create_group'):
                group_name = j[1]
                return self.create_group(group_name)

            elif (command == 'inbox_group'):
                group_name = j[1]
                return self.inbox_group(group_name)

            elif (command == 'join_group'):
                group_name = j[1]
                return self.join_group(group_name)

            elif (command == 'leave_group'):
                group_name = j[1]
                return self.leave_group(group_name)

            elif (command == 'send_group'):
                group_name = j[1]
                message=""
                for w in j[2:]:
                    message="{} {}" . format(message, w)
                return self.send_group(group_name, message)

            elif (command == 'list_group'):
                group_name = j[1]
                return self.list_group(group_name)

            elif (command == 'menu'):
				print '*************************** Menu *****************************'
				print '*  action                    | command                       *'
				print '*============================|===============================*'
				print '*  Login                     |  auth username password       *'
				print '*  logout                    |  logout                       *'
				print '*  Send personal message     |  send username message        *'
				print '*  Send personal img/file    |  send_file username filename  *'
				print '*  Open inbox                |  inbox                        *'
				print '*  Create group              |  create_group groupname       *'
				print '*  Inbox group               |  inbox_group                  *'
				print '*  Join group                |  join_group groupname         *'
				print '*  Leave group               |  leave_group groupname        *'
				print '*  Send group message        |  send_group groupname message *'
				print '*  List group                |  list_group groupname         *'
				return'**************************************************************'

            else:
                return "*Command not found, type `menu` to see all commands"
        except IndexError:
            return "*Command format wrong, type `menu` to see all commands"
    def sendstring(self,string):
        try:
            self.sock.sendall(string)
            receivemsg = ""
            while True:
                data = self.sock.recv(10)
                if (data):
                    receivemsg = "{}{}" . format(receivemsg,data)
                    if receivemsg[-4:]=="\r\n\r\n":
                        return json.loads(receivemsg)
        except:
            self.sock.close()

    def auth(self,username,password):
        if(self.tokenid!=""):
            return "Error, authorized already"
        string="auth {} {} \r\n" . format(username,password)
        result = self.sendstring(string)

        if result['status']=='OK':
            self.tokenid=result['tokenid']
            return "username {} logged in, token {} " .format(username,self.tokenid)
        else:
            return "Error, {}" . format(result['message'])

    def logout(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string = "logout {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)

        if result['status']=='OK':
            self.tokenid = ""
            return "{}" . format(result['message'])
        else:
            return "Error, {}" . format(result['message'])

    def sendmessage(self,usernameto="xxx",message="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="send {} {} {} \r\n" . format(self.tokenid,usernameto,message)
        result = self.sendstring(string)

        if result['status']=='OK':
            return "message sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])

    def send_file(self, usernameto, filename):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="send_file {} {} {} \r\n" . format(self.tokenid, usernameto, filename)
        self.sock.sendall(string)

        try:
            with open(filename, 'rb') as file:
                while True:
                    bytes = file.read(1024)
                    if not bytes:
                        result = self.sendstring("DONE")
                        break
                    self.sock.sendall(bytes)
                file.close()
        except IOError:
            return "Error, file tidak ditemukan"

        if result['status']=='OK':
            return "file sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])

    def inbox(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inbox {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)

        if result['status']=='OK':
            return "{}" . format(json.dumps(result['messages']))
        else:
            return "Error, {}" . format(result['message'])

    def create_group(self,group_name):
        if (self.tokenid==""):
            return "Error, not authorized"
        string = "create_group {} {} \r\n" . format(self.tokenid,group_name)
        result = self.sendstring(string)

        if result['status']=='OK':
            return "{}" . format(result['messages'])
        else:
            return "Error, {}" . format(json.dumps(result['messages']))

    def join_group(self,group_name):
        if (self.tokenid==""):
            return "Error, not authorized"
        string = "join_group {} {} \r\n" . format(self.tokenid, group_name)
        result = self.sendstring(string)

        if result['status']=='OK':
            return "{}" . format(result['message'])
        else:
            return "Error, {}" . format(result['message'])

    def list_group(self,group_name):
        if (self.tokenid==""):
            return "Error, not authorized"
        string = "list_group {} {} \r\n" . format(self.tokenid, group_name)
        result = self.sendstring(string)

        if result['status']=='OK':
            return "{}" . format(json.dumps(result['message']))
        else:
            return "Error, {}" . format(result['message'])

    def leave_group(self, group_name):
        if (self.tokenid==""):
            return "Error, not authorized"
        string = "leave_group {} {} \r\n" . format(self.tokenid, group_name)
        result = self.sendstring(string)

        if result['status']=='OK':
            return "{}" . format(result['message'])
        else:
            return "Error, {}" . format(result['message'])

    def inbox_group(self, group_name):
        if (self.tokenid==""):
            return "Error, not authorized"
        string = "inbox_group {} {} \r\n" . format(self.tokenid, group_name)
        result = self.sendstring(string)

        if result['status']=='OK':
            return "{}" . format(json.dumps(result['message']))
        else:
            return "Error, {}" . format(result['message'])

    def send_group(self, group_name, message):
        if (self.tokenid==""):
            return "Error, not authorized"
        string = "send_group {} {} {} \r\n" . format(self.tokenid, group_name, message)
        result = self.sendstring(string)

        if result['status']=='OK':
            return "{}" . format(result['message'])
        else:
            return "Error, {}" . format(result['message'])

    
if __name__=="__main__":
    cc = ChatClient()
    while True:
        cmdline = raw_input("Command: ")
        print cc.proses(cmdline)

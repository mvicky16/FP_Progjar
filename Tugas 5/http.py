import sys
import os.path
import uuid
from glob import glob
from datetime import datetime

class HttpServer:
	def __init__(self):
		self.sessions={}
		self.types={}
		self.types['.pdf']='application/pdf'
		self.types['.jpg']='image/jpeg'
		self.types['.txt']='text/plain'
		self.types['.html']='text/html'
	
	def response(self,kode=404,message='Not Found',messagebody='',headers={}):
		tanggal = datetime.now().strftime('%c')
		resp=[]
		resp.append("HTTP/1.0 {} {}\r\n" . format(kode,message))
		resp.append("Date: {}\r\n" . format(tanggal))
		resp.append("Connection: close\r\n")
		resp.append("Server: myserver/1.0\r\n")
		resp.append("Content-Length: {}\r\n" . format(len(messagebody)))
		for kk in headers:
			resp.append("{}:{}\r\n" . format(kk,headers[kk]))
		resp.append("\r\n")
		resp.append("{}" . format(messagebody))
		response_str=''
		for i in resp:	
			response_str="{}{}" . format(response_str,i)
		return response_str

	def proses(self,data):
		
		requests = data.split("\r\n")
		baris = requests[0]

		print baris
		j = baris.split(" ")
		try:
			method=j[0].upper().strip()
			if (method=='GET'):
				object_address = j[1].strip()
				return self.http_get(object_address)
			elif (method=='HEAD'):
				object_address =  j[1].strip()
				return self.http_head(object_address)
			elif (method=='OPTIONS'):
				return self.http_options()
			elif (method=='POST'):
				return self.http_post()	
			else:
				return self.response(400,'Bad Request','',{})
		except IndexError:
			return self.response(400,'Bad Request','',{})

	def http_get(self,object_address):
		files = glob('./*')
		thedir='.'
		if thedir+object_address not in files:
			return self.response(404,'Not Found','',{})
		fp = open(thedir+object_address,'r')
		isi = fp.read()
		
		fext = os.path.splitext(thedir+object_address)[1]
		content_type = self.types[fext]
		
		headers={}
		headers['Content-type']=content_type
		
		return self.response(200,'OK',isi,headers)
		
	def http_options(self):
	  tanggal = datetime.now().strftime('%d/%m/%Y')

	  resp=[]
	  resp.append("HTTP/1.0 {} {}\r\n" . format(204, 'No Content'))
	  resp.append("Allow OPTIONS, GET, HEAD, POST\r\n")
	  resp.append("Cache-Control: max-age={}\r\n" . format(604800))
	  resp.append("Date: {}\r\n" . format(tanggal))
	  resp.append("Expires: {}\r\n" . format((datetime.now()+timedelta(days=7)).strftime('%d/%m/%Y')))
	  resp.append("Server: myserver/1.0\r\n")
	  
	  response_str=''
	  for i in resp: 
	   response_str="{}{}" . format(response_str,i)
	  return response_str	

	def http_head(self,object_address):
	  files = glob('./*')
	  thedir='.'
	  if thedir+object_address not in files:
	   return self.response(404,'Not Found','',{})
	  
	  fext = os.path.splitext(thedir+object_address)[1]
	  content_type = self.types[fext]
	  
	  headers={}
	  headers['Content-type']=content_type

	  isi = ''
	  
	  return self.response(200,'OK',isi,headers)

#>>> import os.path
#>>> ext = os.path.splitext('/ak/52.png')

if __name__=="__main__":
	httpserver = HttpServer()
	d = httpserver.proses('GET testing.txt HTTP/1.0')
	print d
        d = httpserver.http_get('/testing2.txt')
	print d
        d = httpserver.http_get('/testing.txt')
	print d
















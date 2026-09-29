#!/usr/bin/env python3
"""Check the current offline course using local Chrome/CDP; never invokes RTL tools."""
import subprocess,tempfile,time,json,socket,base64,os,struct,http.client,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
PAGES=json.loads((ROOT/'scripts/pages.json').read_text())
class CDP:
 def __init__(self,url):
  from urllib.parse import urlsplit
  u=urlsplit(url);self.s=socket.create_connection((u.hostname,u.port),timeout=15);self.n=0;self.events=[]
  key=base64.b64encode(os.urandom(16)).decode()
  self.s.sendall(f'GET {u.path} HTTP/1.1\r\nHost: {u.netloc}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n'.encode())
  b=b''
  while not b.endswith(b'\r\n\r\n'):b+=self.s.recv(1)
  assert b.startswith(b'HTTP/1.1 101'),b
 def take(self,n):
  b=b''
  while len(b)<n:
   x=self.s.recv(n-len(b))
   if not x:raise RuntimeError('closed')
   b+=x
  return b
 def recv(self):
  a,b=self.take(2);n=b&127
  if n==126:n=struct.unpack('!H',self.take(2))[0]
  elif n==127:n=struct.unpack('!Q',self.take(8))[0]
  if b&128:mask=self.take(4)
  data=self.take(n)
  if b&128:data=bytes(v^mask[i%4] for i,v in enumerate(data))
  return json.loads(data)
 def call(self,method,params={}):
  self.n+=1;p=json.dumps({'id':self.n,'method':method,'params':params}).encode();mask=os.urandom(4);n=len(p)
  h=bytes([129,128|n]) if n<126 else (bytes([129,254])+struct.pack('!H',n) if n<65536 else bytes([129,255])+struct.pack('!Q',n))
  self.s.sendall(h+mask+bytes(v^mask[i%4] for i,v in enumerate(p)))
  while True:
   r=self.recv()
   if r.get('id')==self.n:
    if 'error'in r:raise RuntimeError(r)
    return r.get('result',{})
   self.events.append(r)
 def js(self,s):
  r=self.call('Runtime.evaluate',{'expression':s,'returnByValue':True,'awaitPromise':True})
  if 'exceptionDetails'in r:raise RuntimeError(r)
  return r['result'].get('value')
 def shot(self,name):
  r=self.call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})
  (ROOT/'evidence'/('depth-20260929-'+name)).write_bytes(base64.b64decode(r['data']))

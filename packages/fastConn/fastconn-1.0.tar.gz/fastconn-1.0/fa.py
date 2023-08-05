#!/usr/bin/python
import socket
import time
import termios
import fcntl
import sys
import os
from termcolor import colored

def check_ipfile():
	homepath = os.environ['HOME']
	fa_ipfile = homepath + '/.fastconnip'
	file_check = open(fa_ipfile, 'a+')
	tar_ip = file_check.read()
	global target_ip
	if not tar_ip:		 
		target_ip = raw_input('Input the IP address of your server: ')
		file_check.write(target_ip)
	else:
		target_ip = tar_ip
	file_check.close()
		
#interrupt as soon as the user input something
def input_interrupt():
	from threading import Timer
	import threading
	import time
	import sys
	import select

	timer_interval = 0

	intra_event = threading.Event()
	intra_event.clear()

	def delayrun(event):
		event.set()    	

	def inputtimeout():
		i, o, e = select.select( [sys.stdin], [], [], 2 )
		if (i):
	  		return sys.stdin.readline().strip()
		else:
	  		return 0   

	t1 = Timer(timer_interval, delayrun, args = (intra_event,))

	t1.start()

	data = inputtimeout()
	if data:
		intra_event.set()
		t1.cancel()		
	
	else:
		intra_event.set()

	if intra_event.isSet():
		return data

onExit = 1
global target_ip
target_ip = ''
check_ipfile()
target_ip = str(target_ip)
c_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c_sock.connect((target_ip, 8000))
#c_sock.setblocking(0)
print 'Successfully connected to server!'
time.sleep(1)

greetings = c_sock.recv(1024)
print greetings
if greetings.startswith('Welcome to'):
    usr_name = raw_input('My user name: ')
    c_sock.send(usr_name)
    print c_sock.recv(1024)

#set the thread as non-blocking
c_sock.setblocking(0)
intent = ''
print 'Input a user name to start a talk, press q to quit, or do nothing to wait for touch: '

main_flag = 1

while main_flag:
	inbound = ''
	detect = ''
	outbound = ''
	inner_flag = 1
	while inner_flag:
		try:
			inbound = c_sock.recv(1024)
			inner_flag = 0
		except socket.error, e:
			detect = input_interrupt()
			if detect:
				inner_flag = 0

	if inbound:
		print colored(inbound, 'yellow')
	if detect:        
		outbound = detect
#    msg = inputTest(outbound)
	
	if outbound != 'q':
		c_sock.send(outbound)
	else:
		c_sock.send('killme')
		main_flag = 0



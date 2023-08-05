#!/usr/bin/python
import socket
import json
import threading
import os

usr_online = {}
threads = []
clients = {}
global aliveUsers 
aliveUsers = 0

#check if the target name is in dataset
def query(destName, dataLoad):
	for d_address in dataLoad.keys():
		if dataLoad[d_address] == destName:
			return d_address
	return 0

#check initial user file
def initcheck():
	init_json = '{\"\": \"\"}'
	homepath = os.environ['HOME']
	fa_usrs = homepath + '/fa_users'
	init_check = open(fa_usrs, 'a+')
	content = init_check.read()
	if not content:
		print 'initializing user file'
		init_check.write(str(init_json))		
		print 'done'
	init_check.close()
	
def fcer(connection, address):
#    try:
#        connection.settimeout(5000)
	homepath = os.environ['HOME']
	fa_usrs = homepath + '/fa_users'	
	global aliveUsers
	usr_id = connection.getpeername()[0]
	with open(fa_usrs, 'r') as file_r:
		usr_data = json.load(file_r)

		#while the user's info is in the dataset, directly greet and put the user online
		if usr_id in usr_data:
			uname = usr_data[usr_id]
			online_users = ""               
			for u in threads:
				if u in usr_data:
					online_users += usr_data[u] + '\n'
			connection.send('Welcome back, ' + uname + '! Now you can reach others online, current users:\n' + online_users)                
			recv_buf = connection.recv(1024)               
			if recv_buf == 'killme':
				threads.remove(usr_id)
				print uname + ' just quit!'
				aliveUsers -= 1
				print 'current users in total: %d' % aliveUsers
			else:
				d_addr = 'default'
				d_addr = query(recv_buf, usr_data)
				print recv_buf, d_addr
				if d_addr == False:
					errortarget = 'unknown user, please quit and login again'
					connection.send(errortarget)
					threads.remove(usr_id)
					print uname + ' just quit!'
					aliveUsers -= 1
					print 'current users in total: %d' % aliveUsers
				else:				               
					newConn = clients[d_addr]
					talk_flag = 1
					while talk_flag:
						buf = connection.recv(1024)
						print buf
						if buf == 'killme':
							threads.remove(usr_id)
							print uname + ' just quit!'
							aliveUsers -= 1
							print 'current users in total: %d' % aliveUsers
							talk_flag = 0
						else:
							newConn.send('From ' + uname + ': ' + buf)

		#if the user is new, ask the user to fill basic info and save it in the datafile                          
		else:
			connection.send('Welcome to use FC! As a new user, please provide a user name')
			usr_name = connection.recv(1024)
			print usr_name
			user = {usr_id: usr_name}
			usr_data.update(user)
			with open(fa_usrs, 'w') as file_w:  
				json.dump(usr_data, file_w)              
			online_users = ""               
			for u in threads:
				if u in usr_data:
					online_users += usr_data[u] + '\n'
			connection.send('Now you can reach others online, current users:\n' + online_users)
			recv_buf = connection.recv(1024)
			if recv_buf == 'killme':
				threads.remove(usr_id)
				print usr_name + ' just quit!'
				aliveUsers -= 1
				print "current users in total: %d" % aliveUsers
			else:
				d_addr = 'default'
				d_addr = query(recv_buf, usr_data)
				print recv_buf, d_addr
				if d_addr == False:
					errortarget = 'unknown user, please quit and login again'
					connection.send(errortarget)
					threads.remove(usr_id)
					print usr_name + ' just quit!'
					aliveUsers -= 1
					print 'current users in total: %d' % aliveUsers
				else:
					newConn = clients[d_addr]
					talk_flag = 1
					while talk_flag:
						buf = connection.recv(1024)
						print buf
						if buf == 'killme':
							threads.remove(usr_id)
							print usr_name + ' just quit!'
							aliveUsers -= 1
							print 'current users in total: %d' % aliveUsers
							talk_flag = 0
						else:
							newConn.send('From ' + usr_name + ': ' + buf)

#    except socket.timeout:
#   add remove threads array statements here
#        print str(connection.getpeername()[0]) + 'time out'
#   connection.close()

#setup the server
server = raw_input('Please input the ip address of your computer: ')
serverip = str(server)
initcheck()
s_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_sock.bind((serverip, 8000))
s_sock.listen(15)
print 'Server is listening on port 8000'
while True:
	connection, addr = s_sock. _sock.accept()  
	newThread = threading.Thread(target = fcer, args = (connection, addr))
	newThread.setName(connection.getpeername()[0])
	threads.append(newThread.getName())
	clients[connection.getpeername()[0]] = connection
	newThread.start()
	aliveUsers += 1   
	print "current users in total: %d" % aliveUsers


#!/usr/bin/env python

import socket
import sys
import select
import os
import datetime
import time



def escape_control_chars(text):
	escaped_text = ''
	for c in text:
		escaped_text += c if ord(c) > 31 else '<' + str(ord(c)) + '>'
	return escaped_text

def process_data(data):
	data = data.split('\r\n')
	if data[0] == 'Go team venture!':
		if data[1] == 'restart':
			print >>sys.stderr, 'received restart'
			print >>sys.stderr, os.system('reboot')
			return 'Restarting'

		if data[1] == 'hostname':
			hostname = os.popen('hostname').read()
			print >>sys.stderr, hostname
			return hostname

		if data[1] == 'shutdown':
			print >>sys.stderr, 'received shutdown'
			print >>sys.stderr, os.system("shutdown now")
			return 'Shutting down'

	return 'H.E.L.P.eR.!'


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setblocking(0)

# Bind the socket to the port
server_address = ('quizboy.local', 10000)
print >>sys.stderr, 'starting up on %s port %s' % server_address

while True:
	try:
		sock.bind(server_address)
		break
	except socket.error:
		time.sleep(60)

# Listen for incoming connections
sock.listen(1)

print >>sys.stderr, 'Entering connection loop'
while True:
	# Wait for a connection
	try: 
		connection, client_address = sock.accept()

		try:
			print >>sys.stderr, 'connection from', client_address, ' at ', datetime.datetime.now().strftime('%H:%M:%S')

			full_data = ''
			data = ''
			# Receive the data in small chunks and retransmit it
			while True:
				if '\x00' in data: 
					print >>sys.stderr, 'Found NUL'
				else:
					data_ready = select.select([connection], [], [], 15)
				if data_ready[0] and '\x00' not in data:
					data = connection.recv(4096)
					full_data += data
					print >>sys.stderr, 'received "%s"' % data
					print >>sys.stderr, 'message length %s' % len(data)
					print >>sys.stderr, 'sending data back to the client'
					connection.sendall('\x06')
				else:
					print >>sys.stderr, 'no more data from', client_address
					print >>sys.stderr, 'Full data received:'
					print >>sys.stderr, escape_control_chars( full_data )
					connection.sendall( process_data(full_data) + '\x00' )
					break
			
		finally:
			# Clean up the connection
			connection.close()
			print >>sys.stderr, 'Connection closed'
	except socket.error:
		pass

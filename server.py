import socket, select 
import time 

host, port = "172.20.10.2"	, 25001
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

num = 0
readable = [sock]
i = 0
sock.send("Connection is Created".encode("utf-8"))
while True:
		# r will be sockets with readable data
		# print(f"selecting readers, writers and iterables")
		r,w,e = select.select(readable, [], [], 0)
		# If there are sockets with readable data
		for rs in r:
			print("Looking for data: {rs}")
			if rs is socket:
				print("Socket is readable")
				c,a = sock.accept()
				# Add the new socket to the list of readable sockets
				print('\r{}:'.format(a), 'connect')
			else:
				try:
					data = rs.recv(1024)
					if not data:
						print('\r{}:'.format(rs.getpeername()),'disconnected')
						readable.remove(rs)
						rs.close()
					else:
						print('r{}:'.format(rs.getpeername()), data.decode('utf-8'))
						time.sleep(0.5)
						string = f"SAM IS SEXY: {num}" 
						num += 1
						sock.send(string.encode('utf-8')) #Converting string to Byte, and sending it to C#
						print("Sent: " + string)
				except Exception as e:
					print(e)
		i += 1

		# received_data = sock.recv(1024).decode("UTF-8") #Receiving data from C#
		# print(received_data)
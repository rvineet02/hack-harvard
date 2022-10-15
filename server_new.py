import collections  # for the buffer
import re
import time  # to ease polling
import threading 
import socket, select 
import time 

def write_to_socket(sock, terminate_signal):
	try:
		num = 0
		while not terminate_signal.is_set():
			# print("Sending data")
			string = f"SAM IS SEXY: {num}" 
			num += 1
			sock.send(string.encode('utf-8'))
			time.sleep(1.5)
	except KeyboardInterrupt:
		print("Keyboard Interrupt")
		terminate_signal.set()
	except Exception as e:
		print(e)

def process(hand):	
	# Replace (0.00,0.00,-0.00) with (0.00;0.00;-0.00)
	hand = re.sub(r'\((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\)', r'(\1;\2;\3)', hand)
	spl = hand.split(",")

	hand_type = spl[0]
	spl = spl[1:]

	types = spl[::2]
	coords = spl[1::2]

	type_to_coord = {}
	for t, c in zip(types, coords):
		c = c.replace("(", "").replace(")", "")
		tup = tuple(map(float, c[1:-1].split(";")))
		type_to_coord[t] = tup

	points_as_arr = [0] * 21
	points_as_arr[0] = type_to_coord["Hand_Start"]
	points_as_arr[1] = type_to_coord["Hand_Thumb1"]
	points_as_arr[2] = type_to_coord["Hand_Thumb2"]
	points_as_arr[3] = type_to_coord["Hand_Thumb3"]
	points_as_arr[4] = type_to_coord["Hand_ThumbTip"]
	points_as_arr[5] = type_to_coord["Hand_Index1"]
	points_as_arr[6] = type_to_coord["Hand_Index2"]
	points_as_arr[7] = type_to_coord["Hand_Index3"]
	points_as_arr[8] = type_to_coord["Hand_IndexTip"]
	points_as_arr[9] = type_to_coord["Hand_Middle1"]
	points_as_arr[10] = type_to_coord["Hand_Middle2"]
	points_as_arr[11] = type_to_coord["Hand_Middle3"]
	points_as_arr[12] = type_to_coord["Hand_MiddleTip"]
	points_as_arr[13] = type_to_coord["Hand_Ring1"]
	points_as_arr[14] = type_to_coord["Hand_Ring2"]
	points_as_arr[15] = type_to_coord["Hand_Ring3"]
	points_as_arr[16] = type_to_coord["Hand_RingTip"]
	points_as_arr[17] = type_to_coord["Hand_Pinky1"]
	points_as_arr[18] = type_to_coord["Hand_Pinky2"]
	points_as_arr[19] = type_to_coord["Hand_Pinky3"]
	points_as_arr[20] = type_to_coord["Hand_PinkyTip"]

	return points_as_arr, hand_type




def save(data):
	with open("data.txt", "a") as f:
		f.write(data)

def simulate():
	with open("data.txt", "r") as f:
		for line in f:
			process(line)

def read_from_socket(sock, terminate_signal):
	data = ''
	sock.settimeout(15)
	try:
		while True:
			# Read from socket
			char = sock.recv(1)
			if char == b'\n':
				# print("Received data")
				# process(data)
				save(data + "\n")
				print(data)
				data = ''
			else:
				data += char.decode('utf-8')
	except socket.timeout:
		print("Timeout")
		terminate_signal.set()  # signal writer that we are done
		sock.close()

if False:
	host, port = "172.20.10.2", 25001
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((host, port))
	sock.send(f"First Message".encode("utf-8"))
	print(f"Sent first message")

	terminate_signal = threading.Event()  # shared signal
	threads = [
		threading.Thread(target=read_from_socket, kwargs=dict(
			sock=sock,
			terminate_signal=terminate_signal
		)),
		threading.Thread(target= write_to_socket, kwargs=dict(
		  sock=sock,
		  terminate_signal=terminate_signal
		))
	]

	for t in threads:  # start both threads
		t.start()
	for t in threads:  # wait for both threads to finish
		t.join()
else:
	simulate()
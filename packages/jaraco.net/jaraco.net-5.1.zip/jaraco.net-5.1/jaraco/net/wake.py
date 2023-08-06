import struct
import socket

from jaraco.text import local_format as lf

def wake_on_lan(self, addr='00:00:00:00:00:00'):
	"Wake up a computer on the network"
	bytes = map(lambda bs: int(bs,16), addr.split(':'))
	binary_addr = struct.pack('BBBBBB', *bytes)
	magic_packet = '\xff'*6 + binary_addr*16
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	s.sendto(magic_packet, ('<broadcast>', 9))
	s.close()
	return lf('Woke up the computer at {addr}')

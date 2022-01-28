import time
from pathlib import Path
import socket
import sys
import argparse
import zlib

COLOR_CODE_READ = 'y'
COLOR_CODE_WRITE = 'r'
COLOR_CODE_RW = 'b'
COLOR_IGNORE = '-'
COLOR_OFF = '0'

parser = argparse.ArgumentParser()
parser.add_argument("ip", help="IP to send to")
parser.add_argument("--shift", type=int, help="Shift HDD number", default=0)
args = parser.parse_args()

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = (args.ip, 10000)
print('starting up on {} port {}'.format(*server_address))
sock.connect(server_address)

discs = Path('/sys/block/').glob("*/stat")
discs = sorted(list(discs))

ro_wo_discs = {}

for i, disc in enumerate(discs, start=0):
    shift = i + args.shift
    if args.shift:
        print(f"ID={i} -> {shift}: {disc}")
    else:
        print(f"ID={i}: {disc}")


def get_disc_activity(d):
    f = open(d).read()
    f = f.split()
    r, w = int(f[0]), int(f[4])
    prev = ro_wo_discs.get(d)
    if not prev:
        prev = {'r': 0, 'w': 0}
        
    ro, wo = prev['r'], prev['w']
    ro_wo_discs[d] = {
        'r': r, 
        'w': w,
    }
    
    if r != ro and w == wo:
        return COLOR_CODE_READ
    if w != wo and r == ro:
        return COLOR_CODE_WRITE
    if w != wo and r != ro:
        return COLOR_CODE_RW
    return COLOR_OFF


if __name__ == "__main__":
    while True:
        msg_list = ['-'] * 120
        for disc_nr, d in enumerate(discs, start=args.shift):
            code = get_disc_activity(d)
            msg_list[disc_nr] = code
        msg = ''.join(msg_list)
        msg_b = msg.encode()
        #print("> ", msg_b)
        sock.sendall(msg_b)
        time.sleep(0.05)
        #print(zlib.compress(msg_b))

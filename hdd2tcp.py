import time
import curses
from pathlib import Path
import socket
import sys
import argparse

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
        prev = {'r': 0, 'w': 0, 'flash_r': False, 'flash_w': False, 'diff_r': 0, 'diff_w': 0}
        
    ro, wo = prev['r'], prev['w']
    ro_wo_discs[d] = {
        'r': r, 
        'w': w, 
        'flash_r': r != ro, 
        'flash_w': w != wo,
        #'diff_r': abs(r - ro),  # not speed, see https://www.kernel.org/doc/Documentation/block/stat.txt
        #'diff_w': abs(w - wo)
    }
    
    if ro_wo_discs[d]['flash_r']:
        r = "READ"
    else:
        r = "    "
    if ro_wo_discs[d]['flash_w']:
        w = "WRITE"
    else:
        w = "     "
    
    return r, w
    
    """
    print_items = []
    for d, rw_data in ro_wo_discs.items():
        if rw_data['flash_r']:
            r = "READ"
        else:
            r = "    "
        if rw_data['flash_w']:
            w = "WRITE"
        else:
            w = "     "
        txt = u"{}: \u001b[31m{} \u001b[32m{}".format(d, r, w)
        #print(txt)
        stdscr.addstr(0, 0, "Disc: {0}".format(d))
        stdscr.addstr(1, 0, txt)
        stdscr.refresh()
    
    #sys.stdout.write("{}\r".format("".join(print_items)))
    #sys.stdout.flush()   
    #time.sleep(.1)
    """


if __name__ == "__main__":
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)
        
    # Colors see https://stackoverflow.com/a/22166613

    try:
        while True:
            for disc_nr, d in enumerate(discs, start=args.shift):
                rw = get_disc_activity(d)
                d_name = str(d).replace("/sys/block/", "").replace("/stat", "")
                try:
                    #stdscr.addstr(disc_nr, 0, "Disc: {0}".format(d_name))
                    #stdscr.addstr(disc_nr, 13, "|", curses.color_pair(243))
                    #stdscr.addstr(disc_nr, 16, rw[0], curses.color_pair(149))
                    #stdscr.addstr(disc_nr, 22, "|", curses.color_pair(243))
                    #stdscr.addstr(disc_nr, 25, rw[1], curses.color_pair(202))
                    #stdscr.addstr(disc_nr, 32, "|", curses.color_pair(243))
                    r = 0
                    w = 0
                    if len(rw[0].strip()):
                        r = 1
                    if len(rw[1].strip()):
                        w = 1
                    message = '{:2d},{},{};'.format(disc_nr, r, w)
                    sock.sendall(message.encode())
                    
                except curses.error:
                    pass
            #stdscr.refresh()
            time.sleep(0.05)
    finally:
        curses.echo()
        curses.nocbreak()
        curses.endwin()


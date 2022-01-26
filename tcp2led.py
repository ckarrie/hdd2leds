import socket
import sys
import time
from rpi_ws281x import PixelStrip, Color
import argparse
import threading


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('0.0.0.0', 10000)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(10)

# LED strip configuration:
LED_COUNT = 60        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

# Create NeoPixel object with appropriate configuration.
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()


color_off = Color(0, 0, 0)
color_red = Color(255, 0, 0)
color_green = Color(0, 255, 0)
color_blue = Color(0, 0, 255)
color_yellow = Color(255, 255, 0)

def client_process_thread(conn, client_address, strip):
    try:
        print('connection from', client_address)
        # Receive the data in small chunks and retransmit it
        while True:
            data = conn.recv(7)
            #print('received {!r}'.format(data))
            dec = data.decode()
            if not len(dec):
                print("hdd2tcp not running?")
                time.sleep(1)
            else:
                dec = dec.replace(";", "")
                #print(f"> {dec}")
                hddnr, r, w = dec.split(',')
                #print(f"  hddnr={hddnr} r={r} w={w}")
                r_on = int(r) == 1
                w_on = int(w) == 1
                if r_on and not w_on:
                    color = color_yellow #color_green
                elif w_on and not r_on:
                    color = color_red
                elif r_on and w_on:
                    color = color_blue
                else:
                    color = color_off
                strip.setPixelColor(int(hddnr), color)
                strip.show()
    finally:
        conn.close()

while True:
    # Wait for a connection
    print('waiting for a connection')
    conn, client_address = sock.accept()
    threading.Thread(target=client_process_thread, args=(conn, client_address, strip)).start()

sock.close()

import gevent
from gevent.queue import Queue
import gevent.monkey; gevent.monkey.patch_all(thread=False)

import os
import mido
import sys
import time
import argparse 

# use rt midi to access IAC bus
mido.set_backend('mido.backends.rtmidi')

# clock queue
clock = Queue()

# unbuffered readers
sys.stdin = os.fdopen(sys.stdin.fileno(), 'r', 1)
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)

# a lookup of notes => # midi clock messages
# midi clock sends BPM * 24 messages per minute.
# EG 60 BPM * 24 messages = 
BEATS = {
    "1/32": 3,
    "1/16": 6,
    "1/8": 12,
    "1/6": 16,
    "1/4": 24,
    "1/3": 32,
    "3/8": 36,
    "1/2": 48,
    "5/8": 60,
    "2/3": 64,
    "3/4": 72,
    "7/8": 84,
    "1": 96,
    "2": 192,
    "3": 288,
    "4": 384,
    "5": 480,
    "6": 576,
    "7": 672,
    "8": 768,
}

def midi_clock(inport, tick_count, latency):
    """
    Listen to midi clock and send 
    a "tick" to the queue at a desired 
    beat
    """
    start = latency*-1
    for i, msg in enumerate(inport, start):
        if i != start and i % tick_count == 0:
            clock.put_nowait('tick')

def stdin():
    """
    Read from stdin, blocking until a message is recieved from the clock
    """
    while True:
        line = sys.stdin.readline()
        if not line.strip(): break
        # wait to get a clock message
        tick = clock.get()
        # write it to stdout
        sys.stdout.write(line)

def quantize(inport, tick_count, latency):
    # spawn clock + stdin
    gevent.joinall([
        gevent.spawn(midi_clock, inport, tick_count, latency),
        gevent.spawn(stdin)
    ])

def main():
    
    # command line options
    parser = argparse.ArgumentParser(prog="quantize")
    parser.add_argument('-p', '--port', dest='port',
        help='The midi port on which to listen for clock messages.',
        default=os.getenv('QUANTIZE_PORT'))
    parser.add_argument('-b', '--beat', dest='beat',
        help='The beat count to sync stdin to, e.g. "1/8", "1/4", "1", etc',
        default="1/4")
    parser.add_argument('-l', '--latency', dest='latency', type=int,
        help='Number of clock ticks to offset quantization by.',
        default=1)
    parser.add_argument('-i', '--list-inputs', dest='list_inputs', action='store_true',
        help='List available input midi ports and exit.',
        default=False)
    args = parser.parse_args()

    # list input midi ports and exit.
    if args.list_inputs:
        print "Available input ports:"
        for name in mido.get_input_names():
            print "'{}'".format(name)
        sys.exit(0)

    # check args 
    if not args.port:
        print 'ERROR: quantize requires a port to run.\n' \
              'You can optionally set QUANTIZE_PORT as an environment variable.'
        sys.exit(1)
    tick_count = BEATS.get(args.beat)
    if not tick_count:
        print "ERROR: beat must be one of:\n{}".format(", ".join(BEATS.keys()))
        sys.exit(1)
    
    # try to connect to the input port
    try:
        inport = mido.open_input(args.port)
    except Exception as e:
        print "ERROR: {}".format(e.message)
        sys.exit(1)

    # run
    try:
        quantize(inport, tick_count, args.latency)
    except KeyboardInterrupt:
        sys.exit(0)
    sys.exit(0)

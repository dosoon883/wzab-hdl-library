#!/usr/bin/python
import zmq
import struct
ctx=zmq.Context()
s=ctx.socket(zmq.PAIR)
s.connect("ipc://mystream2")
mg1="This is the 1st message!"
s.send(mg1)
mg1="The 2nd message"
s.send(mg1)
mg1="The 3rd one"
s.send(mg1)
while True:
  m=s.recv()
  print m




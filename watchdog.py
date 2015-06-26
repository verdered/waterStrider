#!/usr/bin/python
# file: watchdog.py
# license: MIT License

#POSIX system watchdog!!!
#__author__="svilen.zlatev"
#__date__ ="$2014-7-17 12:37:59$"
#
#import signal
#
#class Watchdog(Exception):
#  def __init__(self, time=5):
#    self.time = time
#  
#  def __enter__(self):
#    signal.signal(signal.SIGALRM, self.handler)
#    signal.alarm(self.time)
#  
#  def __exit__(self, type, value, traceback):
#    signal.alarm(0)
#    
#  def handler(self, signum, frame):
#    raise self
#  
#  def __str__(self):
#    return "The code you executed took more than %ds to complete" % self.time 

#Usage of code below!
#Usage if you want to make sure function finishes in less than x seconds:
#
#watchdog = Watchdog(x)
#try:
#  # do something that might take too long
#except Watchdog:
#  # handle watchdog error
#watchdog.stop()
#
#Usage if you regularly execute something and want to make sure it is executed at least every y seconds:
#
#def myHandler():
#  print "Whoa! Watchdog expired. Holy heavens!"
#  sys.exit()
#
#watchdog = Watchdog(y, myHandler)

def doSomethingRegularly():
  # make sure you do not return in here or call watchdog.reset() before returning
  watchdog.reset()

    
from threading import Timer

class Watchdog:
    def __init__(self, timeout, userHandler=None):  # timeout in seconds
        self.timeout = timeout
        self.handler = userHandler if userHandler is not None else self.defaultHandler
        self.timer = Timer(self.timeout, self.handler)

    def reset(self):
        self.timer.cancel()
        self.timer = Timer(self.timeout, self.handler)

    def stop(self):
        self.timer.cancel()

    def defaultHandler(self):
        raise self
#! /usr/bin/env python

import sys
import threading
import time

class Threader(threading.Thread):
  def __init__(self, todo,
               args=None, kwargs=None, daemon=True):
    if args is None:
      self.args = []
    else:
      self.args = args
    if kwargs is None:
      self.kwargs = {}
    else:
      self.kwargs = kwargs
    self.todo = todo
    threading.Thread.__init__(self)
    self.daemon = daemon
  def run(self):
    self.todo(*self.args, **self.kwargs)

def threadit(f, args=None, kwargs=None, daemon=True):
  t = Threader(f, args, kwargs, daemon)
  t.start()
  return t

if __name__ == "__main__":
  import Tkinter
  import logging

  DURATION = 5

  def fac(m):
    if m <= 1:
      return 1
    else:
      return m * fac(m - 1)

  def waste_time(t):
    tf = time.time() + t
    while True:
      fac(20)
      # time.sleep(0.5)
      if time.time() >= tf:
        break

  def doit():
    import pygmyplot
    for i in xrange(3):
      waste_time(DURATION)
      xy = pygmyplot.MyXYPlot()
      xy.plot(range(10))
      logging.info(str(i))


  logging.basicConfig(level=logging.INFO,
                      stream=sys.stdout)

  tk = Tkinter.Tk()
  threadit(doit)
  imported.doit()
  tk.mainloop()

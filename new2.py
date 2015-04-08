#!/usr/bin/python
# -*- coding: utf-8 -*-

def addx(l, x):
  ll = []
  for [[x0, y0], [x1, y1], z] in l:
    ll.append([[x0 + x, y0], [x1 + x, y1], z])
  return ll

def addy(l, y):
  ll = []
  for [[x0, y0], [x1, y1], z] in l:
    ll.append([[x0, y0 + y], [x1, y1 + y], z])
  return ll

class convert:

  def __init__(self, s, r=[]):
    arr = []
    cur = []
    for c in s:
      if c == '\n':
        arr.append(cur)
        cur = []
      else:
        cur.append(c)
    arr.append(cur)

    res = []
    ylen = len(arr)
    maxy, maxx = 0, 0
    for y in range(ylen):
      xlen = len(arr[y])
      for x in range(xlen):
        if arr[y][x] not in ['', '|', ' ', '-']:
          cur = [ [x, y], [x + 1, y + 1] ]
          if x > 0 and arr[y][x - 1] == '|':
            arr[y][x - 1] = ''
            cur[0] = [x - 0.5, y]
          if y > 0 and arr[y - 1][x] == '-':
            arr[y - 1][x] = ''
            cur[0] = [cur[0][0], y - 0.5]
          v = arr[y][x]
          yy = y
          while yy < ylen and x < len(arr[yy]) and arr[yy][x] == v:
            xx = x
            while xx < xlen and arr[yy][xx] == v:
              arr[yy][xx] = ''
              cur[1][0] = max(cur[1][0], xx + 1)
              maxx = max(maxx, xx + 1)
              xx += 1
            cur[1][1] = max(cur[1][1], yy + 1)
            maxy = max(maxy, yy + 1)
            if xx < xlen and arr[yy][xx] == '|':
              cur[1][0] = max(cur[1][0], xx + 0.5)
              maxx = max(maxx, xx + 1)
            yy += 1
          if yy < ylen and arr[yy][x] == '-':
            cur[1][1] = max(cur[1][1], yy + 0.5)
            maxy = max(maxy, yy + 1)
          try:
            cur.append('{0}' + ('0' + str(r[int(v)]))[-2:])
          except ValueError:
            cur.append(v)
          res.append(cur)

    self.maxy = maxy
    self.maxx = maxx
    self.data = res

  def __add__(self, other):
    import copy
    c = copy.deepcopy(self)
    if type(other) == convert:
      maxy = self.maxy
      c.data.extend([ [x0, y0 + maxy], [x1, y1 + maxy], z] for [[x0, y0], [x1, y1], z] in other.data)
      c.maxy += other.maxy
      c.maxx = max(c.maxx, other.maxx)
    elif type(other) == list:
      for x in other:
        c += x
    return c

  def __mul__(self, other):
    import copy
    c = copy.deepcopy(self)
    if type(other) == convert:
      c.data.extend(addx(other.data, c.maxx))
      c.maxx += other.maxx
      c.maxy = max(other.maxy, self.maxy)
    elif type(other) == list:
      for x in other:
        c *= x
    return c

  def __truediv__(self, other):
    import copy
    c = copy.deepcopy(self)
    if type(other) == convert:
      c.data.extend(addy(addx(other.data, c.maxx), c.maxy - other.maxy))
      c.maxx += other.maxx
      c.maxy = max(other.maxy, self.maxy)
    c.reset_zero()
    return c

  def __str__(self):
    res = ''
    n = 0
    colors = ['orange', 'red', 'blue', 'green', 'pink']
    for x in self.data:
      [ [lstart, tstart], [lend, tend], what ] = x
      s = '<div style="position: absolute; background: {}; top: {}px; left: {}px; width: {}px; height: {}px;">'. \
          format(colors[n % 5], \
            str(100 * tstart), str(100 * lstart), str(100 * (lend - lstart)), \
            str(100 * (tend - tstart)))
      res += s + what + '</div>\n'
      n += 1
    return res

  def reset_zero(self):
    miny = 0
    for c in self.data:
      miny = min(miny, c[0][1], c[1][1])
    self.data = addy(self.data, -miny)

import os
root = 'output'
for location in all_thurnes:
  buildings = all_thurnes[location]
  for name, thurnes in buildings:
    os.makedirs(os.path.join(root, location, name), exist_ok=True)
    for label, prefix, info in thurnes:
      with open(os.path.join(root, location, name, label + '.html'), 'w') as f:
        f.write(str(info).format(prefix))

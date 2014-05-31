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

# TODO: deuxième du 45

# E3
troisieme_erasme = \
convert("EE0|122\n" + \
        "EE   22", [24, 22, 20]) + [\
convert("  00 11", [25 - 2 * i, 18 - 2 * i]) for i in range(7)] + \
convert("  00 DDDDTTT\n" + \
        "  11 DDDDEEE\n" + \
        "  22     EEE\n" + \
        "  XXX3344EEE", [11, 9, 7, 3, 1])

# C3
couloir_vert = \
   convert("0\n-\n-\n1", [64, 65]) * \
  [convert("0\n-\n-\n1", [62 - 2 * i, 63 - 2 * i]) for i in range(5)] * \
   convert("0\n-\n-\nX", [52]) * \
  [convert("0\n-\n-\n1", [50 - 2 * i, 51 - 2 * i]) for i in range(6)]

# R3
troisieme_rataud = (\
  convert("    CC01\n" + \
          "    C --\n" + \
          "    ----\n" + \
          "    2||E", [21, 23, 17]) * [\
  convert("0\n-\n-\n1", [25 + 2 * i, 22 + 2 * i]) for i in range(14)] * \
  convert("01EEE\n--EEE\n----\nXDDTT", [53, 55]) ) + [\
  convert("    0||1", [15 - 2 * i, 20 - 2 * i]) for i in range(6)] + \
  convert("TTTDD||0\n" + \
          "EEE--||-\n" + \
          "EEE---|1\n" + \
          "EEE23||E", [8, 6, 2, 4])

# IR2, IR4
nir24 = \
    convert(" 00", [39]) + [\
    convert(" 00", [37 - 2 * i]) for i in range(9)] + \
    convert("  X\n" + \
            " 00", [19]) + [\
    convert(" 00", [17 - 2 * i]) for i in range(8)] + \
    convert(" XX", [])

#IR3
nir3 = \
    convert(" 00", [39]) + [\
    convert(" 00", [37 - 2 * i]) for i in range(7)] + \
    convert(" 00\n" + \
            "  X", [23]) + \
    convert("  X\n" + \
            " 00", [19]) + [\
    convert(" 00", [17 - 2 * i]) for i in range(9)]

# A1
annexe1 = \
    convert("EES\n" + \
            "---\n" + \
            "---\n" + \
            "012", [2, 4, 6]) * [\
    convert("0\n-\n-\n1", [3 + 2 * i, 8 + 2 * i]) for i in range(9)] * [\
    convert(" \n-\n-\n0", [26 + 2 * i]) for i in range(6)] * \
    convert("SXEE\n" + \
            "----\n" + \
            "----\n" + \
            "0123", [38, 40, 42, 44])

# A2, A3, A4
annexe234 = \
    convert("EES\n" + \
            "---\n" + \
            "---\n" + \
            "012", [2, 4, 6]) * [\
    convert("0\n-\n-\n1", [3 + 2 * i, 8 + 2 * i]) for i in range(7)] * \
    convert("CC\n--\n--\n01", [22, 24]) * [\
    convert(" \n-\n-\n0", [26 + 2 * i]) for i in range(6)] * \
    convert("SXEE\n" + \
            "----\n" + \
            "----\n" + \
            "0123", [38, 40, 42, 44])

# TODO: jourdanBC

# JD1
jourdanD0 = \
    convert("SD0\n---\n---\n1XX", [28, 35]) * [\
    convert("0\n-\n-\n1", [26 - 2 * i, 29 - 2 * i]) for i in range(4)] * \
    convert(" \n-\n-\nE")

# JD1
jourdanD1 = \
    convert("S\n-\n-\n0", [49]) * [\
    convert("0\n-\n-\n1", [42 - 2 * i, 47 - 2 * i]) for i in range(6)] * \
    convert("0\n-\n-\nE", [30])

# JD1
jourdanD2 = \
    convert("S\n-\n-\n0", [60]) * [\
    convert("0\n-\n-\n1", [56 - 2 * i, 59 - 2 * i]) for i in range(6)] * \
    convert("0\n-\n-\nE", [44])

print(str(troisieme_rataud).format('R3'))

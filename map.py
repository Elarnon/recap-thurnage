import copy

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
  def to_paths(self, prefix):
    pathes = {}
    pad = 0.1
    for [ [ left, top ], [ right, bottom ], ( is_special, name ) ] in self.data:
      left += pad
      top += pad
      if not is_special:
        width = right - left
        height = bottom - top
        path = "M{left},{top}l{width},0l0,{height}l-{width},0l0,-{height}".format(
            left=left*1.1, top=top*1.1, width=width, height=height
        )
        if prefix == '':
          realname = name
        else:
          realname = "{}{:02}".format(prefix, name)
        pathes[realname] = {
          "name": realname,
          "path": path
        }
    return {
        "width": 2 * pad + self.maxx * 1.1,
        "height": 2 * pad + self.maxy * 1.1,
        "paths": pathes
    }

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
          left = x
          right = x + 1
          top = y
          bottom  = y + 1
          if x > 0 and arr[y][x - 1] == '|':
            arr[y][x - 1] = ''
            [ left, top ] = [x - 0.5, y]
          if y > 0 and arr[y - 1][x] == '-':
            arr[y - 1][x] = ''
            top = y - 0.5
          v = arr[y][x]
          yy = y
          while yy < ylen and x < len(arr[yy]) and arr[yy][x] == v:
            xx = x
            while xx < xlen and arr[yy][xx] == v:
              arr[yy][xx] = ''
              right = max(right, xx + 1)
              maxx = max(maxx, xx + 1)
              xx += 1
            bottom = max(bottom, yy + 1)
            maxy = max(maxy, yy + 1)
            if xx < xlen and arr[yy][xx] == '|':
              right = max(right, xx + 0.5)
              maxx = max(maxx, xx + 1)
            yy += 1
          if yy < ylen and arr[yy][x] == '-':
            bottom = max(bottom, yy + 0.5)
            maxy = max(maxy, yy + 1)
          # START XXX
          try:
            name = (False, r[int(v)])
          except ValueError:
            name = (True, v)
          res.append([ [ left, top ], [ right, bottom ], name ])
          # END XXX
          # cur = [ [ left, top ], [ right, bottom ] ]
          # try:
          #   cur.append('{0}' + ('0' + str(r[int(v)]))[-2:])
          # except ValueError:
          #   cur.append(v)
          # res.append(cur)

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


# E2
deuxieme_erasme = \
  convert("EE0|122\n" + \
          "EE   22", [24, 22, 20]) + [\
  convert("  00 11", [25 - 2 * i, 18 - 2 * i]) for i in range(7)] + \
  convert("  00 DDDDTTT\n" + \
          "  11 ----EEE\n" + \
          "  22 --- EEE\n" + \
          "  X| CCC EEE", [11, 9, 7, 3, 1])

# R2
deuxieme_rataud = (\
  convert("    CC01\n" + \
          "    C --\n" + \
          "    ----\n" + \
          "    2||E", [21, 23, 17]) * [\
  convert("0\n-\n-\n1", [25 + 2 * i, 22 + 2 * i]) for i in range(14)] * \
  convert("01EEE\n--EEE\n----\nXDDTT", [53, 55]) ) + [\
  convert("    0||1", [15 - 2 * i, 20 - 2 * i]) for i in range(6)] + \
  convert("TTTDD||0\n" + \
          "EEE   |1\n" + \
          "EEE X||2" , [8, 6, 4])

# C2, jaune
couloir_jaune = \
  convert("01\n" + \
          "--\n" + \
          "--\n" + \
          "|2", [64, 62, 63]) * [\
  convert("0\n-\n-\n1", [60 - 2 * i, 61 - 2 * i]) for i in range(9)] * \
  convert("01\n" + \
          "--\n" + \
          "--\n" + \
          "2|", [42, 40, 43])

# C2, rouge
couloir_rouge = \
  convert("      0||1", [70, 71]) + [\
  convert("      0||1", [72 + 2 * i, 73+ 2 * i]) for i in range(3)] + \
  convert("------0||1\n" + \
          "223344D||5", [78, 79, 86, 84, 82, 81]) + \
  convert("       ||0", [83]) + \
  convert("001122T||3\n" + \
          "------4||5", [88, 90, 92, 85, 96, 87]) + \
  convert("      0||1", [98, 89])+ \
  convert("       ||0", [91]) 

# C2, saumon
couloir_saumon = \
  convert("0||1", [25, 36]) + [\
  convert("0||1", [23 - 2 * i, 34 - 2 * i]) for i in range (3)] + \
  convert("0||1------\n" + \
          "2||D334455", [17, 28, 15, 24, 22, 20]) + \
  convert("0|", [13]) + \
  convert("0||T112233\n" + \
          "4||5------", [11, 14, 16, 18, 9, 10]) + [\
  convert("0||1", [7 - 2 * i, 8 - 2 * i]) for i in range(3)] + \
  convert("X||X")

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
   convert("0\n-\n-\n1", [64, 65]) * [\
   convert("0\n-\n-\n1", [62 - 2 * i, 63 - 2 * i]) for i in range(5)] * \
   convert("0\n-\n-\nX", [52]) * [\
   convert("0\n-\n-\n1", [50 - 2 * i, 51 - 2 * i]) for i in range(6)]

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
          "EEEDD||-\n" + \
          "EEE   |1\n" +\
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

# A2, A3
annexe23 = \
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
#A4
annexe4 = \
    convert("EES\n" + \
            "---\n" + \
            "---\n" + \
            "012", [2, 4, 6]) * [\
    convert("0\n-\n-\n1", [3 + 2 * i, 8 + 2 * i]) for i in range(7)] * \
    convert("CX\n--\n--\n01", [22, 24]) * [\
    convert(" \n-\n-\n0", [26 + 2 * i]) for i in range(6)] * \
    convert("SXEE\n" + \
            "----\n" + \
            "----\n" + \
            "0123", [38, 40, 42, 44])


# JBC0
jourdanBC0 = \
  convert("CD\n--\n--\nE ") * [\
  convert("0\n-\n-\n1", [90 - 2 * i, 93 - 2 * i]) for i in range(6)]

# JBC1
jourdanBC1 = \
  convert("S\n-\n-\nE") * [\
  convert("0\n-\n-\n1", ['JC' + str(104 - 2 * i), 'JC' + str(107 - 2 * i)]) \
     for i in range(7)] * [\
  convert("0\n-\n-\n1", ['JB' + str(64 - 2 * i), 'JB' + str(67 - 2 * i)]) \
     for i in range(7)] * \
  convert("S\n-\n-\nE")

# JBC2
jourdanBC2 = \
  convert("S\n--\n--\nE") * [\
  convert("0\n-\n-\n1", [118 - 2 * i, 121 - 2 * i]) for i in range(7)]

# JD0
jourdanD0 = \
    convert("CD0\n---\n---\n1XX", [28, 35]) * [\
    convert("0\n-\n-\n1", [26 - 2 * i, 29 - 2 * i]) for i in range(4)] * \
    convert(" \n-\n-\nE")

# JD1
jourdanD1 = \
    convert("S\n-\n-\n0", [49]) * [\
    convert("0\n-\n-\n1", [42 - 2 * i, 47 - 2 * i]) for i in range(6)] * \
    convert("0\n-\n-\nE", [30])

# JD2
jourdanD2 = \
    convert("S\n-\n-\n0", [60]) * [\
    convert("0\n-\n-\n1", [56 - 2 * i, 59 - 2 * i]) for i in range(6)] * \
    convert("0\n-\n-\nE", [44])

removed = [ 'UR202', 'IR319', 'IR323', 'UC204' ]

all_thurnes = {
  'Ulm': [
    ('Annexe', [
      ('Premier étage', 'UA1', annexe1),
      ('Deuxième étage', 'UA2', annexe23),
      ('Troisième étage', 'UA3', annexe23),
      ('Quatrième étage', 'UA4', annexe4),
    ]),

    ('Troisième étage du 45', [
      ('Troisième Érasme', 'UE3', troisieme_erasme),
      ('Couloir Vert', 'UC3', couloir_vert),
      ('Troisième Rataud', 'UR3', troisieme_rataud),
    ]),

    ('Deuxième étage du 45', [
      ('Deuxième Érasme', 'UE2', deuxieme_erasme),
      ('Deuxième Rataud', 'UR2', deuxieme_rataud),
      ('Couloir Jaune', 'UC2', couloir_jaune),
      ('Couloir Rouge (Travaux à partir de mai !)', 'UC2', couloir_rouge),
      ('Couloir Saumon', 'UC2', couloir_saumon),
    ]),

    ['NIR', [
      ('Deuxième étage', 'IR2', nir24),
      ('Troisième étage', 'IR3', nir3),
      ('Quatrième étage', 'IR4', nir24),
    ]],
    ],

  'Jourdan': [
    ('Pavillon D', [
      ('Rez-de-chaussée', 'JD1', jourdanD0),
      ('Premier étage', 'JD1', jourdanD1),
      ('Deuxième étage', 'JD1', jourdanD2),
    ]),
    ('Pavillons B et C', [
      ('Rez-de-chaussée', 'JC', jourdanBC0),
      ('Premier étage', '', jourdanBC1),
      ('Deuxième étage', 'JC', jourdanBC2),
    ]),
    ]
}

step = 50

import json

for location in all_thurnes:
  buildings = all_thurnes[location]
  for name, floors in buildings:
    for label, prefix, plan in floors:
      with open("maps/{}_{}_{}.json".format(location, name, label), 'w') as f:
        json.dump(plan.to_paths(prefix), f)

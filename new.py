from bs4 import BeautifulSoup#{{{
import urllib.request
import re
import copy#}}}


from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('./templates/'))

class comment:#{{{
  def __init__(self, author, year, state, mezza, volets, rideaux, text):
    # Compute comment tags
    infos = [{ 'color': state['color'], 'text': state['name'] }]
    self.mezza = False
    if mezza != 'Non':
      self.mezza = True
      infos.append({ 'color': 'green', 'text': 'Mezzanine ' + mezza })
    if volets:
      infos.append({ 'color': 'green', 'text': 'Volets' })
    if rideaux:
      infos.append({ 'color': 'green', 'text': 'Rideaux' })
    # Store
    self.author = author
    self.year = int(year)
    self.state = state
    self.text = text
    self.infos = infos

  def __str__(self):
    html = '<blockquote>'
    for info in self.infos:
      html += '''
      <span class="label" style="background-color: {info[color]}">
        {info[text]}
      </span>
      '''.format(info=info)
    html += self.text
    html += '<small>{0.author}, {0.year}</small>'.format(self)
    html += '</blockquote>'
    return html#}}}

state_of_class = {#{{{
    'bon':         { 'color': 'green'    , 'name': 'Bon état'          },
    'moyen':       { 'color': 'orange'   , 'name': 'État moyen'        },
    'mauvais':     { 'color': 'red'      , 'name': 'Mauvais état'      },
    'tresbon':     { 'color': 'darkgreen', 'name': 'Très bon état'     },
    'tresmauvais': { 'color': 'darkred'  , 'name': 'Très mauvais état' },
    }#}}}

def parse_comments(thurnes, html_doc):#{{{
  for table in html_doc.find_all('table'):
    for tr in table.find_all('tr'):
      tds = tr.find_all('td', recursive=False)
      if len(tds) == 8: # Check it really is informations about a room
        name = thurne.normalize_name(tds[0].string, mezza=tds[4].string)
        # Check thurne is in the database
        if not name in thurnes:
          print("Unknown thurne ", tds[0].string, name, tds[4].string)
          continue
        # Parse data
        author = tds[1].string
        year = int(tds[2].string)
        state = state_of_class[tds[3].find('span')['class'][0]]
        mezza = tds[4].string
        volets = tds[5].string == 'Oui'
        rideaux = tds[6].string == 'Oui'
        text = tds[7].string
        # Create comment object
        thurnes[name].comments.append(
            comment(author, year, state, mezza,
              volets, rideaux, text)
            )#}}}

def parse_results(dic, html_doc):#{{{
  tbl = html_doc.find_all(text=re.compile('Choix des'))[0].parent.find_next_sibling('table')
  for child in tbl.find_all('tr'):
    tds= child.find_all('td', recursive=False)
    if len(tds) == 4 and tds[2].string != None:
      name = thurne.normalize_name(tds[2].string)
      if name not in dic:
        continue
      person = tds[1].string
      dic[name].owner = person#}}}


## START ANEW

class thurne:
  template = env.get_template('thurne.html')
  def __init__(self, name, left, top, width, height):
    self.special = False
    self.name = name
    self.vertical = height > width
    self.removed = False
    self.rank = None
    # if height > width:
    #   width = 15/40.
    # elif width > height:
    #   height = 0.5
    self.position = (left * 1.5, top * 1.5, width, height)
    self.comments = []
    self.owner = None

  def zoom(self, k):
    left, top, width, height = self.position
    left *= k
    top *= k
    width *= k
    height *= k
    self.position = (left, top, width, height)

  def __str__(self):
    # Trie les commentaires avec les plus récents en premier
    self.comments.sort(key=lambda comment: comment.year, reverse=True)
    # L'état de la chambre est l'état donné par le dernier commentaire, si présent
    state = { 'color': 'grey', 'name': 'État inconnu' }
    if len(self.comments) > 0 and self.comments[0].year > 2009: # TODO: current_year - 4
      state = self.comments[0].state
    mezza = False
    if len(self.comments) > 0:
      mezza = self.comments[0].mezza
    color = state['color']
    # Informations sur l'occupant de la chambre
    info = ''
    # Génération du HTML
    (left, top, width, height) = self.position
    return thurne.template.render(
      top=top, left=left, width=width, height=height,
      color=color, name=self.name, state=state['name'],
      comments=self.comments, owner=self.owner, vertical=self.vertical,
      mezza=mezza, removed=self.removed, rank=self.rank)

  def normalize_name(name, mezza=None):
    """ Discard spaces and truncates a string to 5 characters, the
    common name format for rooms.  """
    res = name.replace(' ', '').replace('-', '').replace(';', '')[:5].upper()
    res = res.rstrip(''.join(chr(i) for i in range(ord('A'), ord('Z'))))
    if re.match(r"^[A-Z][0-9]{,3}$", res):
      if mezza is not None and 'non' not in mezza.lower():
        res = "U" + res
      elif res[0] == 'A' or res[0] == 'R':
        res = "U" + res
    elif re.match(r"^[0-9]{,3}$", res) and mezza is not None and 'non' not in mezza.lower():
      res = "UC" + res
    return res

class thurnes:
  template = env.get_template('thurnes.html')
  def __init__(self, label, prefix, data, width, height):
    self.label = label
    self.prefix = prefix
    self.thurnes = data
    self.width = width * 1.5
    self.height = height * 1.5

  def zoom(self, k):
    self.width *= k
    self.height *= k
    for thurne in self.thurnes:
      thurne.zoom(k)

  def __str__(self):
    nb_thurnes = 0
    for thurne in self.thurnes:
      if not thurne.special:
        nb_thurnes += 1
    return thurnes.template.render(
      width=self.width, height=self.height, label=self.label, thurnes=self.thurnes,
      nb_thurnes=nb_thurnes
    )

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

class special:
  template = env.get_template("special.html")
  def __init__(self, name, left, top, width, height):
    self.special = True
    self.left = left * 1.5
    self.top = top * 1.5
    self.width = width
    self.height = height
    self.name = name

  def zoom(self, k):
    self.left *= k
    self.top *= k
    self.width *= k
    self.height *= k

  def __str__(self):
    vertical = self.height > self.width
    return special.template.render(
      top=self.top, left=self.left, width=self.width, height=self.height,
      name=self.name, vertical=vertical)
    
specials = {
  'E': "Escaliers",
  'T': "Toilettes",
  'S': "Sanitaires",
  'X': "Autres",
  'D': "Douches",
  'C': "Cuisine",
}

class convert:
  def to_thurnes(self, label, prefix):
    res = []
    for [ [ left, top ], [ right, bottom ], ( is_special, name ) ] in self.data:
      width = right - left
      height = bottom - top
      if is_special:
        res.append(special(specials[name], left=left, top=top, width=width, height=height))
      else:
        fullname = name if prefix == '' else '{}{:02}'.format(prefix, name)
        res.append(thurne(name=fullname, left=left, top=top, width=width, height=height))
    return thurnes(label, prefix, res, width=self.maxx, height=self.maxy)

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
  'Ulm (115 thurnes disponibles)': [
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

  'Jourdan (23 thurnes disponibles)': [
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

# Database creation
tinfo = {}
for location in all_thurnes:
  tinfo[location] = []
  buildings = all_thurnes[location]
  for name, floors in buildings:
    new_floors = []
    tinfo[location].append((name, new_floors))
    for label, prefix, plan in floors:
      new_thurnes = (plan.to_thurnes(label, prefix))
      new_thurnes.zoom(35)
      new_floors.append(new_thurnes)
    new_floors.sort(key=lambda thurnes: thurnes.prefix)
  tinfo[location].sort(key=lambda x: x[0])

dic = {}
for location in tinfo:
  buildings = tinfo[location]
  for name, floors in buildings:
    for rooms in floors:
      for th in rooms.thurnes:
        # TODO: Check special.
        th.removed = th.name in removed
        dic[th.name] = th

# État des chambres#{{{
url = urllib.request.urlopen('http://www.dg.ens.fr/thurnage/EtatChambre.html')
html_doc = BeautifulSoup(url.read().decode('utf8'))
url.close()

# Résultats !!!!#{{{
url = urllib.request.urlopen('http://www.dg.ens.fr/thurnage/2013/resultats-classement.html')
html_doc3 = BeautifulSoup(url.read().decode('utf8'))
url.close()

parse_results(dic, html_doc3)#}}}

parse_comments(dic, html_doc)#}}}

with open('rank') as ranks:
  nth = 1
  for line in ranks:
    [ name, rank ] = line.strip().split(':')
    name = name.strip()
    rank = round(float(rank.strip()), 1)
    if name in dic:
      dic[name].rank = '{}'.format(nth)
    nth += 1

# Manual beautification
for location in tinfo:
  buildings = tinfo[location]
  for name, floors in buildings:
    if name == "NIR":
      st = '<div class=span{}">'.format(12 / len(floors))
      en = '</div>'
      floors[:] = [st + (en + st).join(str(floor) for floor in floors) + en]

html = env.get_template('index.html')
for location in tinfo:
  with open('output/' + location + '.html', 'w') as output:
    output.write(html.render(buildings=tinfo[location], where=location))

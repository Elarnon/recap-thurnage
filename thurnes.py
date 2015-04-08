from bs4 import BeautifulSoup#{{{
import urllib.request
import re
import copy#}}}

class thurne:#{{{
  def __init__(self, name, comments, base_style, base_class):
    self.name = name
    self.comments = comments
    self.base_style = base_style
    self.base_class = base_class
    self.occupant = None
    self.garde_thurne = None
    self.rank = None

  def __str__(self):
    # Détermination du dernier état connu
    self.comments.sort(key=lambda comment: comment.year, reverse=True)
    state = { 'color': 'grey', 'name': 'État inconnu' }
    if len(self.comments) > 0:
      state = self.comments[0].state
    color = state['color']
    # Intégration des informations d'occupant
    occupied = []
    if self.garde_thurne != None:
      color = 'black'
      occupied += [ 'Garde-thurne par ' + self.garde_thurne + '.' ]
    notif = '<i class="icon-ok"></i>'
    if self.occupant != None:
      notif = '<i class="icon-user"></i>'
      occupied += [ 'Occupé par ' + self.occupant + '.' ]
    occupied = '<br />'.join(occupied)
    if self.rank is not None:
      rank = " - Classement : {}".format(self.rank)
    else:
      rank = ""
    # Génération du HTML
    return '''
    <div style="{base_style}; background-color: {color};"
         class="{base_class} label" rel="popover" title="{name} ({state}){rank}"
         data-content="{comments} {occupied}">
      <div class="turne-content">{name}{occupied_notif}</div>
      <span class="badge badge-info">{nb_comments}</span>
    </div>
    '''.format(
      rank=rank,
      base_style=self.base_style, base_class=self.base_class, color=color,
        name=self.name, occupied_notif=notif, state=state['name'],
        comments=''.join(map(str, self.comments)).replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;'), # TODO escape
        occupied=occupied, nb_comments=len(self.comments))

  def normalize_name(name):
    return name.replace(' ', '')[:5].upper()#}}}

class comment:#{{{
  def __init__(self, author, year, state, mezza, volets, rideaux, text):
    # Compute comment tags
    infos = [{ 'color': state['color'], 'text': state['name'] }]
    if mezza != 'Non':
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
        name = thurne.normalize_name(tds[0].string)
        # Check thurne is in the database
        if not name in thurnes:
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

def parse_unavail(dic, html_doc):#{{{
  sibling = html_doc.find_all(text=re.compile('Gardes-thurnes'))[0].parent
  tbl = sibling.find_next_sibling('table')
  for child in tbl.find_all('tr'):
    tds = child.find_all('td', recursive=False)
    if len(tds) == 4:
      name = thurne.normalize_name(tds[2].string)
      if name not in dic:
        continue
      person = tds[1].string
      dic[name].garde_thurne = person#}}}

def parse_results(dic, html_doc):#{{{
  tbl = html_doc.find_all(text=re.compile('Choix des'))[0].parent.find_next_sibling('table')
  for child in tbl.find_all('tr'):
    tds= child.find_all('td', recursive=False)
    if len(tds) == 4 and tds[2].string != None:
      name = thurne.normalize_name(tds[2].string)
      if name not in dic:
        continue
      person = tds[1].string
      dic[name].occupant = person#}}}

# Largeur thurne
step = 30

# Thurnes à Montrouge, tour B
mtrg_b_thurnes = (#{{{
    {
      '14':  (['top',     'left'],   (0,  0),  {},  'turne-h'),
      '13':  (['top',     'left'],   (0,  1),  {},  'turne-h'),
      '12':  (['top',     'left'],   (0,  2),  {},  'turne-h'),
      '11':  (['top',     'left'],   (0,  3),  {},  'turne-h'),
      '10':  (['top',     'left'],   (0,  4),  {},  'turne-h'),
      '09':  (['top',     'left'],   (0,  5),  {},  'turne-h'),
      '08':  (['top',     'left'],   (0,  6),  {},  'turne-h'),
      '07':  (['top',     'left'],   (0,  7),  {},  'turne-h'),
      '18':  (['bottom',  'left'],   (0,  0),  {},  'turne-w'),
      '17':  (['bottom',  'left'],   (1,  0),  {},  'turne-w'),
      '16':  (['bottom',  'left'],   (2,  0),  {},  'turne-w'),
      '15':  (['bottom',  'left'],   (3,  0),  {},  'turne-w'),
      '03':  (['bottom',  'right'],  (0,  0),  {},  'turne-w'),
      '04':  (['bottom',  'right'],  (1,  0),  {},  'turne-w'),
      '05':  (['bottom',  'right'],  (2,  0),  {},  'turne-w'),
      '06':  (['bottom',  'right'],  (3,  0),  {},  'turne-w'),
      },
    # Special
    {
      'Cuisine':    (['bottom',  'left'],   (0,  3.1),  {},  'cuisine'),
      'Toilettes':  (['bottom',  'right'],  (1,  3.1),  {},  'toilettes'),
      'Laverie':    (['bottom',  'right'],  (0,  0),    {},  'turne-w'),
      })#}}}

# Thurnes à Montrouge, tour C
mtrg_c_thurnes = copy.deepcopy(mtrg_b_thurnes)#{{{
mtrg_c_thurnes[1]['Toilettes'][0][1] = 'left' # Swap toilets#}}}

# Septième étage de Montrouge, tour B
mtrg_b7 = (#{{{
    {
      '04':  (['bottom',  'right'],  (4,  0),  {},  'turne-w'),
      '05':  (['bottom',  'right'],  (3,  0),  {},  'turne-w'),
      '06':  (['bottom',  'right'],  (2,  0),  {},  'turne-w'),
      '07':  (['bottom',  'right'],  (1,  0),  {},  'turne-w'),
      },
    # Special
    {
      'Toilettes':  (['bottom',  'right'],  (1,  3.1),  {},  'toilettes'),
      'Cuisine':    (['bottom',  'left'],   (0,  3.1),
                     { 'width': '145px', 'text-align': 'center' }, 'cuisine'),
      })#}}}

# Septième étage de Montrouge, tour C
mtrg_c7 = copy.deepcopy(mtrg_b7)#{{{
mtrg_c7[1]['Toilettes'][0][1] = 'left' # Swap toilets#}}}

# Étages impairs à Montrouge
mtrg_odd = ([       '04', '05', '06', '07', '08', '09', '10', '11', '12', '13'#{{{
            , '14', '15', '16', '17', '18' ], [ 'Cuisine', 'Toilettes', 'Laverie' ])#}}}

# Étages pairs à Montrouge
mtrg_even = ([ '03' ] + mtrg_odd[0], [ 'Cuisine', 'Toilettes' ])

# Septième étage à Montrouge
mtrg_seven = ([ '04', '05', '06', '07' ], [ 'Cuisine', 'Toilettes' ])

# Tout Montrouge réuni !
mtrg = [#{{{
    ("Tour B - Montrouge", "MB", [
      ([2, 4, 6], mtrg_even, mtrg_b_thurnes),
      ([1, 3, 5], mtrg_odd, mtrg_b_thurnes),
      ([7,     ], mtrg_seven, mtrg_b7),
      ]),
    ("Tour C - Montrouge", "MC", [
      ([2, 4, 6], mtrg_even, mtrg_c_thurnes),
      ([1, 3, 5], mtrg_odd, mtrg_c_thurnes),
      ([7,     ], mtrg_seven, mtrg_c7),
      ]),
    ]#}}}

# Thurnes database creation
dic = {}#{{{
for bat in mtrg:
  name = bat[0]
  prefix = bat[1]
  for etages in bat[2]:
    nums = etages[0]
    thurnes = etages[1]
    display = etages[2]
    for etage in nums:
      for tname in thurnes[0]:
        info = display[0][tname]
        dic[prefix + str(etage) + tname] = thurne(
            name=prefix + str(etage) + tname,
            comments=[],
            base_style=info[0][0] + ': ' + str(info[1][0] * step) + 'px; '
                      + info[0][1] + ': ' + str(info[1][1] * step) + 'px; '
                      + '; '.join(k + ': ' + info[2][k] for k in info[2]),
            base_class=info[3])#}}}

# État des chambres#{{{
url = urllib.request.urlopen('http://www.dg.ens.fr/thurnage/EtatChambre.html')
html_doc = BeautifulSoup(url.read().decode('utf8'))
url.close()

parse_comments(dic, html_doc)#}}}

# Garde-thurne#{{{
# url = urllib.request.urlopen('http://www.dg.ens.fr/thurnage/2012/classement.html')
# html_doc2 = BeautifulSoup(url.read().decode('utf8'))
# url.close()

# parse_unavail(dic, html_doc2)#}}}

# Résultats !!!!#{{{
url = urllib.request.urlopen('http://www.dg.ens.fr/thurnage/2013/resultats-classement.html')
html_doc3 = BeautifulSoup(url.read().decode('utf8'))
url.close()

parse_results(dic, html_doc3)#}}}


with open('rank') as ranks:
  nth = 1
  for line in ranks:
    [ name, rank ] = line.strip().split(':')
    name = name.strip()
    rank = round(float(rank.strip()), 1)
    if name in dic:
      dic[name].rank = '{}'.format(nth)
    nth += 1

html = ''#{{{
for bat in mtrg:
  name = bat[0]
  prefix = bat[1]
  html += '<h2 class="page-header" style="padding-top: 42px;" id="' + prefix + '">' + name + '</h2>'
  html += '<div class="turnes">'
  floors = []
  for etages in bat[2]:
    nums = etages[0]
    thurnes = etages[1]
    for etage in nums:
      floor = ''
      floor += '<div class="well" style="margin: auto; width: 240px;">' # TODO size
      floor += '<div style="width: 240px; height: 240px; position: relative;">'
      for tname in thurnes[0]:
        floor += str(dic[prefix + str(etage) + tname])
      for spec in thurnes[1]:
        info = etages[2][1][spec]
        floor += '''
        <div style="{base_style}; background-color: darkorchid; cursor: default;"
        class="{base_class} label">
          <div class="turne-content">{name}</div></div>
        '''.format(base_style=info[0][0] + ': ' + str(info[1][0] * step) + 'px; '
                      + info[0][1] + ': ' + str(info[1][1] * step) + 'px; '
                      + '; '.join(k + ': ' + info[2][k] for k in info[2]),
            base_class=info[3],
            name=spec)
      floor += '</div>'
      floor += '<div style="width: 100%; text-align: center; margin-bottom: -10px; margin-top: 5px;">'
      floor += 'Étage ' + prefix + str(etage) + ' (' + str(len(thurnes[0])) + ' chambres)'
      floor += '</div></div>'
      floors.append( (etage, floor) )
  floors.sort(key=lambda x: x[0])
  rem = len(floors)
  i = 0
  html += '<div class="row" style="margin-bottom: 10px">'
  for floor in floors:
    if i % 3 == 0:
      span = 4 * (rem >= 3) + 6 * (rem == 2) + 12 * (rem == 1)
      if i != 0:
        html += '</div><div class="row" style="margin-bottom: 10px">'
    html += '<div class="span' + str(span) + '">' + floor[1] + '</div>'
    i += 1
    rem -= 1
  html += '</div></div>'#}}}

with open('index.html.tpl', 'r') as tpl:#{{{
  with open('output/Montrouge.html', 'w') as index:
    index.write(tpl.read().replace('{0}', html))#}}}

print('Done.')

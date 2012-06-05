from bs4 import BeautifulSoup
import urllib.request
import re
from functools import reduce

class thurne:#{{{
  __slots__ = ('state', 'name', 'comments')

  def __init__(self, name, comments, state):
    self.state = state
    self.name = name
    self.comments = comments
    pass

  def __str__(self):
    html = '''
    <div style="{base_style}; background-color: {color};"
         class="{base_class} label" rel="popover" title="{name} ({state})"
         data-content="{comments}">
      <div class="turne-content">{name}</div>
      <span class="badge badge-info">{nb_comments}</span>
    </div>
    '''.format(
        base_style=base_style,
        base_class=base_class,
        color=self.state['color'],
        name=self.name,
        state=self.state['name'],
        comments=''.join(map(str, self.comments)),
        nb_comments=len(self.comments)
        )

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
      <span class="label" style="background-color: {info.color}">
        {info.text}
      </span>
      '''.format(info=info)
    html += self.text
    html += '<small>{0.author}, {0.year}</small>'.format(self)
    html += '</blockquote>'
    return html#}}}

def mk_turne(turne_infos, base_style, base_classes):
  if 'special' not in turne_infos:
    s = """
    <div style="{0} background-color: {5}" class="{1} label" rel="popover" title="{2} ({6})"
    data-content="{3}">
      <div class="turne-content">
        {2}
      </div>
        <span class="badge badge-info">{4}</span>
    </div>
    """.format(base_style, base_classes, turne_infos['name'], turne_infos['comments'],
        turne_infos['nb_comments'], turne_infos['status_color'], turne_infos['state'])
  else:
    s = """
    <div style="{0} background-color: darkorchid; cursor: default" class="{1} label">
      <div class="turne-content">{2}</div>
      </div>""".format(base_style, base_classes, turne_infos['name'])
  return s

def mk_turne_infos(raw):
  if 'special' in raw:
    return { 'name': raw['turne_name'], 'special': True }
  state = get_last_state(raw)
  nb = len(raw['comments'])
  if raw['available']:
    color = state['color']
  else:
    color = 'black'
    raw['comments'].append({
      'infos': [],
      'text': 'Occupé par ' + raw['occupied_by'],
      'author': raw['occupied_by'],
      'year': '2012'
      })
  turne_infos = {
      'name': raw['turne_name'],
      'comments': mk_turne_comments(raw),
      'nb_comments': nb,
      'status_color': color,
      'state': state['name']
      }
  return turne_infos

def get_last_state(raw):
  bst = {'color': 'grey', 'name': 'État inconnu.'}
  bst_yr = 0
  for comment in raw['comments']:
    if int(comment['year']) > bst_yr:
      bst = comment['status']
      bst_yr = int(comment['year'])
  return bst

state_of_class = {#{{{
    'bon':         { 'color': 'green'    , 'name': 'Bon état'          },
    'moyen':       { 'color': 'orange'   , 'name': 'État moyen'        },
    'mauvais':     { 'color': 'red'      , 'name': 'Mauvais état'      },
    'tresbon':     { 'color': 'darkgreen', 'name': 'Très bon état'     },
    'tresmauvais': { 'color': 'darkred'  , 'name': 'Très mauvais état' },
    }#}}}

def parse_comments(thurnes, html_doc):#{{{
  for table in html_doc.find_all('table'):
    for tr in tbl.find_all('tr'):
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
        thurnes[name]['comments'].append(
            comment(author, year, state, mezza,
              volets, rideaux, text)
            )#}}}

def parse_unavail(dic, html_doc):
  tbl = html_doc.find_all(text=re.compile('Gardes-thurnes'))[0].parent.find_next_sibling('table')
  for child in tbl.find_all('tr'):
    tds = child.find_all('td', recursive=False)
    if tds != []:
      turne = thurne.normalize_name(tds[2].string)
      person = tds[1].string
      dic[turne]['available'] = False
      dic[turne]['occupied_by'] = person

mtrg_b_even = {
    '14': ("top: 0px; left: 0px;", "turne-h"),
    '13': ("top: 0px; left: 30px;", "turne-h"),
    '12': ("top: 0px; left: 60px;", "turne-h"), 
    '11': ("top: 0px; left: 90px;", "turne-h"), 
    '10': ("top: 0px; left: 120px;", "turne-h"),
    '09': ("top: 0px; left: 150px;", "turne-h"),
    '08': ("top: 0px; left: 180px;", "turne-h"),
    '07': ("top: 0px; left: 210px;", "turne-h"),
    '18': ("bottom: 0; left: 0;", "turne-w"),
    '17': ("bottom: 30px; left: 0;", "turne-w"),
    '16': ("bottom: 60px; left: 0;", "turne-w"),
    '15': ("bottom: 90px; left: 0;", "turne-w"),
    '03': ("bottom: 0; right: 0;", "turne-w"),
    '04': ("bottom: 30px; right: 0;", "turne-w"),
    '05': ("bottom: 60px; right: 0;", "turne-w"),
    '06': ("bottom: 85px; right: 0;", "turne-w"),
    ' (Cuisine)': ("bottom: 0; left: 94px;", "cuisine"),
    ' (Toilettes)': ("bottom: 30px; right: 94px;", "toilettes"),
  }

mtrg_b_odd = mtrg_b_even.copy()
mtrg_b_odd[' (Laverie)'] = mtrg_b_odd['03']
del mtrg_b_odd['03'] # laverie

mtrg_seven = {
    '04': ("bottom: 120px; right: 0;", "turne-w"),
    '05': ("bottom: 90px; right: 0;", "turne-w"),
    '06': ("bottom: 60px; right: 0;", "turne-w"),
    '07': ("bottom: 30px; right: 0;", "turne-w"),
    ' (Cuisine)': ("bottom: 0; left: 94px; width: 145px; text-align: center; ", "cuisine"),
    ' (Toilettes)': ("bottom: 30px; right: 94px;", "toilettes"),
    }

mtrg_c_seven = {
    '04': ("bottom: 120px; left: 0;", "turne-w"),
    '05': ("bottom: 90px; left: 0;", "turne-w"),
    '06': ("bottom: 60px; left: 0;", "turne-w"),
    '07': ("bottom: 30px; left: 0;", "turne-w"),
    ' (Cuisine)': ("bottom: 0; left: 94px; width: 145px; text-align: center; ", "cuisine"),
    ' (Toilettes)': ("bottom: 30px; left: 94px;", "toilettes"),
    }

url = urllib.request.urlopen('http://www.dg.ens.fr/thurnage/EtatChambre.html')
html_doc = BeautifulSoup(url.read().decode('utf8'))
url.close()

dic = {}
for etage in "135":
  for num in mtrg_b_odd:
    turne = 'MB' + etage + num
    dic[turne] = {
      'comments': [],
      'turne_name': turne,
      'available': True,
      'base_style': mtrg_b_odd[num][0],
      'base_class': mtrg_b_odd[num][1]
      }
  dic['MB' + etage + ' (Laverie)'] = {
      'comments': [],
      'turne_name': 'Laverie',
      'available': False,
      'special': True,
      'base_style': mtrg_b_odd[' (Laverie)'][0],
      'base_class': mtrg_b_odd[' (Laverie)'][1],
      }
  dic['MB' + etage + ' (Cuisine)'] = {
      'comments': [],
      'turne_name': 'Cuisine',
      'available': False,
      'special': True,
      'base_style': mtrg_b_odd[' (Cuisine)'][0],
      'base_class': mtrg_b_odd[' (Cuisine)'][1],
      }
  dic['MB' + etage + ' (Toilettes)'] = {
      'comments': [],
      'turne_name': 'Toilettes',
      'available': False,
      'special': True,
      'base_style': mtrg_b_odd[' (Toilettes)'][0],
      'base_class': mtrg_b_odd[' (Toilettes)'][1],
      }

for etage in "246":
  for num in mtrg_b_even:
    turne = 'MB' + etage + num
    dic[turne] = {
        'comments': [],
        'turne_name': turne,
        'available': True,
        'base_style': mtrg_b_even[num][0],
        'base_class': mtrg_b_even[num][1]
        }
  dic['MB' + etage + ' (Cuisine)'] = {
      'comments': [],
      'turne_name': 'Cuisine',
      'available': False,
      'special': True,
      'base_style': mtrg_b_odd[' (Cuisine)'][0],
      'base_class': mtrg_b_odd[' (Cuisine)'][1],
      }
  dic['MB' + etage + ' (Toilettes)'] = {
      'comments': [],
      'turne_name': 'Toilettes',
      'available': False,
      'special': True,
      'base_style': mtrg_b_odd[' (Toilettes)'][0],
      'base_class': mtrg_b_odd[' (Toilettes)'][1],
      }

for num in mtrg_seven:
  turne = 'MB7' + num
  dic[turne] = {
      'comments': [],
      'turne_name': turne,
      'available': True,
      'base_style': mtrg_seven[num][0],
      'base_class': mtrg_seven[num][1]
      }
dic['MB7 (Cuisine)'] = {
    'comments': [],
    'turne_name': 'Cuisine',
    'available': False,
    'special': True,
    'base_style': mtrg_seven[' (Cuisine)'][0],
    'base_class': mtrg_seven[' (Cuisine)'][1],
    }
dic['MB7 (Toilettes)'] = {
    'comments': [],
    'turne_name': 'Toilettes',
    'available': False,
    'special': True,
    'base_style': mtrg_b_odd[' (Toilettes)'][0],
    'base_class': mtrg_b_odd[' (Toilettes)'][1],
    }

for etage in "135":
  for num in mtrg_b_odd:
    turne = 'MC' + etage + num
    dic[turne] = {
      'comments': [],
      'turne_name': turne,
      'available': True,
      'base_style': mtrg_b_odd[num][0],
      'base_class': mtrg_b_odd[num][1]
      }
  dic['MC' + etage + ' (Laverie)'] = {
      'comments': [],
      'turne_name': 'Laverie',
      'available': False,
      'special': True,
      'base_style': mtrg_b_odd[' (Laverie)'][0],
      'base_class': mtrg_b_odd[' (Laverie)'][1],
      }
  dic['MC' + etage + ' (Cuisine)'] = {
      'comments': [],
      'turne_name': 'Cuisine',
      'available': False,
      'special': True,
      'base_style': mtrg_b_odd[' (Cuisine)'][0],
      'base_class': mtrg_b_odd[' (Cuisine)'][1],
      }
  # TODO
  dic['MC' + etage + ' (Toilettes)'] = {
      'comments': [],
      'turne_name': 'Toilettes',
      'available': False,
      'special': True,
      'base_style': "bottom: 30px; left: 94px;",
      'base_class': mtrg_b_odd[' (Toilettes)'][1],
      }

for etage in "246":
  for num in mtrg_b_even:
    turne = 'MC' + etage + num
    dic[turne] = {
        'comments': [],
        'turne_name': turne,
        'available': True,
        'base_style': mtrg_b_even[num][0],
        'base_class': mtrg_b_even[num][1]
        }
  dic['MC' + etage + ' (Cuisine)'] = {
      'comments': [],
      'turne_name': 'Cuisine',
      'available': False,
      'special': True,
      'base_style': mtrg_b_odd[' (Cuisine)'][0],
      'base_class': mtrg_b_odd[' (Cuisine)'][1],
      }
  dic['MC' + etage + ' (Toilettes)'] = {
      'comments': [],
      'turne_name': 'Toilettes',
      'available': False,
      'special': True,
      'base_style': "bottom: 30px; left: 94px;",
      'base_class': mtrg_b_odd[' (Toilettes)'][1],
      }

for num in mtrg_seven:
  turne = 'MC7' + num
  dic[turne] = {
      'comments': [],
      'turne_name': turne,
      'available': True,
      'base_style': mtrg_c_seven[num][0],
      'base_class': mtrg_c_seven[num][1]
      }

dic['MC7 (Cuisine)'] = {
    'comments': [],
    'turne_name': 'Cuisine',
    'available': False,
    'special': True,
    'base_style': mtrg_c_seven[' (Cuisine)'][0],
    'base_class': mtrg_c_seven[' (Cuisine)'][1],
    }
dic['MC7' + ' (Toilettes)'] = {
    'comments': [],
    'turne_name': 'Toilettes',
    'available': False,
    'special': True,
    'base_style': "bottom: 30px; left: 94px;",
    'base_class': mtrg_c_seven[' (Toilettes)'][1],
    }
parse_comments(dic, html_doc)

url = urllib.request.urlopen('http://www.dg.ens.fr/thurnage/2012/classement.html')
html_doc2 = BeautifulSoup(url.read().decode('utf8'))
url.close()

parse_unavail(dic, html_doc2)

def gen_row(name, etages, nums):
  html = '<div class="row" style="margin-bottom: 10px">'
  span = str(int(12 / len(etages)))
  for etage in etages:
    html += '<div class="span' + span + '">'
    html += '<div class="well" style="margin: auto; width: 240px;">'
    html += '<div style="width: 240px; height: 240px; position: relative;">'
    for num in nums:
      turne = name + etage + num
      html += mk_turne(mk_turne_infos(dic[turne]), dic[turne]['base_style'], dic[turne]['base_class'])
    html += '</div>'
    html += '<div style="width: 100%; text-align: center; margin-bottom: -10px; margin-top: 5px;">'
    html += 'Étage ' + name + etage + ' (' + str(len(nums)) + ' chambres)'
    html += '</div>'
    html += '</div></div>'
  html += '</div>'
  return html

html = """<div class="alert alert-info" style="cursor: pointer;" data-toggle="collapse" data-target="#tourB">Tour B - Montrouge
  <button class="close"><i class="icon-chevron-down"></i></button>
  </div>"""
html += '<div class="collapse turnes" id="tourB">'
html += gen_row('MB', '135', mtrg_b_odd)
html += gen_row('MB', '246', mtrg_b_even)
html += gen_row('MB', '7', mtrg_seven)
html += '</div>'

html += '''<div class="alert alert-info" style="cursor: pointer;" data-toggle="collapse" data-target="#tourC">Tour C - Montrouge
<button class="close"><i class="icon-chevron-down"></i></button>
</div>'''
html += '<div class="collapse turnes" id="tourC">'
html += gen_row('MC', '135', mtrg_b_odd)
html += gen_row('MC', '246', mtrg_b_even)
html += gen_row('MC', '7', mtrg_seven)
html += '</div>'

with open('index.html.tpl', 'r') as tpl:
  with open('index.html', 'w') as index:
    index.write(tpl.read().replace('{0}', html))

print('Done.')

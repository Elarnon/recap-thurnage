from bs4 import BeautifulSoup
import urllib.request
import re

def mk_thurne(thurne_infos, base_style, base_classes):
  s = """
  <div style="{0} background-color: {5}" class="{1} label" rel="popover" title="{2} ({6})"
  data-content="{3}">
    {2}
    <span class="badge badge-info"
          style="position: absolute; bottom: 0; right: 0">{4}</span>
  </div>
  """.format(base_style, base_classes, thurne_infos['name'], thurne_infos['comments'],
      thurne_infos['nb_comments'], thurne_infos['status_color'], thurne_infos['state'])
  return s

def mk_thurne_infos(raw):
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
  thurne_infos = {
      'name': raw['thurne_name'],
      'comments': mk_thurne_comments(raw),
      'nb_comments': nb,
      'status_color': color,
      'state': state['name']
      }
  return thurne_infos

def get_last_state(raw):
  bst = {'color': 'grey', 'name': 'État inconnu.'}
  bst_yr = 0
  for comment in raw['comments']:
    if int(comment['year']) > bst_yr:
      bst = comment['status']
      bst_yr = int(comment['year'])
  return bst

def mk_thurne_comments(raw):
  cts = ""
  for comment in raw['comments']:
    cts += "&lt;blockquote&gt;"
    for info in comment['infos']:
      cts += "&lt;span class=&quot;label&quot; style=&quot;background-color: "
      cts += info['color']
      cts += ";&quot;&gt;"
      cts += info['text']
      cts += "&lt;/span&gt;"
    cts += comment['text']
    cts += "&lt;small&gt;"
    cts += comment['author']
    cts += ", " + comment['year']
    cts += "&lt;/small&gt;&lt;/blockquote&gt;"
  return cts

def normalize_thurne_name(name):
  return name.replace(' ', '')[:5].upper()

def add_comment(dic, thurne, author, yr, state, mezza, volets, rideaux, txt):
  infos = [{'color': state['color'], 'text': state['name']}]
  if mezza:
    infos.append({'color': 'green', 'text': 'Mezzanine !'})
  if volets:
    infos.append({'color': 'green', 'text': 'Volets'})
  if rideaux:
    infos.append({'color': 'green', 'text': 'Rideaux'})
  comment = {
      'infos': infos,
      'text': txt,
      'author': author,
      'year': yr,
      'status': state,
      'infos': infos
      }
  if thurne in dic:
    dic[thurne]['comments'].append(comment)

def mk_state(state):
  if state == 'bon':
    return { 'color': 'green', 'name': 'Bon état' }
  if state == 'moyen':
    return { 'color': 'orange', 'name': 'État moyen' }
  if state == 'mauvais':
    return { 'color': 'red', 'name': 'Mauvais état' }
  if state == 'tresbon':
    return { 'color': 'darkgreen', 'name': 'Très bon état' }
  if state == 'tresmauvais':
    return { 'color': 'darkred', 'name': 'Très mauvais état' }

def parse_comments(dic, html_doc):
  tbl = html_doc.find_all('h2', text='Montrouge')[0].find_next_sibling('table')
  for child in tbl.find_all('tr'):
    tds = child.find_all('td', recursive=False)
    if tds != []:
      name = normalize_thurne_name(tds[0].string)
      author = tds[1].string
      year = tds[2].string
      state = mk_state(tds[3].find('span')['class'][0])
      mezza = tds[4].string == 'Oui'
      volets = tds[5].string == 'Oui'
      rideaux = tds[6].string == 'Oui'
      comm = tds[7].string
      add_comment(dic, name, author, year, state, mezza, volets, rideaux, comm)

def parse_unavail(dic, html_doc):
  tbl = html_doc.find_all(text=re.compile('Gardes-thurnes'))[0].parent.find_next_sibling('table')
  for child in tbl.find_all('tr'):
    tds = child.find_all('td', recursive=False)
    if tds != []:
      thurne = normalize_thurne_name(tds[2].string)
      person = tds[1].string
      dic[thurne]['available'] = False
      dic[thurne]['occupied_by'] = person

mtrg_b_even = {
    '14': ("top: 20px; left: -20px;", "thurne-h"),
    '13': ("top: 20px; left: 5px;", "thurne-h"),
    '12': ("top: 20px; left: 30px;", "thurne-h"), 
    '11': ("top: 20px; left: 55px;", "thurne-h"), 
    '10': ("top: 20px; left: 80px;", "thurne-h"),
    '09': ("top: 20px; left: 105px;", "thurne-h"),
    '08': ("top: 20px; left: 130px;", "thurne-h"),
    '07': ("top: 20px; left: 155px;", "thurne-h"),
    '18': ("bottom: 0; left: 0;", "thurne-w"),
    '17': ("bottom: 25px; left: 0;", "thurne-w"),
    '16': ("bottom: 50px; left: 0;", "thurne-w"),
    '15': ("bottom: 75px; left: 0;", "thurne-w"),
    '03': ("bottom: 0; right: 0;", "thurne-w"),
    '04': ("bottom: 25px; right: 0;", "thurne-w"),
    '05': ("bottom: 50px; right: 0;", "thurne-w"),
    '06': ("bottom: 75px; right: 0;", "thurne-w"),
  }

mtrg_b_odd = mtrg_b_even.copy()
del mtrg_b_odd['03'] # laverie

url = urllib.request.urlopen('http://www.dg.ens.fr/thurnage/EtatChambre.html')
html_doc = BeautifulSoup(url.read().decode('utf8'))
url.close()

dic = {}
for etage in "135":
  for num in mtrg_b_odd:
    thurne = 'MB' + etage + num
    dic[thurne] = {
      'comments': [],
      'thurne_name': thurne,
      'available': True,
      'base_style': mtrg_b_odd[num][0],
      'base_class': mtrg_b_odd[num][1]
      }

for etage in "246":
  for num in mtrg_b_even:
    thurne = 'MB' + etage + num
    dic[thurne] = {
        'comments': [],
        'thurne_name': thurne,
        'available': True,
        'base_style': mtrg_b_even[num][0],
        'base_class': mtrg_b_even[num][1]
        }

for etage in "135":
  for num in mtrg_b_odd:
    thurne = 'MC' + etage + num
    dic[thurne] = {
      'comments': [],
      'thurne_name': thurne,
      'available': True,
      'base_style': mtrg_b_odd[num][0],
      'base_class': mtrg_b_odd[num][1]
      }

for etage in "246":
  for num in mtrg_b_even:
    thurne = 'MC' + etage + num
    dic[thurne] = {
        'comments': [],
        'thurne_name': thurne,
        'available': True,
        'base_style': mtrg_b_even[num][0],
        'base_class': mtrg_b_even[num][1]
        }

parse_comments(dic, html_doc)

url = urllib.request.urlopen('http://www.dg.ens.fr/thurnage/2012/classement.html')
html_doc2 = BeautifulSoup(url.read().decode('utf8'))
url.close()

parse_unavail(dic, html_doc2)

html = '<div class="row">'
html += '<div class="alert alert-info">Tour B</div>'
for etage in "135":
  html += '<div class="span4">'
  html += '<div style="margin: 20px; width: 200px; height: 200px; position: relative; border: 1px solid black;">'
  for num in mtrg_b_odd:
    thurne = 'MB' + etage + num
    html += mk_thurne(mk_thurne_infos(dic[thurne]), dic[thurne]['base_style'], dic[thurne]['base_class'])
  html += '</div>'
  html += '<div class="well" style="width: 200px">' + 'Étage B' + etage + '</div>'
  html += '</div>'

html += '</div><div class="row">'

for etage in "246":
  html += '<div class="span4">'
  html += '<div style="margin: 50px; width: 200px; height: 200px; position: relative; border: 1px solid black;">'
  for num in mtrg_b_even:
    thurne = 'MB' + etage + num
    html += mk_thurne(mk_thurne_infos(dic[thurne]), dic[thurne]['base_style'], dic[thurne]['base_class'])
  html += '</div>'
  html += '<div class="well" style="width: 200px">' + 'Étage B' + etage + '</div>'
  html += '</div>'

html += '</div><div class="row">'

html += '<div class="alert alert-info">Tour C</div>'

for etage in "135":
  html += '<div class="span4">'
  html += '<div style="margin: 20px; width: 200px; height: 200px; position: relative; border: 1px solid black;">'
  for num in mtrg_b_odd:
    thurne = 'MC' + etage + num
    html += mk_thurne(mk_thurne_infos(dic[thurne]), dic[thurne]['base_style'], dic[thurne]['base_class'])
  html += '</div>'
  html += '<div class="well" style="width: 200px">' + 'Étage C' + etage + '</div>'
  html += '</div>'

html += '</div><div class="row">'

for etage in "246":
  html += '<div class="span4">'
  html += '<div style="margin: 50px; width: 200px; height: 200px; position: relative; border: 1px solid black;">'
  for num in mtrg_b_even:
    thurne = 'MC' + etage + num
    html += mk_thurne(mk_thurne_infos(dic[thurne]), dic[thurne]['base_style'], dic[thurne]['base_class'])
  html += '</div>'
  html += '<div class="well" style="width: 200px">' + 'Étage C' + etage + '</div>'
  html += '</div>'

html += '</div>'

print(html)


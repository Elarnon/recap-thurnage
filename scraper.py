from scrapy.spider import Spider
from scrapy.selector import Selector

class EtatThurnesSpider(Spider):
    name = "etat.thurnes.dg.ens"
    allowed_domains = ["dg.ens.fr"]
    start_urls = [
        "http://www.dg.ens.fr/thurnage/EtatChambre.html"
    ]

    text_fields = [ u'Ann\xe9e', u'Commentaires', u'Occupant', u'Thurne' ]
    ouinon = [ u'Rideaux', u'Volets', u'Mezza' ]
    etat = [ u'\xc9tat' ]
    renamer = {
        u'Ann\xe9e': 'year',
        u'Commentaires': 'comment',
        u'Occupant': 'owner',
        u'Thurne': 'name',
        u'Rideaux': 'shutters',
        u'Volets': 'curtains',
        u'Mezza': 'mezzanine',
        u'\xc9tat': 'state',
    }

    def parse(self, response):
        sel = Selector(response)
        attributes = sel.xpath('//tr[count(*)=8][th][1]/th/text()').extract()
        thurnes = sel.xpath('//tr[count(*)=8][td]')
        data = []
        for thurne in thurnes:
            info = { k: v for k, v in zip(attributes, thurne.xpath('td')) }
            for k in self.text_fields:
                info[k] = ''.join(info[k].xpath('text()').extract())
            for k in self.ouinon:
                span = info[k].xpath('span')
                class_ = span.xpath('@class').extract()
                if class_ == [ u'ok' ]:
                    info[k] = ''.join(span.xpath('text()').extract())
                elif class_ == [ u'notok' ]:
                    info[k] = False
                else:
                    print("FAILURE") # TODO
            for k in self.etat:
                info[k] = ''.join(info[k].xpath('span/@class').extract())
            item = ThurneComment()
            for k in info:
                item[k] = info[k]
            data.append(item)

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

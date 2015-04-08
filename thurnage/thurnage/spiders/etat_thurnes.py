from scrapy.spider import Spider
from scrapy.selector import Selector

from thurnage.items import ThurneComment

class EtatThurnesSpider(Spider):
    name = "etat_thurnes"
    allowed_domains = ["dg.ens.fr"]
    start_urls = [
        "http://www.dg.ens.fr/thurnage/EtatChambre.html"
    ]

    text_fields = [ u'Ann\xe9e', u'Commentaires', u'Occupant', u'Thurne' ]
    ouinon = [ u'Rideaux', u'Volets', u'Mezza' ]
    etat = [ u'\xc9tat' ]
    renamer = {
        u'Ann\xe9e': 'annee',
        u'Commentaires': 'commentaire',
        u'Occupant': 'occupant',
        u'Thurne': 'thurne',
        u'Rideaux': 'rideaux',
        u'Volets': 'volets',
        u'Mezza': 'mezzanine',
        u'\xc9tat': 'etat',
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
                    if k == u'Mezza':
                        info[k] = ''.join(span.xpath('text()').extract())
                    else:
                        info[k] = True
                elif class_ == [ u'notok' ]:
                    info[k] = False
                else:
                    # TODO: Error.
                    continue
            for k in self.etat:
                info[k] = ''.join(info[k].xpath('span/@class').extract())
            item = ThurneComment()
            for k in info:
                item[self.renamer[k]] = info[k]
            item['annee'] = int(item['annee'])
            yield item

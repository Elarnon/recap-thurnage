# -*- coding: utf-8 -*-
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request

from thurnage.items import Thurnage
from datetime import date

import re

class ResultatsSpider(Spider):
    name = "resultats"
    allowed_domains = ["dg.ens.fr"]

    def __init__(self, years="", *args, **kwargs):
        super(ResultatsSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            "http://www.dg.ens.fr/thurnage/{}/".format(year)
            for year in years.split(",")
        ]

    def parse(self, response):
        sel = Selector(response)
        year = int(''.join(x for x in response.url.split('/') if len(x) == 4 and x.isdigit()))
        tg = sel.xpath(u"//ul[@class='arbre']/li/a[contains(text(), 'Résultats')]/@href").extract()[0]
        tg_final = sel.xpath(u"//ul[@class='arbre']/li/a[contains(text(), 'Réattributions')]/@href").extract()[0]
        tps = [
            (int(''.join(x.xpath("text()").extract()).strip("TP")), ''.join(x.xpath("@href").extract()))
            for x in sel.xpath(u"//ul[@class='arbre']/li/a[contains(text(), 'TP')]")
        ]
        
        yield Request(response.url + '/{}'.format(tg), callback=self.parse_tg, meta={ "year": year, "final": False })
        yield Request(response.url + '/{}'.format(tg_final), callback=self.parse_tg,
                      meta={ "year": year, "final": True })

        for tp, url in tps:
            yield Request(response.url + '/{}'.format(url), callback=self.parse_tp,
                          meta={ "year": year, "tp": tp })

    def parse_tg(self, response):
        sel = Selector(response)
        year = response.meta['year']
        final = response.meta['final']
        results = sel.xpath("//h2[contains(text(), 'Choix des')]/following-sibling::table[1]/tr[td]")
        items = []
        for result in results:
            [ clt, who, thurne ] = [ ''.join(td.xpath('text()').extract()) for td in result.xpath('td')[:3] ]
            clt = int(clt)
            item = Thurnage()
            item['annee'] = year
            item['thurne'] = thurne
            who = re.sub(r"\s+", " ", who)
            if re.match(r"^\s*\([a-zA-Z]+\)\s*$", who):
                who = who.replace('(', '').replace(')', '').strip()
            else:
                who = who[:who.index('(')]
                who = who.split(' ')
                who = ' '.join(who[1:]) + who[0]
            who = re.sub(r"\s+", " ", who).strip()
            item['occupant'] = who
            item['thurnage'] = 0 if final else -1
            if not final:
                item['classement'] = clt
            yield item

    def parse_tp(self, response):
        sel = Selector(response)
        year = response.meta['year']
        tp = response.meta['tp']
        results = sel.xpath("//table[@class='result']/tr[td]")
        for result in results:
            [ who, libere, prend ] = [ ''.join(td.xpath('text()').extract()) for td in result.xpath('td')[:3] ]
            item = Thurnage()
            item['annee'] = year
            item['thurne'] = prend
            who = re.sub(r"\s+", " ", who).strip()
            item['occupant'] = who
            item['thurnage'] = tp
            if libere is not '':
                item['libere'] = libere
            yield item

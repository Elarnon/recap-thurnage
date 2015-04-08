# -*- coding: utf-8 -*-
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
import re

class ThurneNamePipeline(object):
    thurne_format = re.compile(r"^[A-Z]{2}[0-9]{,3}$")
    wrong_order = re.compile(r"^([A-Z]?[0-9]{,3})([A-Z]+)$")
    def process_item(self, item, spider):
        if 'thurne' not in item:
            return item

        name = item['thurne'].replace(' ', '').replace('-', '').replace(';', '').replace(',', '').upper()
        name = name.replace('ULM', 'U').replace('ERASME', 'E').replace('MONTROUGE', 'M').replace('JOUDAN', 'J')
        name = name.replace('JOURDAN', 'J').replace('DUNIR', 'IR').replace('NIR', 'IR').replace('JJ', 'J')
        name = name.replace('MA1', 'MA')

        if name is '':
            return item
        
        match = self.wrong_order.match(name)
        if match:
            name = '{1}{0}'.format(*match.groups())
        if self.thurne_format.match(name):
            name = '{}{:03}'.format(name[:2], int(name[2:]))
        elif re.match(r"^[ARE][0-9]{,3}$", name):
            # Les préfixes A, R, E ne sont présents qu'à Ulm
            name = 'U{}{:03}'.format(name[:1], int(name[1:]))
        else:
            match = re.match(r"^C([0-9])([0-9]{2})", name)
            if match:
                first, rest = [ int(i) for i in match.groups() ]
                if first > 3:
                    # Seul Montrouge à des étages en CXYY avec X > 3
                    name = "MC{}{:02}".format(first, rest)
                elif first == 1 and rest > 16:
                    # Seul Jourdan à des étages en C1XX avec XX > 16
                    name = "JC{}{:02}".format(first, rest)
                elif first in [ 2, 3 ] and rest > 16:
                    # Seul Ulm à des étages en C2XX et C3XX avec XX > 16
                    name = "UC{}{:02}".format(first, rest)
                elif item['mezzanine']:
                    # Seul Ulm à des mezzanines
                    name = "UC{}{:02}".format(first, rest)
                else:
                    raise DropItem("Je ne parviens pas à déterminer si cette thurne est à Ulm, Montrouge, ou Jourdan: '{}'".format(item['thurne']))
            elif re.match(r"^C[0-9]{2}$", name):
                # Seul Jourdan à des thurnes en CXX
                name = "J{}{:03}".format(name[:1], int(name[1:]))
            elif re.match(r"^[0-9]{,3}$", name) and item['mezzanine']:
                name = "UC{:03}".format(int(name))
            elif re.match(r"^[A-Z]{2}[0-9]{3}", name):
                name = name[:5]
            else:
                raise DropItem(u"Je ne comprends pas le nom de cette thurne: '{}'".format(item['thurne']))
        item['thurne'] = name
        return item

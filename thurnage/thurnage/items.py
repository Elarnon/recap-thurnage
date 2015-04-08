# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class ThurneComment(Item):
    annee = Field()
    commentaire = Field()
    occupant = Field()
    thurne = Field()
    rideaux = Field()
    volets = Field()
    mezzanine = Field()
    etat = Field()

class Thurnage(Item):
    annee = Field()
    occupant = Field()
    thurne = Field()
    thurnage = Field()
    libere = Field()
    classement = Field()

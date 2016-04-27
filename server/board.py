class Board(object):
    def __init__(self, db):
        self.db = db

    def setup(self):
        pass

    def add_territory(self, shortname, name=None, supply=False, land=True, coastal=False):
        if not name:
            name = shortname
        self.db.territory.insert({
            'shortname': shortname,
            'name': name,
            'supply': supply,
            'land': land,
            'coastal': coastal,
            'neighbors': [],
            'unit': None
        })

    def link(self, sn1, sn2):
        for (a, b) in ((sn1, sn2), (sn2, sn1)):
            self.db.territory.update_one({'shortname': a}, {
                '$addToSet': {'neighbors': b}
            })

    def set_unit(self, nation, shortname):
        self.db.territory.update_one({'shortname': shortname}, {
            '$set': {'unit': nation}
        })

    def add_nation(self, name):
        self.db.nation.insert({'name': name})

    def reset(self):
        self.db.territory.delete_many({})
        self.db.nation.delete_many({})
        self.db.game.delete_many({})
        self.db.move.delete_many({})
        self.db.log.delete_many({})

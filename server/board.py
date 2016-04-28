class Board(object):
    def __init__(self, db):
        self.db = db

    def setup(self):
        pass

    def add_territory(self, shortname, name=None, supply=False, land=True):
        if not name:
            name = shortname
        self.db.territory.insert({
            'shortname': shortname,
            'name': name,
            'supply': supply,
            'land': land,
            'coasts': {},
            'neighbors': [],
            'unit': None
        })

    def link(self, sn1, sn2):
        for (a, b) in ((sn1, sn2), (sn2, sn1)):
            updates = {'$addToSet': {'neighbors': b}}
            self.db.territory.update_one({'shortname': a}, updates)

    def linkcoast(self, sn1, sn2, coast1='default', coast2='default'):
        self.link(sn1, sn2)
        for (a, b, cname) in ((sn1, sn2, coast1), (sn2, sn1, coast2)):
            if self.is_land(a):
                # add/update coast
                if not self.db.territory.find({'shortname': a, 'coasts.'+cname: {'$exists': True}}):
                    self.db.territory.update_one({'shortname': a}, {'$set': {'coasts.'+cname: []}})
                self.db.territory.update_one({'shortname': a}, {'$addToSet': {'coasts.'+cname: b}})
            # seas have no coast, already called link so good

    def is_land(self, sn):
        return self.db.territory.find({
            'shortname': sn, 'land': True
        })

    def is_coast(self):
        pass

    def set_unit(self, nation, shortname):
        self.db.territory.update_one({'shortname': shortname}, {
            '$set': {'unit': nation}
        })

    def add_nation(self, name):
        self.db.nation.insert({'name': name})

    def add_move(self, turn, nation, order):
        # TODO: check for nation here
        self.db.move.insert({
            'turn': turn, 'nation': nation, 'order': order
        })

    def get_territory(self, shortname):
        return self.db.territory.find_one({'shortname': shortname})

    def reset(self):
        self.db.territory.delete_many({})
        self.db.nation.delete_many({})
        self.db.game.delete_many({})
        self.db.move.delete_many({})
        self.db.log.delete_many({})

    def are_adjacent(self, a, b):
        # TODO: check coastal restrictions
        return self.db.territory.find({'shortname': a, 'neighbors': b})

    def can_move_to(self, type, a, b):
        # TODO: check coastal restrictions! Esp. dual coasts
        return (
            # adjacent
            self.__are_adjacent(a, b) and (
                # army - b is land
                type == 'A' and self.db.territory.find({'shortname': b, 'land': True}) or
                # fleet - b is sea or coastal
                type == 'F' and self.db.territory.find({
                    'shortname': b,
                    '$or': {'coastal': True, 'land': False}
                })
            )
        )

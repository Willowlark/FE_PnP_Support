from random import randint



class CsvImport(object):
    def __init__(self, printhook, d):
        self.printhook = printhook
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [CsvImport(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, CsvImport(b) if isinstance(b, dict) else b if not b.isdigit() else int(b))


class Unit(CsvImport):

    header = "Name","Class","Lv","Exp","HP","Str","Mag","Skl","Spd","Luck","Def","Res","Con","Mov","Affinity",\
                      "I1","I2","I3","I4","I5","I6","I7","I8","Usable", "GHP", 'GStr', 'GMag', 'GSkl', 'GSpd', 'GLuck', \
                      'GDef', 'GRes'

    def __init__(self, printhook, d):
        super(Unit, self).__init__(printhook, d)
        self.using = None

        self.dattack = None
        self.dhit = None
        self.davd = None
        self.dcrt = None
        self.devd = None
        self.das = None

    def __str__(self):
        if self.using is not None: output = """{0}: {1}/{2}\nClass: {3} {4} ({5})\nUsing: {6}.""".format(
                self.Name, self.CHP, self.HP, self.Class, self.Lv, self.Exp, self.using.Name)
        else: output = """{0}: {1}/{2}\nClass: {3} {4} ({5}).""".format(
                self.Name, self.CHP, self.HP, self.Class, self.Lv, self.Exp)
        return output

    def __repr__(self):
        return self.writeString()

    def equipped(self, item=None):
        if item is None:
            print self.using
        else:
            self.using = item
            self.deriveStats()

    def deriveStats(self):
        if self.using is not None:
            if self.using.Physical == 'TRUE': self.dattack = self.using.Mt + self.Str
            else: self.dattack = self.using.Mt + self.Mag
            self.dhit = (self.Skl*2) + self.Luck/2 + self.using.Hit
            self.davd = self.Luck + 2*self.Spd
            self.dcrt = self.Skl/2 + self.Luck/4
            self.devd = self.Luck
            self.das = self.Spd

        else:
            self.database.standard("Has nothing to use.")

    def levelUp(self):

        if self.Exp < 100:
            print "ERROR: Not enough exp to level up!"
            return -1

        if self.Lv == 20:
            print "ERROR: Max level reached."
            return -2

        self.Lv += 1
        self.Exp = 0

        # Horrible not a good idea code yay!
        for attr, value in self.__dict__.iteritems():
            if attr in ["GHP", 'GStr', 'GMag', 'GSkl', 'GSpd', 'GLuck','GDef', 'GRes'] and value > 0:
                r = randint(1, _roundup(value))
                bonus = r/ 100 + 1
                if r < value:
                    self.__setattr__(attr[1:], self.__getattribute__(attr[1:])+bonus)
                    if attr[1:] == "HP": self.CHP += bonus
                    self.database.standard("{0} has increased by {1}!".format(attr[1:], bonus))

    def writeString(self):
        ret = [self.Name, self.Class, self.Lv, self.Exp, self.CHP, self.HP, self.Str, self.Mag, self.Skl, self.Spd,
                self.Luck, self.Def, self.Res, self.Con, self.Mov, self.Affinity, self.I1, self.I2, self.I3, self.I4,
               self.I5, self.I6, self.I7, self.I8, self.Usable, self.GHP, self.GStr, self.GMag, self.GSkl, self.GSpd,
               self.GLuck, self.GDef, self.GRes]
        return ret


class PartUnit(CsvImport):

    header = "Name","Class","Lv","CHP","HP","Def","Res","Weapon","Atk","Hit","Avd","Crt","Evd","AS","Mov"

    def __init__(self, printhook, d):
        super(PartUnit, self).__init__(printhook, d)
        self.using = None

        self.dattack = self.Atk
        self.dhit = self.Hit
        self.davd = self.Avd
        self.dcrt = self.Crt
        self.devd = self.Evd
        self.das = self.AS

        self.tryEquip()

    def __str__(self):
        output = """{0}: {1}/{2}\nClass: {3} {4}.""".format(self.Name, self.CHP, self.HP, self.Class, self.Lv)
        return output

    def __repr__(self):
        return self.writeString()

    def tryEquip(self):
        it = Item(self.printhook, {})
        it.Physical = 'TRUE'
        it.Range = 1 if not hasattr(self, 'Range') else self.Range
        self.using = it

    def writeString(self):
        #Name,Class,Lv,HP,Def,Res,Weapon,Atk,Hit,Avd,Crt,Evd,AS,Mov
        ret = [self.Name, self.Class, self.Lv, self.CHP, self.HP, self.Def, self.Res, self.Weapon, self.Atk, self.Hit,
               self.Avd, self.Crt, self.Evd, self.AS, self.Mov]
        return ret


class Enemy(Unit):
    pass


class Item(CsvImport):

    header = "Name","Mt","Hit","Crt","Weight","Range","Rank","Effect","Physical"

    def __str__(self):
        output = """{0}\nMt: {1} Crit: {2} Rng: {3}\n{4}""".format(
                self.Name, self.Mt, self.Crt, self.Range, self.Effect)
        return output

    def __repr__(self):
        return self.writeString()

    def writeString(self):
        #Name,Mt,Hit,Crt,Weight,Range,Rank,Effect,Physical
        ret = [self.Name, self.Mt, self.Hit, self.Crt, self.Weight, str(self.Range), self.Rank, self.Effect, self.Physical]
        return ret

def _roundup(x):
    return x if x % 100 == 0 else x + 100 - x % 100


strReference = {"unit":Unit, "enemy":Enemy, "item":Item, "punit":PartUnit}
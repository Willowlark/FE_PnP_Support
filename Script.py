import csv
from random import randint

global scope


class CsvImport(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [CsvImport(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, CsvImport(b) if isinstance(b, dict) else b if not b.isdigit() else int(b))


class Unit(CsvImport):

    def __init__(self, d):
        super(Unit, self).__init__(d)
        self.using = None

        self.dattack = None
        self.dhit = None
        self.davd = None
        self.dcrt = None
        self.devd = None
        self.das = None

        self.tryEquip()

    def __str__(self):
        if self.using is not None: output = """{0}: {1}/{2}\nClass: {3} {4} ({5})\nUsing: {6}.
        """.format(self.Name, self.CHP, self.HP, self.Class, self.Lv, self.Exp, self.using.Name)
        else: output = """{0}: {1}/{2}\nClass: {3} {4} ({5}).
        """.format(self.Name, self.CHP, self.HP, self.Class, self.Lv, self.Exp)
        return output

    def __repr__(self):
        return self.writeString()

    def tryEquip(self):
        global scope
        if self.I1 in scope:
            self.equipped(self.I1)

    def equipped(self, item=None):
        global scope
        if item is None:
            print self.using
        else:
            if item in scope:
                self.using = scope[item]
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
            print "Has nothing to use."

    def levelUp(self):

        # if self.Exp < 100:
        #     print "Not enough exp to level up!"
        #     return -1
        #
        # if self.Lv == 20:
        #     print "Max level reached."
        #     return -2

        self.Lv += 1
        self.Exp = 0

        # Horrible not a good idea code yay!
        for attr, value in self.__dict__.iteritems():
            if attr in ["GHP", 'GStr', 'GMag', 'GSkl', 'GSpd', 'GLuck','GDef', 'GRes']:
                r = randint(1, _roundup(value))
                bonus = r/ 100 + 1
                if r < value:
                    self.__setattr__(attr[1:], self.__getattribute__(attr[1:])+bonus)
                    if attr[1:] == "HP": self.CHP += bonus
                    print "{0} has increased by {1}!".format(attr[1:], bonus)

    def writeString(self):
        ret = [self.Name, self.Class, self.Lv, self.Exp, self.CHP, self.HP, self.Str, self.Mag, self.Skl, self.Spd,
                self.Luck, self.Def, self.Res, self.Con, self.Mov, self.Affinity, self.I1, self.I2, self.I3, self.I4,
               self.I5, self.I6, self.I7, self.I8, self.Usable, self.GHP, self.GStr, self.GMag, self.GSkl, self.GSpd,
               self.GLuck, self.GDef, self.GRes]
        return ret


class PartUnit(CsvImport):

    def __init__(self, d):
        super(PartUnit, self).__init__(d)
        self.using = None

        self.dattack = self.Atk
        self.dhit = self.Hit
        self.davd = self.Avd
        self.dcrt = self.Crt
        self.devd = self.Evd
        self.das = self.AS

        self.tryEquip()

    def __str__(self):
        output = """{0}: {1}/{2}\nClass: {3} {4}.
        """.format(self.Name, self.CHP, self.HP, self.Class, self.Lv)
        return output

    def __repr__(self):
        return self.writeString()

    def tryEquip(self):
        it = Item({})
        it.Physical = 'TRUE'
        self.using = it
        # global scope
        # if self.Weapon in scope:
        #     self.equipped(self.Weapon)

    def equipped(self, item=None):
        global scope
        if item is None:
            print self.using
        else:
            if item in scope:
                self.using = scope[item]

    def writeString(self):
        #Name,Class,Lv,HP,Def,Res,Weapon,Atk,Hit,Avd,Crt,Evd,AS,Mov
        ret = [self.Name, self.Class, self.Lv, self.CHP, self.HP, self.Def, self.Res, self.Weapon, self.Atk, self.Hit,
               self.Avd, self.Crt, self.Evd, self.AS, self.Mov]
        return ret


class Enemy(Unit):
    pass


class Item(CsvImport):

    def __str__(self):
        output = """{0}\nMt: {1} Crit: {2} Rng: {3}\n{4}
        """.format(self.Name, self.Mt, self.Crt, self.Range, self.Effect)
        return output

    def __repr__(self):
        return self.writeString()

    def writeString(self):
        #Name,Mt,Hit,Crt,Weight,Range,Rank,Effect,Physical
        ret = [self.Name, self.Mt, self.Hit, self.Crt, self.Weight, str(self.Range), self.Rank, self.Effect, self.Physical]
        return ret


def fight(command):
    global scope
    index = command.index('fights')
    attackerkey = " ".join(command[:index])
    defenderkey = " ".join(command[index+1:])
    attacker = scope[attackerkey]
    defender = scope[defenderkey]

    if attacker.using is None or defender.using is None:
        print "Someone isn't equipped"
        return -1

    # Calculate combat results
    adamage = attacker.dattack - defender.Def if defender.using.Physical == 'TRUE' else defender.Res
    aaccuracy = attacker.dhit - defender.davd
    acrt = attacker.dcrt - defender.devd
    adouble = attacker.das - defender.das >= 4

    ddamage = defender.dattack - attacker.Def if attacker.using.Physical == 'TRUE' else attacker.Res
    daccuracy = defender.dhit - attacker.davd
    dcrt = defender.dcrt - attacker.devd
    ddouble = defender.das - attacker.das >= 4

    data = [['Name', 'Damage', 'To Hit', 'Crit Chance', 'Double?'], [attacker.Name, adamage, aaccuracy, acrt, adouble],
            [defender.Name, ddamage, daccuracy, dcrt, ddouble]]
    col_width = 10  # max(len(word) for row in data for word in row) + 2  # padding
    for row in data:
        print "".join(str(word).ljust(col_width) for word in row)
    prompt = raw_input("Make the attack?> ")
    if prompt == 'y' or prompt == 'yes':

        if randint(1, 100) < daccuracy: attacker.CHP -= ddamage *2 if randint(1,100) < dcrt else ddamage
        if randint(1, 100) < aaccuracy: defender.CHP -= adamage *2 if randint(1,100) < acrt else adamage
        if ddouble:
            if randint(1, 100) < daccuracy: attacker.CHP -= ddamage *2 if randint(1,100) < dcrt else ddamage
        if adouble:
            if randint(1, 100) < aaccuracy: defender.CHP -= adamage *2 if randint(1,100) < acrt else adamage
        #do exp.


def uses(command):
    global scope
    index = command.index('uses')
    unit = " ".join(command[:index])
    item = " ".join(command[index+1:])
    scope[unit].equipped(item)


def load(command):
    global scope

    #find type
    units, items, enemies, punit, index = _flags(command)

    f = ' '.join(command[index:])

    with open(f + '.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            loadtype = _actcheck(units, items, enemies, punit)
            if loadtype is 1: scope[row["Name"]] = Unit(row)
            elif loadtype is 2: scope[row["Name"]] = Item(row)
            elif loadtype is 3: scope[row["Name"]] = Enemy(row)
            elif loadtype is 4: scope[row["Name"]] = PartUnit(row)
            else: print 'Error'


def save(command):
    global scope

    #find type
    units, items, enemies, punit, index = _flags(command)
    filepath = " ".join(command[index:])+'.csv'

    f = open(filepath, 'w')
    writer = csv.writer(f)

    uheader = "Name","Class","Lv","Exp","HP","Str","Mag","Skl","Spd","Luck","Def","Res","Con","Mov","Affinity",\
                  "I1","I2","I3","I4","I5","I6","I7","I8","Usable", "GHP", 'GStr', 'GMag', 'GSkl', 'GSpd', 'GLuck', \
                    'GDef', 'GRes'
    iheader = "Name","Mt","Hit","Crt","Weight","Range","Rank","Effect","Physical"
    puheader = "Name","Class","Lv","CHP","HP","Def","Res","Weapon","Atk","Hit","Avd","Crt","Evd","AS","Mov"
    if units or enemies: writer.writerow(uheader)
    elif items: writer.writerow(iheader)
    elif punit: writer.writerow(puheader)

    for key in scope:
        value = scope[key]
        if _actcheck(units,items,enemies,punit,value): writer.writerow(value.writeString())
    f.close()


def show(command):
    units, items, enemies, punit, _ = _flags(command)
    for key in scope:
        value = scope[key]
        if _actcheck(units,items,enemies,punit,value): print value.Name, value


def main():
    global scope
    while 1:
        try:
            command = raw_input("> ")
            command = command.split()
            if 'fights' in command:
                fight(command)
            elif 'uses' in command:
                uses(command)
            elif 'level' in command:
                scope[" ".join(command[1:])].levelUp()
            elif 'load' in command:
                load(command)
            elif 'save' in command:
                save(command)
            elif 'show' in command:
                show(command)
            elif 'help' in command:
                print "Commands are 'X fights Y', 'X uses Z', 'load type filename', 'save type filename', 'show type' & help."
                print "type can be unit (full stated characters), punit (partial units),  \n" \
                      "enemy (different group of units), and item (weapons)"
                print 'X represents a unit, punit, or enemy type. Y represents the same. Z represents a weapon.'
            else:
                if " ".join(command) in scope:
                    print scope[' '.join(command)]
                else:
                    print "Unrecognized command and nothing with that name exists."
        except KeyError:
            print "A name was spelled incorrectly. Capitalization matters."
        except IOError:
            print "A bad file name was used."


def _roundup(x):
    return x if x % 100 == 0 else x + 100 - x % 100


def _actcheck(units,items,enemies,punits,value=None):
    #Used in load, save, show.
    if (type(value) is Unit or value is None) and units: return 1
    if (type(value) is Item or value is None) and items: return 2
    if (type(value) is Enemy or value is None) and enemies: return 3
    if (type(value) is PartUnit or value is None) and punits: return 4
    return 0


def _flags(command):
    #used in load, save, show.
    units = items = enemies = punits = 0
    index = -1
    if 'unit' in command:
        units = 1
        index = command.index('unit')+1
    if 'item' in command:
        items = 1
        index = command.index('item')+1
    if 'enemy' in command:
        enemies = 1
        index = command.index('enemy')+1
    if 'punit' in command:
        punits = 1
        index = command.index('punit')+1
    return units, items, enemies, punits, index

if __name__ == "__main__":
    global scope
    scope = {}
    main()
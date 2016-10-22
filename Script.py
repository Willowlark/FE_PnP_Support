import csv
from random import randint

global scope
scope = {}
socket_interface = None

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
            _pprint("Has nothing to use.")

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
            if attr in ["GHP", 'GStr', 'GMag', 'GSkl', 'GSpd', 'GLuck','GDef', 'GRes']:
                r = randint(1, _roundup(value))
                bonus = r/ 100 + 1
                if r < value:
                    self.__setattr__(attr[1:], self.__getattribute__(attr[1:])+bonus)
                    if attr[1:] == "HP": self.CHP += bonus
                    _pprint("{0} has increased by {1}!".format(attr[1:], bonus))

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
        it.Range = 1 if not hasattr(self, 'Range') else self.Range
        self.using = it
        # global scope
        # if self.Weapon in scope:
        #     self.equipped(self.Weapon)

    def equipped(self, item=None):
        global scope
        if item is None:
            _pprint(self.using)
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

def rangedfight(command):
    command[command.index('shoots')] = 'fights'
    fight(command, 1)

def heal(command):
    global scope
    index = command.index('heals')
    attackerkey = " ".join(command[:index])
    defenderkey = " ".join(command[index+1:])
    attacker = scope[attackerkey]
    defender = scope[defenderkey]

    if attacker.using is None or defender.using is None:
        _pprint("ERROR: Someone isn't equipped")
        return -1

    healamount = attacker.using.Mt + attacker.Mag

    data = [['Name', "Hp", 'Healing', 'To Hit', 'Crit Chance', 'Double?'],
            [attacker.Name, repr(attacker.CHP)+'/'+repr(attacker.HP), healamount, 100, 0, 0],
            [defender.Name, repr(defender.CHP)+'/'+repr(defender.HP), 0, 0, 0, 0]]
    col_width = 10  # max(len(word) for row in data for word in row) + 2  # padding
    for row in data:
        _pprint("".join(str(word).ljust(col_width) for word in row))
    prompt = raw_input("Confirm the healing?> ")
    if prompt == 'y' or prompt == 'yes':
        defender.CHP += healamount
        if defender.CHP > defender.HP: defender.CHP = defender.HP
        attacker.Exp += 10
        _pprint("{0} gained {1} Exp".format(attacker.Name, 10))

def fight(command, ranged=None):
    global scope
    index = command.index('fights')
    attackerkey = " ".join(command[:index])
    defenderkey = " ".join(command[index+1:])
    attacker = scope[attackerkey]
    defender = scope[defenderkey]

    if attacker.using is None or defender.using is None:
        _pprint("ERROR: Someone isn't equipped")
        return -1

    # Calculate combat results
    adamage = attacker.dattack - defender.Def if defender.using.Physical == 'TRUE' else defender.Res
    aaccuracy = attacker.dhit - defender.davd
    acrt = attacker.dcrt - defender.devd
    adouble = attacker.das - defender.das >= 4
    astats = [adamage, aaccuracy, acrt, adouble]

    if ranged and attacker.using.Range == 1:
        _pprint("ERROR: The attacker does not have a ranged weapon. ")
        return -1

    ddamage = defender.dattack - attacker.Def if attacker.using.Physical == 'TRUE' else attacker.Res
    daccuracy = defender.dhit - attacker.davd
    dcrt = defender.dcrt - attacker.devd
    ddouble = defender.das - attacker.das >= 4
    dstats = [ddamage, daccuracy, dcrt, ddouble]

    data = [['Name', "Hp", 'Damage', 'To Hit', 'Crit Chance', 'Double?'],
            [attacker.Name, repr(attacker.CHP)+'/'+repr(attacker.HP)] + astats,
            [defender.Name, repr(defender.CHP)+'/'+repr(defender.HP)] + dstats]
    col_width = 10  # max(len(word) for row in data for word in row) + 2  # padding
    for row in data:
        _pprint("".join(str(word).ljust(col_width) for word in row))

    if socket_interface is None:
        prompt = raw_input("Make the attack?> ")
        if prompt == 'y' or prompt == 'yes': prompt = True
        else: prompt = False
    else:
        prompt = socket_interface.yn_response()

    if prompt:
        def combatCalc(attacker, defender, astats, exp=True):
            adamage, aaccuracy, acrt, adouble = astats
            if randint(1, 100) < aaccuracy:
                damresult = adamage *2 if randint(1,100) < acrt else adamage
                defender.CHP -= damresult
                _pprint("{0} does {1} damage to {2}!".format(attacker.Name, damresult, defender.Name))

                if type(attacker) is Unit and exp:
                    bonus = 10 + (max(defender.Lv, attacker.Lv) - min(defender.Lv, attacker.Lv)) \
                                         * (3 if defender.CHP > 0 else 9)
                    attacker.Exp += bonus
                    _pprint("{0} gained {1} Exp".format(attacker.Name, bonus))
            else:
                _pprint("{0} missed {1}.".format(attacker.Name, defender.Name))

        combatCalc(attacker, defender, astats)
        if not ranged or (ranged and defender.using.Range >= 2): combatCalc(defender, attacker, dstats)

        if adouble: combatCalc(attacker, defender, astats, False)
        if ddouble:
            if not ranged or (ranged and defender.using.Range >= 2): combatCalc(defender, attacker, dstats, False)



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
            else: _pprint('ERROR: A line was not loaded into an object!')


def save(command):
    global scope

    # find type
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
        if _actcheck(units,items,enemies,punit,value): _pprint(value.Name, value)

def _processcmd(command):
    global scope
    command = command.split()

    try:
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
            _pprint("Commands are 'X fights Y', 'X uses Z', 'level X', \n" \
             "'load type filename', 'save type filename', 'show type' & help.")
            _pprint('')
            _pprint("type can be unit (full stated characters), punit (partial units),  \n" \
                  "enemy (different group of units), and item (weapons)")
            _pprint('')
            _pprint(('X represents a unit, punit, or enemy type. Y represents the same. Z represents a weapon.'))
        else:
            if " ".join(command) in scope:
                _pprint(scope[' '.join(command)])
            else:
                _pprint("Unrecognized command and nothing with that name exists.")
    except KeyError:
        _pprint("A name was spelled incorrectly. Capitalization matters.")
    except IOError:
        _pprint("A bad file name was used.")


def _roundup(x):
    return x if x % 100 == 0 else x + 100 - x % 100


def _actcheck(units,items,enemies,punits,value=None):
    # Used in load, save, show.
    if (type(value) is Unit or value is None) and units: return 1
    if (type(value) is Item or value is None) and items: return 2
    if (type(value) is Enemy or value is None) and enemies: return 3
    if (type(value) is PartUnit or value is None) and punits: return 4
    return 0


def _flags(command):
    # used in load, save, show.
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

def _pprint(text):
    global socket_interface
    if socket_interface is not None:
        socket_interface.postAll(text)
    else:
        print text

if __name__ == "__main__":
    while 1:
        command = raw_input("> ")
        _processcmd(command)
from random import randint

def rangedfight(parsed):
    parsed.keyword = 'shoots'
    fight(parsed, 1)

def heal(parsed):
    global scope
    attacker = parsed.unitX
    defender = parsed.unitY

    if attacker.using is None or defender.using is None:
        printhook.standard("ERROR: Someone isn't equipped")
        return -1

    healamount = attacker.using.Mt + attacker.Mag

    data = [['Name', "Hp", 'Healing', 'To Hit', 'Crit Chance', 'Double?'],
            [attacker.Name, repr(attacker.CHP)+'/'+repr(attacker.HP), healamount, 100, 0, 0],
            [defender.Name, repr(defender.CHP)+'/'+repr(defender.HP), 0, 0, 0, 0]]
    col_width = 10  # max(len(word) for row in data for word in row) + 2  # padding
    for row in data:
        printhook.standard("".join(str(word).ljust(col_width) for word in row))

    printhook.standard("That's so nice! Are they really doing that?")
    prompt = printhook.confirm()

    if prompt:
        defender.CHP += healamount
        if defender.CHP > defender.HP: defender.CHP = defender.HP
        attacker.Exp += 10
        printhook.standard("{0} gained {1} Exp".format(attacker.Name, 10))

def fight(parsed, ranged=None):
    global scope
    attacker = parsed.unitX
    defender = parsed.unitY

    if attacker.using is None or defender.using is None:
        printhook.standard("ERROR: Someone isn't equipped")
        return -1

    # Calculate combat results
    adamage = attacker.dattack - defender.Def if defender.using.Physical == 'TRUE' else defender.Res
    aaccuracy = attacker.dhit - defender.davd
    acrt = attacker.dcrt - defender.devd
    adouble = attacker.das - defender.das >= 4
    astats = [adamage, aaccuracy, acrt, adouble]

    if ranged and attacker.using.Range == 1:
        printhook.standard("ERROR: The attacker does not have a ranged weapon. ")
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
        printhook.standard("".join(str(word).ljust(col_width) for word in row))

    printhook.standard("Make the attack?")
    prompt = printhook.confirm()

    if prompt:
        def combatCalc(attacker, defender, astats, exp=True):
            adamage, aaccuracy, acrt, adouble = astats
            if randint(1, 100) < aaccuracy:
                damresult = adamage *2 if randint(1,100) < acrt else adamage
                defender.CHP -= damresult
                printhook.standard("{0} does {1} damage to {2}!".format(attacker.Name, damresult, defender.Name))

                if hasattr(attacker, 'Exp') and exp:
                    bonus = 10 + (max(defender.Lv, attacker.Lv) - min(defender.Lv, attacker.Lv)) \
                                         * (3 if defender.CHP > 0 else 9)
                    attacker.Exp += bonus
                    printhook.standard("{0} gained {1} Exp".format(attacker.Name, bonus))
            else:
                printhook.standard("{0} missed {1}.".format(attacker.Name, defender.Name))

        combatCalc(attacker, defender, astats)
        if not ranged or (ranged and defender.using.Range >= 2): combatCalc(defender, attacker, dstats)

        if adouble: combatCalc(attacker, defender, astats, False)
        if ddouble:
            if not ranged or (ranged and defender.using.Range >= 2): combatCalc(defender, attacker, dstats, False)



def uses(parsed):
    unit = parsed.unitX
    item = parsed.item
    unit.equipped(item)


class Printhook(object):

    def standard(self, text):
        print text

    def special(self, text):
        print text

    def confirm(self):
        prompt = raw_input("Confirm?> ")
        if prompt == 'y' or prompt == 'yes': prompt = True
        else: prompt = False
        return prompt

printhook = Printhook()
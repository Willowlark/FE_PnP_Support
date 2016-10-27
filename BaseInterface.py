#parser
import GameActions
from GameActions import Printhook
import Database

class Tactician(object):

    def __init__(self, printhook):
        self.printhook = printhook

        self.database = Database.FeDB(self.printhook)

        self.valid = {'fights':GameActions.fight, 'uses':GameActions.uses, #'':self._noKeyword,
                      'save':self.database.save, 'load':self.database.load, 'show':self.database.show,
                      'help':self._help, 'shoots':GameActions.rangedfight, 'heals':GameActions.heal}

        self.templates = ['XkY', 'XkZ', 'kX', 'ktf', 'kt', 'k']

        self.validtemplates = {'fights':self.templates[0], 'shoots':self.templates[0], 'heals':self.templates[0],
                               'save':self.templates[3], 'load':self.templates[3], 'uses':self.templates[1],
                               'show':self.templates[4], 'help':self.templates[5]}

    def _help(self, _):
        self.printhook.standard("Commands are 'X fights Y', 'X uses Z', 'level X', \n" \
                "'load type filename', 'save type filename', 'show type' & help.")
        self.printhook.standard('')
        self.printhook.standard("type can be unit (full stated characters), punit (partial units),  \n" \
                "enemy (different group of units), and item (weapons)")
        self.printhook.standard('')
        self.printhook.standard(('X represents a unit, punit, or enemy type. Y represents the same. Z represents a weapon.'))

    def _noKeyword(self, command):
        self.printhook.standard(self.database.retrieve(command))

    def order(self, command):
        for keyword in self.valid:
            if keyword in command:
                parsed = self._parseCommand(command, self.validtemplates[keyword])

                try:
                    #load loadable things.
                    if parsed.unitX != "":
                        parsed.unitX = self.database.retrieve(parsed.unitX, 'X')
                    if parsed.unitY != "":
                        parsed.unitY = self.database.retrieve(parsed.unitY, 'X')
                    if parsed.item != "":
                        parsed.item = self.database.retrieve(parsed.item, 2)
                except KeyError:
                    self.printhook.standard("A key was not found in the database.")
                except AssertionError:
                    self.printhook.standard("Something was loaded as something it isn't.")

                try:
                    if parsed.keyword: self.valid[keyword](parsed)
                except KeyError:
                    self.printhook.standard("Nothing you specificed could be found.")
                except IOError:
                    self.printhook.standard("You tried to load something that doesn't exist.")
                return 0
        try:
            self._noKeyword(command)
        except KeyError:
            self.printhook.standard("Nothing you specificed could be found.")



    def _parseCommand(self, text, pattern):  # This is probably stupid.
        ipattern = 0 #index in pattern
        p = Parsed()
        for word in text.split():

            if word in self.valid: #found keyword
                p.keyword = word
                ipattern += 1
                if ipattern >= len(pattern): return p
                if pattern[ipattern] == 'k':
                    ipattern += 1
                    if ipattern >= len(pattern): return p
            elif pattern[ipattern] == 'X':
                p.unitX += ' ' + word
                p.unitX = p.unitX.strip()
            elif pattern[ipattern] == 'Y':
                p.unitY += ' ' + word
                p.unitY = p.unitY.strip()
            elif pattern[ipattern] == 'Z':
                p.item += ' ' + word
                p.item = p.item.strip()
            elif pattern[ipattern] == 't':
                p.type = word
                ipattern += 1
                if ipattern >= len(pattern): return p
            elif pattern[ipattern] == 'f':
                p.file += ' ' + word
                p.file = p.file.strip()
        return p


class Parsed(object):

    def __init__(self):
        self.keyword = ''
        self.unitX = ''
        self.unitY = ''
        self.item = ''
        self.type = ''
        self.file = ''

    def __str__(self):
        args = self.keyword, self.unitX, self.unitY, self.item, self.type, self.file
        return ' '.join(args)



if __name__ == "__main__":
    tactician = Tactician(Printhook())
    while 1:
        command = raw_input("> ")
        tactician.order(command)
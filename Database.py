import csv
import Datatypes

class FeDB(object):

    def __init__(self, printhook):
        self.scope = {}
        self.printhook = printhook


    def load(self,parsed):

        with open(parsed.file + '.csv') as csvfile:
            reader = csv.DictReader(csvfile)
            datatype = Datatypes.strReference[parsed.type]
            for row in reader:
                self.scope[row["Name"]] = datatype(self.printhook, row)
            if datatype == Datatypes.Unit:
                self.autoequip()


    def save(self, parsed):
        f = open(parsed.file, 'w')
        writer = csv.writer(f)

        datatype = Datatypes.strReference[parsed.type]
        writer.writerow(datatype.header)

        for key in self.scope:
            value = self.scope[key]
            if type(value) == datatype: writer.writerow(value.writeString())
        f.close()


    def show(self, parsed):
        datatype = Datatypes.strReference[parsed.type]
        for key in self.scope:
            value = self.scope[key]
            if type(value) == datatype: self.printhook.standard(value.Name)

    def autoequip(self):
        for key in self.scope:
            value = self.scope[key]
            if type(value) == Datatypes.Unit:
                if value.I1 in self.scope:
                    value.equipped(self.scope[value.I1])

    def retrieve(self, key, assertion=0):
        """retrieve key from databse. Assertion is for internal use, to confirm what's being retrieved."""
        value = self.scope[key]
        if assertion == 1: assert type(value) == Datatypes.Unit
        if assertion == 2: assert type(value) == Datatypes.Item
        if assertion == 3: assert type(value) == Datatypes.Enemy
        if assertion == 4: assert type(value) == Datatypes.PartUnit
        if assertion == 'X': assert type(value) != Datatypes.Item
        return value
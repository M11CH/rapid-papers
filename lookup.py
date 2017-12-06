#!/usr/bin/env python3


# Copyright 2017 Michal Zarnowski
#
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. 
# 
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License 
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import csv 

class Lookup():

    results = []
    
    def __init__(self):
        # open file
        filename = "items.csv"
        f = open(filename, 'r')

        # read item list
        r = csv.reader(f)
        items, itemblobs = self.readcsv(r)
        self.items = items
        self.itemblobs = itemblobs

    def readcsv(self, r):
        items = []
        itemblobs = []
        for line in r:
            upc = line[0]
            desc = line[1]
            rprice = line[2]
            cprice = line[3]

            items.append([upc,desc,rprice,cprice])
            itemblobs.append(upc+desc)
        return items, itemblobs

    def readinput(self, userinput):
        inp = userinput

        self.grep(inp)

    # match items in CSV with user input, pass in list format
    def grep(self, inp):
        indicies = [] # list of match indicies
    
        for x in process.extract(inp, self.itemblobs, limit=10, scorer=fuzz.partial_ratio):
            i = self.itemblobs.index(x[0])
            indicies.append(i)
        self.storeresults(indicies)

    def storeresults(self, indicies):
        products = []

        for i in indicies:
            desc = self.items[i][1] # description = second column in csv
            retail = self.items[i][2] # retail price = third column in csv
            contractor = self.items[i][3] # contractor price = fourth column in csv

            products.append(desc)

        Lookup.results.clear()
        Lookup.results.extend(products)
            
    def returnvalues(self):
        return Lookup.results

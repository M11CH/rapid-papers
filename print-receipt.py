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

import MySQLdb as sql
from escpos import printer
import getpass

## connet to db

#prepare the cursor
cur = db.cursor()

cur.execute("SELECT * FROM SalesReceipts;")
data = cur.fetchall()

for row in data:
    saleNo = str(row[0])
    date = str(row[1])
    total = str(row[2])
    numItems = str(row[3])
    custName = row[4]
    custAdd = ""
    if row[5] is not None:
        custAdd = row[5]
    custPhone = ""
    if row[6] is not None:
        custPhone = row[6]
    soldBy = row[7]
    paymentMethod = row[8]

#printing
p = printer.Network("") ## insert IP
#p.close()
#p.open()
p.image("") ## insert logo
p.text("\n"*2)
p.text("Sale no:"+saleNo)
p.text(" "*25 + date + "\n"*2)
p.text("Sold to: " + custName + "\n"*2)
p.text("TEST PRODUCT \n"*5)
p.text("\n")
p.text("Total: $" + total + "\n")
p.text("Payment method: " + paymentMethod + "\n")
p.text("Sold by: " + soldBy + "\n")

p.text("\n"*5)
p.cut(mode="PART")




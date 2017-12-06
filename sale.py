
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


import datetime
from escpos import printer
import MySQLdb as sql
import config

class Sale():
    def __init__(self, salesman, customer, items, paymethod, subtotal, taxes, total):
        self.salesman = salesman
        self.customer = customer
        self.items = items
        self.paymethod = paymethod
        self.subtotal = subtotal
        self.taxes = taxes
        self.total = total
        self.date = datetime.datetime.now().strftime("%Y-%m-%d")

    def insertintodb(self):
        # open connection
        db = sql.connect(config.DBHOST,
                         config.DBUSER,
                         config.DBPASS,
                         config.DBNAME)

        # prepare the cursor
        cur = db.cursor()

        count = 0
        products = ""
        itemlist = []
        for item in self.items:
            itemlist.append(item["DESC"])
            products += "(LAST_INSERT_ID(), %s),"
            count += 1
        # replacing last ',' in the statement wiht ';'
        products = products[:-1]
        products += ";"

        salesreceipt = {
            "Date" : str(self.date),
            "Total" :str(self.total),
            "NumItems" : str(count),
            "CustName" : self.customer,
            "CustAddress" : "",
            "CustPhone" : "9056159700",
            "SoldBy" : self.salesman,
            "PaymentMethod" : self.paymethod
            }

        saleparams = tuple(salesreceipt.values())
        productparams = tuple(itemlist)
        
        sqlstatement = """ 
        INSERT INTO SalesReceipts 
        (Date, Total, NumItems, CustName, CustAddress, CustPhone, SoldBy, PaymentMethod) 
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s);"""
        cur.execute(sqlstatement, saleparams)
        
        sqlstatement = "INSERT INTO ProductSales (SaleNo, Product) VALUES"+ products 
        cur.execute(sqlstatement, productparams)

        sqlstatement = "SELECT LAST_INSERT_ID() FROM SalesReceipts;"
        saleid = cur.execute(sqlstatement)
        
        cur.close()
        db.commit()        
        
        db.close()

        return saleid

    def rprint(self, saleid):
        
        p = printer.Network("") ## insert ip

        # company and customer data
        p.image("", high_density_vertical=True, high_density_horizontal=True, impl="bitImageRaster",
                      fragment_height=10060, center=True) ##insert logo
        p.set(u'center')
        p.text("") ## insert address
        p.ln()
        p.text("PHONE FAX") ## insert phone numbers
        p.ln()
        p.text("") ## insert email
        p.ln()
        p.text("") ## insert website
        p.ln(count=3)
        p.set(u'left')
        p.text("SALE NO.: " + str(saleid))
        p.text(" " * (28-(len(str(saleid)))))
        p.text(self.date)
        p.ln(count=3)
        p.text("SERVED BY: " + self.salesman)
        p.ln()
        p.text("SOLD TO: " + self.customer)
        p.ln(count=2)
        p.text(("-" * 48) + "\n")

        # products
        for item in self.items:
            p.set(u'left')
            p.text(item["CODE"])
            whitespace = 47 - len(item["CODE"]) - len(item["DESC"])
            p.text(" " * whitespace)
            p.text(item["DESC"] + "\n")
            p.set(u'right')
            p.text(item["QTY"] + " @ ")
            p.text("$" + item["RATE"] + " = ")
            p.text("$" + item["TOTAL"] + "\n")
            p.text(("-" * 48) + "\n")
        p.ln(count=2)

        # aligning totals
        subspace = 1
        taxspace = 1
        totspace = 1
        if len(self.total) != len(self.subtotal):
            subspace += (len(self.total) - len(self.subtotal))
        if len(self.taxes) == len(self.subtotal):
            taxspace = subspace
        else:
            taxspace += (len(self.subtotal) - len(self.taxes)) 
            
        p.set(u'right')
        p.text("SUBTOTAL:" + " " * subspace + "$" + str(self.subtotal))
        p.ln(count=1)
        p.text("SALES TAX TOTAL:" + " " * taxspace + "$" + str(self.taxes))
        p.ln(count=1)
        p.text("TRANSACTION TOTAL:" + " " * totspace + "$" + str(self.total))
        p.ln(count=2)
        p.text("PAYMENT METHOD: " + self.paymethod)
        p.ln(count=1)

        # disclaimer
        p.set(u'center')
        p.text('\n'*3)
        p.text('') ## insert return policy
        p.ln(count=4)

        # barcode
        saleid = (12 - len(str(saleid))) * "0" + str(saleid)
        p.barcode(saleid, 'UPC-A', width=5, function_type='A')
        p.ln(count=3)
        p.cut(mode="PART")
        p.close()


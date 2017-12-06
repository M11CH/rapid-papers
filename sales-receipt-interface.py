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


import curses
import sys
from sale import Sale
from windows import Swindow, Sinit
from lookup import Lookup

# reset screen and windows after receipt has been printed
def resetinterface():
    global activewin
    global addedlines
    
    for win in wins + nawins:
        win.serase()
        win.saddvalue("")

    for i in range(addedlines):
        delline()
        
    activewin = 0
    addedlines = 0
    wins[0].smove()
    wins[0].srefresh()

def refreshwindows():
    for win in wins:
        win.srefresh()
    for win in nawins:
        win.srefresh()

def addline():
    global wins
    global addedlines
    
    if addedlines < 35:
        addedlines += 1
        newy = 12 + addedlines
        if addedlines % 2 == 0:
            newline = [Swindow(newy, 1, 1, addwinwidths[0], 2),
                       Swindow(newy, 1 + widths[2], 1, addwinwidths[1], 2),
                       Swindow(newy, (1 + widths[2] + widths[3]), 1, addwinwidths[2], 2),
                       Swindow(newy, (maxx-widths[6]-widths[5]), 1, addwinwidths[3], 2),
                       Swindow(newy, maxx-widths[6], 1, addwinwidths[4], 2)]
        else:
            newline = [Swindow(newy, 1, 1, addwinwidths[0], 3),
                       Swindow(newy, 1 + widths[2], 1, addwinwidths[1], 3),
                       Swindow(newy, (1 + widths[2] + widths[3]), 1, addwinwidths[2], 3),
                       Swindow(newy, (maxx-widths[6]-widths[5]), 1, addwinwidths[3], 3),
                       Swindow(newy, maxx-widths[6], 1, addwinwidths[4], 3)]

        for win in newline:
            win.srefresh()

        wins.extend(newline)

def delline():
    global wins
    global addedlines

    for i in range(5):
        win = wins.pop()
        win.serase()
        win.srefresh()
        win.sdelete()
        del win
    stdscr.refresh()
    addedlines -= 1

# populate subtotal, taxes, total fields on user screen
def calculatetotals():
    global subtotal
    global taxes
    global total
    
    subtotal = 0.00
    for i in range(6, len(wins), 5): # return values from each existing line total field
        linetotal = wins[i].sgetcontents()
        if len(linetotal) > 0:
            subtotal += float(linetotal)

    taxes = (subtotal * 1.13) - subtotal
    total = subtotal + taxes
    subtotal = "%.2f" % subtotal
    taxes = "%.2f" % taxes
    total = "%.2f" % total

    nawins[1].saddvalue(subtotal)
    nawins[2].saddvalue(taxes)
    nawins[3].saddvalue(total)

    # return cursor to original position
    if activewin != 999:
        wins[activewin].smove()
        wins[activewin].srefresh()
    else:
        nawins[0].smove()
        nawins[0].srefresh()

# calculate and input line total
def calculatelinetotal(i, qty, rate):
    linetotal = float(rate) * float(qty)
    linetotal = "%.2f" %  float(linetotal) # 2 decimal points
    wins[i+1].saddvalue(linetotal)

    calculatetotals()
        
# check if a value has been entered into rate and qty windows after
# each move, if so, calculate item line totals
def checktotals():
   for  i in range(5, len(wins), 5):
        qty = wins[i-3].sgetcontents()
        rate = wins[i].sgetcontents()
        if len(qty) > 0 and len(rate) > 0:
            calculatelinetotal(i, qty, rate)

def readmove(c):
    global wins
    global activewin
    
    enter = [curses.KEY_ENTER, 10, 13]
    
    if c == curses.KEY_UP:
        # if cursor is in first item line, move to first window
        if 1 < activewin <= 6 or activewin == 999:
            wins[0].smove()
            wins[0].srefresh()
            activewin = 0
        # if cursor is in any item line apart from first, move up 1
        # line and erase current line
        elif activewin > 6:
            # if item line not populated, delete line
            result = list(map(Swindow.sgetcontents, wins[-5:]))
            if all(not(x) for x in result):
                delline()
                activewin = (len(wins)-5)
            else:
                activewin = activewin - 5
            wins[activewin].smove()
            wins[activewin].srefresh()

    elif c == curses.KEY_DOWN:
        # if cursor is in salesman or customer window, move to qty
        # window in first item line
        if activewin == 0 or activewin == 1:
            wins[2].smove()
            wins[2].srefresh()
            activewin = 2
        # if cursor is in any of the item line windows
        elif 999 > activewin > 1:
            result = list(map(Swindow.sgetcontents, wins[-5:]))
            # if item line below exists, move down to that line
            if (activewin + 5) <= (len(wins)-1):
                wins[(activewin + 5)].smove()
                wins[(activewin + 5)].srefresh()
                activewin = (activewin + 5)
            # otherwise create new item line
            elif any(x for x in result):
                addline()
                wins[(len(wins)-5)].smove()
                wins[(len(wins)-5)].srefresh()
                activewin = len(wins)-5
                
    elif c == curses.KEY_RIGHT or c == ord('\t'):
        if activewin != 999:
            # if a window is available to the right of current one
            if activewin and (activewin + 1) <= (len(wins)-1):
                # if window to the right is not line total, move there
                if activewin % 5 != 0:
                    activewin += 1
                    wins[activewin].smove()
                    wins[activewin].srefresh()
                # otherwise skip window and move to next available
                else:
                    result = list(map(Swindow.sgetcontents, wins[-5:]))
                    # if next line exists
                    if (activewin + 2) <= (len(wins)-1):
                        activewin += 2
                        wins[activewin].smove()
                        wins[activewin].srefresh()
                    elif any(x for x in result):
                        addline()
                        wins[(len(wins)-5)].smove()
                        wins[(len(wins)-5)].srefresh()
                        activewin = len(wins)-5
            else:
                activewin += 1
                wins[activewin].smove()
                wins[activewin].srefresh()
            
                    
    elif c == curses.KEY_LEFT:
        # if a window is available to the left of current one
        if 999 > activewin > 0:
            # if window to the left is not line total, move there
            if activewin > 6:
                if (activewin - 2) % 5 != 0:
                    activewin -= 1
                    wins[activewin].smove()
                    wins[activewin].srefresh()
                # otherwise skip window and move to next available
                else:
                    # if item line not populated, delete line
                    result = list(map(Swindow.sgetcontents, wins[-5:]))
                    if all(not(x) for x in result):
                        delline()
                    activewin -= 2
                    wins[activewin].smove()
                    wins[activewin].srefresh()
            else:
                activewin -= 1
                wins[activewin].smove()
                wins[activewin].srefresh()
    
    elif c in enter:
        nawins[0].smove()
        nawins[0].srefresh()
        activewin = 999 # special payment method window indicator

    checktotals()

def lookup():
    # co-ordinates and dimesnsions for lookup interface
    # ypos always 1 below current window
    ypos = int((activewin / 5) + 13)
    xpos = int(widths[2] + 1)
    lookupwidth = int(widths[3] + widths[4])
    lookupheight = 15

    # create lookup interface
    lookupwin = Swindow(ypos, xpos, lookupheight, lookupwidth, 4)

    # return products matching user input
    lookup = Lookup()
    userinput = wins[activewin].sgetcontents()
    if userinput:
        lookup.readinput(userinput)
        lookupresults = lookup.returnvalues()

        # enter lookup results into lookup interface
        lookupwin.sadditems(lookupresults)
        wins[activewin].smove()
        wins[activewin].srefresh()
        
# print user input to current occupied window
def addc(c, position):
    position.saddchar(c)

# store data from the screen for printing
def storedata():
    global wins
    global nawins
    
    saleswin = wins.pop(0)
    custwin = wins.pop(0)
    
    SALESMAN = saleswin.sgetcontents().upper()
    CUSTOMER = custwin.sgetcontents().upper()
    PAYMETHOD = nawins[0].sgetcontents().upper()

    ITEMS = [] # a list of dicts

    # dice the list into sets of 5
    itemblock = [wins[x:x+5] for x in range(0, len(wins), 5)]
    for line in itemblock:
        itemattributes = ["QTY", "CODE", "DESC", "RATE", "TOTAL"]
        item = {}
        for attribute in itemattributes:
            item.update({attribute : line.pop(0).sgetcontents().upper()})
        
        ITEMS.append(item)

    wins.insert(0,custwin)
    wins.insert(0,saleswin)

    r = Sale(SALESMAN, CUSTOMER, ITEMS, PAYMETHOD, subtotal, taxes, total)
    saleid = r.insertintodb()
    r.rprint(saleid)
    resetinterface()
    del r

def backspace(position):
    position.sdelchar()

def readkey(c):
    global activewin
    movekeys = [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_RIGHT, curses.KEY_LEFT, curses.KEY_ENTER, 10, 13, ord('\t')]
    backspacekey = [curses.KEY_BACKSPACE, 8]

    # determine window to modify string
    if activewin != 999:
        position = wins[activewin]
    else:
        position = nawins[0]

    # check key
    if c in movekeys:
         readmove(c)

    # ALT
    elif c == 27: 
        stdscr.nodelay(True)
        c2 = stdscr.getch()
        if c2 == ord('q'): # ALT+Q -> exit
            sys.exit()

    elif c == curses.KEY_F1: 
        storedata()

    elif c in backspacekey:
        backspace(position)
        # initialise look-up window if in code or desc window
        if activewin % 5 == 3 or activewin % 5 == 4:
            lookup()

    else:
        addc(c, position)
        # initialise look-up window if in code or desc window
        if activewin % 5 == 3 or activewin % 5 == 4:
            lookup()
        
def main(stdscr): 
    stdscr.refresh()
    refreshwindows()
    wins[0].srestartcursor()
    wins[0].srefresh()
    while True:
        c = stdscr.getch()
        readkey(c)

init = Sinit()
stdscr = init.sinitscr()
init.sinitcolor()
maxy, maxx, widths, nawidths, addwinwidths = init.sinitsizes(stdscr)
init.sinitlabels(stdscr, maxy, maxx, widths, nawidths, addwinwidths)
wins, nawins = init.sinitwindows(maxx, maxy, widths, nawidths)

activewin = 0 # cursor location(window number)
addedlines = 0 # number of added item lines

# receipt totals
subtotal = 0.00
taxes = 0.00
total = 0.00

curses.curs_set(1)
curses.wrapper(main)
curses.endwin()

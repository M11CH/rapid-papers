
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
import re

class Sinit():

    def sinitscr(self):
        return curses.initscr()
        
    def sinitcolor(self):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(2, 255, 236)
        curses.init_pair(3, 255, 234)
        curses.init_pair(4, 255, 232)

    # get the seizes of the screen/windows
    def sinitsizes(self, stdscr):
        widths = [] # widths for accessible windows
        nawidths = [] # widths for locked windows
        addwinwidths = [] # widths for additional windows
    
        maxy,maxx = stdscr.getmaxyx()

        salesmanwinwidth = 15
        customerwinwidth = 25
        codewinwidth = int((maxx/3)/2)
        qtywinwidth = int(codewinwidth/3)
        ratewinwidth = qtywinwidth
        totalwinwidth = ratewinwidth
        descwinwidth = int(maxx-qtywinwidth-codewinwidth-ratewinwidth-totalwinwidth-1)

        pmethodwinwidth = qtywinwidth
        subtwinwidth = totalwinwidth
        taxwinwidth = totalwinwidth
    
        widths.extend([salesmanwinwidth, customerwinwidth, qtywinwidth, codewinwidth,
                       descwinwidth, ratewinwidth, totalwinwidth])

        nawidths.extend([pmethodwinwidth,
                         subtwinwidth, taxwinwidth, totalwinwidth])
        
        addwinwidths.extend([qtywinwidth, codewinwidth,
                             descwinwidth, ratewinwidth, totalwinwidth])
                   
        return maxy, maxx, widths, nawidths, addwinwidths

    def sinitlabels(self, stdscr, maxy, maxx, widths, nawidths, addwinwidths):
        stdscr.addstr(2, 1, "SALESMAN")
        stdscr.addstr(2, 31, "SOLD TO")
            
        stdscr.addstr(10, 1, "QTY")
        stdscr.addstr(10, 1 + widths[2], "ITEM CODE")
        stdscr.addstr(10, (1 + widths[2] + widths[3]), "ITEM DESCRIPTION")
        stdscr.addstr(10, (maxx - widths[6] - widths[5]), "RATE")
        stdscr.addstr(10, maxx - widths[6], "TOTAL")

        stdscr.addstr(maxy - 11, 1, "PAYMENT METHOD")
        stdscr.addstr(maxy - 11, maxx - widths[6], "SUBTOTAL")
        stdscr.addstr(maxy - 7, maxx - widths[6], "TAXES")
        stdscr.addstr(maxy - 3, maxx - widths[6], "TOTAL")

    def sinitwindows(self, maxx, maxy, widths, nawidths):
        accesswins = [] # accessible windows
        noaccesswins = [] # locked windows

        salesmanwin = Swindow(4, 1, 1, widths[0], 2)
        customerwin = Swindow(4, 31, 1, widths[1], 2)
        qtywin = Swindow(12, 1, 1, widths[2], 2)
        codewin = Swindow(12, 1 + widths[2], 1, widths[3], 2)
        descwin = Swindow(12, (1 + widths[2] + widths[3]), 1, widths[4], 2)
        ratewin = Swindow(12, (maxx - widths[6] - widths[5]), 1, widths[5], 2)
        linetotalwin = Swindow(12, maxx - widths[6], 1, widths[6], 2)

        pmethodwin = Swindow(maxy - 9, 1, 1, nawidths[0], 2)
        subtwin = Swindow(maxy - 10, maxx - widths[6], 1, nawidths[1], 2)
        taxwin = Swindow(maxy - 6, maxx - widths[6], 1, nawidths[2], 2)
        totalwin = Swindow( maxy - 2, maxx - widths[6], 1, nawidths[3], 2)

        accesswins.extend([salesmanwin, customerwin, qtywin, codewin,
                           descwin, ratewin, linetotalwin])
        noaccesswins.extend([pmethodwin, subtwin,
                             taxwin, totalwin])
        
        return accesswins, noaccesswins

class Swindow():

    def __init__(self, ypos, xpos, height, width, bg):
        self.win = curses.newwin(height, width, ypos, xpos)
        self.win.addstr(0, 0, " " * (width-1),
                        curses.color_pair(bg)) # shading
        self.ypos = ypos
        self.xpos = xpos
        self.height = height
        self.width = width
        self.bg = bg

    def srefresh(self):
        self.win.refresh()

    def srestartcursor(self):
        self.win.move(0, 0)

    def sgetcontents(self):
        contents = self.win.instr(0, 0).strip().decode("utf-8")
        return contents

    def saddchar(self, c):
        # check if new char will fit
        contents = self.sgetcontents()
        if len(contents) + 1 < self.width:
            self.win.move(0, len(contents))
            #self.win.addstr(re.escape(chr(c)), curses.color_pair(self.bg))
            self.win.addstr(chr(c), curses.color_pair(self.bg))
            self.srefresh()

    def sdelchar(self):
        contents = self.sgetcontents()
        if len(contents) > 0:
            self.win.addstr(0, 0, " " * (self.width-1),
                            curses.color_pair(self.bg)) # shading
            contents = contents[:-1]
            self.win.addstr(0, 0, contents, curses.color_pair(self.bg))
            self.srefresh()

    def saddvalue(self, value):
        self.serase()
        self.win.addstr(0, 0, " " * (self.width-1),
                        curses.color_pair(self.bg)) # shading
        self.win.addstr(0, 0, value, curses.color_pair(self.bg))
        self.srefresh()

    def sadditems(self, items):
        self.serase()
        self.win.move(0, 0)
        for item in items:
            self.win.addstr(item + "\n")
        self.srefresh()

    def smove(self):
        contents = self.sgetcontents()
        if contents:
            self.win.move(0, len(contents))
        else:
            self.win.move(0, 0)

    def serase(self):
        self.win.erase()

    def sdelete(self):
        del self.win

# -*- coding: utf-8 -*-
"""
via.
https://gist.github.com/abishur/2482046
https://github.com/LyleScott/Python-curses-Scrolling-Example/blob/master/curses_scrolling.py
"""

import curses
import os


class Menu:
    db = None
    screen = None

    SPACE_KEY = 32
    ESC_KEY = 27

    output_format = '{idx} - {key}: {value}'
    output_list = []

    def __init__(self, db, current_node):
        self.db = db
        self.current_node = current_node
        self.after = None
        self.selected_address = None
        self.running = False

        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        self.screen.keypad(1)
        self.screen.border(0)

        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        self.text_normal = curses.A_NORMAL
        self.text_highlight = curses.color_pair(1)

        self.title_size = 5

        self.top_line_idx = 0
        self.current_line_idx = 0
        self.output_list = []
        self.output_list_length = 0

        self.define_output_list()
        self.run()

    def run(self):
        self.running = True
        try:
            while self.running:
                self.draw()
                c = self.screen.getch()
                self.key_hook(c)

        except KeyboardInterrupt:
            self.close()

    def define_output_list(self):
        self.output_list = self.db['address_list']
        self.output_list.insert(0, ('New Mac Address', ''))
        self.output_list.append(('Exit', ''))
        self.output_list_length = len(self.output_list)

    def draw(self):
        self.screen.erase()
        self.draw_title()

        top = self.top_line_idx
        bottom = top + curses.LINES - self.title_size - 1

        for idx, (key, value) in enumerate(self.output_list[top:bottom]):
            line_num = self.top_line_idx + idx
            if line_num == self.current_line_idx:
                text_style = self.text_highlight
            else:
                text_style = self.text_normal

            if value == self.current_node:
                value += ' (now)'

            self.screen.addstr(idx + self.title_size, 4, self.output_format.format(idx=format(line_num, '03'),
                                                                                   key=key,
                                                                                   value=value), text_style)

        self.screen.refresh()

    def draw_title(self):
        self.screen.addstr(1, 2, 'MSwitcher - Mac Address Switcher, by @jeyraof', curses.A_STANDOUT)
        self.screen.addstr(3, 2, 'Please select an mac address...', curses.A_BOLD)

    def key_hook(self, c):
        if c == curses.KEY_UP:
            if self.current_line_idx > 0:
                self.current_line_idx -= 1

            if self.current_line_idx == self.top_line_idx and self.top_line_idx > 0:
                self.top_line_idx -= 1

        elif c == curses.KEY_DOWN:
            if self.current_line_idx + 1 < self.output_list_length:
                self.current_line_idx += 1

            bottom = self.top_line_idx + curses.LINES - self.title_size - 1
            if self.current_line_idx == bottom and bottom < self.output_list_length:
                self.top_line_idx += 1

        elif c == self.SPACE_KEY or c == ord('\n'):
            skey, sval = self.output_list[self.current_line_idx]
            if skey == 'New Mac Address' and sval == '':
                self.after = 'new'
            elif skey == 'Exit' and sval == '':
                self.after = 'exit'
            else:
                self.after = 'switch'
                self.selected_address = sval

            self.close()

        elif c == 27:
            self.close()

    def close(self):
        self.running = False
        self.screen.clear()
        curses.initscr()
        curses.nocbreak()
        curses.echo()
        curses.endwin()

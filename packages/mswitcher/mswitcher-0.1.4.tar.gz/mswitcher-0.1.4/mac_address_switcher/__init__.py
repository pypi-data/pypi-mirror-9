#!/usr/bin/python
# -*- coding: utf-8 -*-

from .helpers import (user_is_root, yes_or_no, relaunch_with_sudo,
                      load_db, initialize,
                      get_current_node,
                      switch_address, new_address_on_db)
from .menu import Menu


def switch():
    # Sudo check
    if not user_is_root():
        if yes_or_no('Please launch with sudo, re-launch now?', default=True):
            relaunch_with_sudo()
        else:
            exit()

    # Load DB
    db = load_db()

    # Draw menu
    m = Menu(db=db, current_node=get_current_node())
    if m.after == 'new':
        new_address_on_db(db)
        db.close()

    elif m.after == 'exit':
        exit()

    elif m.after == 'switch':
        switch_address(m.selected_address)

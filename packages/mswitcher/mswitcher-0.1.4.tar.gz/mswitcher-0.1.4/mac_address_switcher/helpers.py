# -*- coding: utf-8 -*-
import os
import shelve
import sys
import uuid

from . import constants


def user_is_root():
    return os.getuid() == 0


def yes_or_no(message, default=True):
    prompt = ' [y/N] ' if not default else ' [Y/n] '
    valid_inputs = {'yes': True, 'y': True,
                    'no': False, 'n': False}

    while 1:
        sys.stdout.write(message + prompt)
        answer = raw_input().strip().lower()

        if answer == '':
            return default

        elif answer in valid_inputs.keys():
            return valid_inputs.get(answer)

        else:
            sys.stderr.write('Incorrect input {input}.\n'.format(input=answer))


def relaunch_with_sudo():
    os.execvp("sudo", ["sudo"] + sys.argv)


def initialize(dbm):
    dbm['Original'] = get_current_node()
    dbm['address_list'] = []
    dbm.sync()
    return dbm


def load_db():
    dbm = shelve.open(constants.DB_FILE)
    if not dbm:
        dbm = initialize(dbm)
    return dbm


def get_current_node():
    node = uuid.getnode()
    hex_node = hex(node)
    particle_size = 2
    hex_list = [hex_node[j:j+particle_size].capitalize() for j in range(2, len(hex_node), particle_size)]
    return u':'.join(hex_list)


def switch_address(address):
    os.system('sudo ifconfig en0 ether {address}'.format(address=address))
    os.system("sudo ifconfig en0 down")
    os.system("sudo ifconfig en0 up")
    os.system("sudo ifconfig en0")


def new_address_on_db(dbm):
    sys.stdout.write('New Mac Address\n')
    sys.stdout.write(' Name: ')
    key = raw_input().strip()
    sys.stdout.write(' Mac Address: ')
    val = raw_input().strip()
    address_list = dbm['address_list']
    address_list.append((key, val))
    dbm['address_list'] = address_list


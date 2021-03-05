#!/usr/bin/env python3


__author__ = "Ely Miranda"
__version__ = "1.4.0"
__license__ = "MIT"

'''
CHANGELOG:
* Modifications to remove UI and be CLI only.
* Fix for issue where Settings UI window did not fit on smaller resolution screens.
    The window is now re-sizeable and scrolling is enabled.
* Augmented the suffix and prefix functionality. The Artist and Song data chunks now
    can have independent suffixes and prefixes.
* Added version number to Settings window title bar.
'''

import requests
import configparser
from threading import Thread
from polling2 import poll
from lxml import html
from time import sleep, time
import os
import sys

# define global variables
ini = paused = 0
track = ''
config_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "bin/config.ini"))
ico = os.path.abspath(os.path.join(os.path.dirname(__file__), "bin/icon.ico"))

# create needed object instances
config = configparser.ConfigParser()

class ConfigFile:  # read and write to config.ini
    def __init__(self, cparser, cfile):
        self.cparser = cparser
        self.cfile = cfile

        try:
            self.cparser.read(self.cfile)
            self.cparser.sections()

            self.local = is_bool(config.get('Settings', 'local'))
            self.libpath = config.get('Settings', 'libpath')
            self.url = config.get('Settings', 'url')
            self.file = config.get('Settings', 'file')
            self.interval = config.get('Settings', 'interval')
            self.delay = config.get('Settings', 'delay')
            self.multi = is_bool(config.get('Settings', 'multi'))
            self.quote = is_bool(config.get('Settings', 'quote'))
            self.a_pref = config.get('Settings', 'a_pref').replace("|_0", " ")
            self.a_suff = config.get('Settings', 'a_suff').replace("|_0", " ")
            self.s_pref = config.get('Settings', 's_pref').replace("|_0", " ")
            self.s_suff = config.get('Settings', 's_suff').replace("|_0", " ")
            self.notif = is_bool(config.get('Settings', 'notif'))

            if is_number(self.interval) is False:
                self.interval = 10
            if is_number(self.delay) is False:
                self.delay = 0

            self.interval = float(self.interval)
            self.delay = float(self.delay)
        except configparser.NoOptionError:
            print("fuck my life")
            pass

    def put(self, local, libpath, url, file, interval, delay, multi, quote, a_pref, a_suff, s_pref, s_suff, notif):
        self.cparser.set('Settings', 'local', local)
        self.cparser.set('Settings', 'libpath', libpath)
        self.cparser.set('Settings', 'url', url)
        self.cparser.set('Settings', 'file', file)
        self.cparser.set('Settings', 'interval', interval)
        self.cparser.set('Settings', 'delay', delay)
        self.cparser.set('Settings', 'multi', str(multi))
        self.cparser.set('Settings', 'quote', str(quote))
        self.cparser.set('Settings', 'a_pref', a_pref)
        self.cparser.set('Settings', 'a_suff', a_suff)
        self.cparser.set('Settings', 's_pref', s_pref)
        self.cparser.set('Settings', 's_suff', s_suff)
        self.cparser.set('Settings', 'notif', str(notif))

        cf = open(self.cfile, 'w')
        self.cparser.write(cf)
        cf.close()

#--------------------------------------
# FUNCTIONS 
def is_number(s):  # test for number type
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_bool(s):  # test for bool type
    if s == "False":
        return 0
    else:
        return 1

def main():  # track polling process
    global track
    conf = ConfigFile(config, config_file)

    # get poll interval and then poll
    interval = conf.interval
    print("polling interval is: "+str(interval))
    new = poll(lambda: gettrack(ConfigFile(config, config_file), track), step=interval, poll_forever=True)

    # display new track info in system notification
    track = new

    # write new track info to file
    tinfo = new  # conf.pref + new + conf.suff
    if 'No Song Data' in tinfo:
        tinfo = ''
    sleep(conf.delay)
    writetrack(conf.file, tinfo)

    # recurse
    main()

main_thread = Thread(target=main, daemon=True)

def gettrack(c, t):  # get last played track
    global paused
    conf = c
    tk = t

    # check paused state
    while True:
        if not paused:
            break

    print("checking: "+conf.url)

    # get and parse playlist source code
    page = requests.get(conf.url)
    tree = html.fromstring(page.text)
    item = tree.xpath('(//div[@class="playlist-trackname"]/text())[last()]')
    tdat = item

    # cleanup
    tdat = str(tdat)
    tdat = tdat.replace("['", "").replace("']", "").replace("[]", "").replace("\\n", "").replace("\\t", "") \
        .replace("[\"", "").replace("\"]", "")
    tdat = tdat.strip()

    if tdat == "":
        return False

    t = tdat.split(" - ", 1)

    if t[0] == '.':
        artist = ''
    else:
        artist = c.a_pref + t[0] + c.a_suff

    if t[1] == '.':
        song = ''
    elif conf.quote == 1:  # handle quotes
        song = c.s_pref + "\"" + t[1] + "\"" + c.s_suff
    else:
        song = c.s_pref + t[1] + c.s_suff

    if artist == '' and song == '':
        return 'No Song Data'

    # handle multiline
    if conf.multi == 1:
        tdat = artist + "\n" + song
    elif song == '' or artist == '':
        tdat = artist + song
    else:
        tdat = artist + " - " + song

    if tdat != tk:
        return tdat
    else:
        return False

def writetrack(f, t=""):  # write new track info
    file = f
    with open(file, "w", encoding='utf-8') as f:
        print("writing...")
        f.write(t)

if __name__ == "__main__":
    main()

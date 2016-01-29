#!/usr/bin/env python3
# -*- encoding: UTF-8 -*-
import os
from sh import cd, git, ErrorReturnCode
from time import strftime, tzset
from ircbot import ircbot

host = "irc.freenode.net"
port = 6666
chan = '#gzlug-test'
nick = "gzluglog"
repo = '../irclog'

f = None

def log(msg):
    global f
    print('[logbot]', 'log:', msg)
    today = strftime('%Y-%m-%d.log')
    if f.name != today:
        f.close()
        try:
            git.add(f.name)
            git.commit('-m', 'add ' + f.name)
            git.push()
        except ErrorReturnCode:
            print('[logbot]', 'err:', 'fail to commit', f.name)

        print('[logbot]', 'commit:', f.name)
        print('[logbot]', 'new:', today)
        f = open(today, 'w+')
    f.write(msg)

def main():
    global f

    os.environ['TZ'] = 'Asia/Shanghai'
    tzset()
    print('[logbot]', 'start logging:', strftime('%Y-%m-%d %H:%M:%S'))

    cd(repo)
    f = open(strftime('%Y-%m-%d.log'), 'w+')

    bot = ircbot(host, port, nick)
    bot.join_chan(chan)

    try:
        while True:
            rmsg = bot.recv_msg()
            if rmsg == (None, None, None):
                continue
            if rmsg[1] in ['PART', 'JOIN']:
                man, act, ch = rmsg
                line = '[{0}] -- {1} {2} {3}\n'.format(strftime('%H:%M:%S'), man, act, ch)
            else:
                man, ch, msg = rmsg
                line = '[{0}] {1}@{2}: {3}\n'.format(strftime('%H:%M:%S'), man, ch, msg)
            log(line)
            
    except KeyboardInterrupt:
        bot.stop()
        f.close()
        print('[logbot]', 'exit')
        exit(0)

if __name__ == '__main__':
    main()

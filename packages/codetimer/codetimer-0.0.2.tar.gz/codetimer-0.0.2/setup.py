# -*- coding: utf-8 -*-
__author__ = 'Min'

from distutils.core import setup

setup (
        name               = 'codetimer',
        version             = '0.0.2',
        py_modules      = ['codetimer'],
        author              = 'Min',
        author_email     = 'wwwee98@gmail.com',
        url                    = 'https://www.facebook.com/yingerking',
        description        = """
        SimpleCodeTimer !

Before :
=================== CODE ====================
    def say(what):
        print "say : %s" % what

    say("ho!!")

=================== OUTPUT ===================
    say : ho!!

After :

=================== CODE ====================
    import codetimer
    @codetimer.methodTimer
    def say(what):
        print "say : %s" % what

    say("ho!!")

=================== OUTPUT ===================
    say : ho!!
    SimpleCodeTimer : say method costs 0.000028 seconds !

        """,
        keywords = ['runtime', 'timer', 'codetimer']
    )
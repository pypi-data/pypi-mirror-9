# -*- coding: utf-8 -*-
__author__ = 'Min'

from distutils.core import setup

setup (
        name               = 'codetimer',
        version             = '0.1.0',
        py_modules      = ['codetimer'],
        author              = 'Min',
        author_email     = 'wwwee98@gmail.com',
        url                    = 'https://www.facebook.com/yingerking',
        long_description        = """
        SimpleCodeTimer !

Before :
=================== CODE ====================
    def say(what):
        print "say : %s" % what

    say("ho!!")

=================== OUTPUT ==================
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
        description="simple code timer",
        keywords = ['runtime', 'timer', 'codetimer']
    )
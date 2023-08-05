# -*- coding: utf-8 -*-
__author__ = 'Min'

from distutils.core import setup

setup (
        name               = 'codetimer',
        version             = '0.0.0.1',
        py_modules      = ['codetimer'],
        author              = 'Min',
        author_email     = 'wwwee98@gmail.com',
        url                    = 'https://www.facebook.com/yingerking',
        description        = """
        SimpleCodeTimer !<br>
/n
Before :/n
=================== CODE ====================/n
    def say(what):/n
        print "say : %s" % what/n
/n
    say("ho!!")/n
/n
=================== OUTPUT ===================/n
    say : ho!!/n
/n
After :/n
/n
=================== CODE ====================/n
    import codetimer/n
    @codetimer.methodTimer/n
    def say(what):/n
        print "say : %s" % what/n
/n
    say("ho!!")/n
/n
=================== OUTPUT ===================/n
    say : ho!!/n
    SimpleCodeTimer : say method costs 0.000028 seconds !/n

        """,
        keywords = ['runtime', 'timer', 'codetimer']
    )
# -*- coding: utf-8 -*-
__author__ = 'Min'


def methodTimer(method):
    def measure(*args, **kwargs):
        try:
            import time
            time_before = time.time()
            method(*args, **kwargs)
            print("SimpleCodeTimer : %s method costs %f seconds !" % (method.__name__, time.time() - time_before))
        except Exception as E:
            print("SimpleCodeTimer : An error occured ! - %s" % str(E))

    return measure


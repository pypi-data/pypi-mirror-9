# -*- coding: utf-8 -*-
import jdatetime

__author__ = 'esnaashari'

class jalaliLibrary():
    """

    """
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    __version__ = pkg_resources.get_distribution("robotframework-jalalidate").version

    def __init__(self):
        pass

    def today_date(self, format=None):
        if format is None:
            return jdatetime.date.today()
        else:
            return jdatetime.date.today().strftime(format)


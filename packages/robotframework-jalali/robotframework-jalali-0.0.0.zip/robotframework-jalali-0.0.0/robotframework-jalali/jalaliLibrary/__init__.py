# -*- coding: utf-8 -*-
import jdatetime

__author__ = 'esnaashari'

class JALALIDate():
    """

    """
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    __version__ = pkg_resources.get_distribution("robotframework-jalalidate").version

    def __init__(self):
        pass

    def today_date(self):
		return jdatetime.date.today()
		
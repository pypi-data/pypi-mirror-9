# -*- coding: utf-8 -*-
"""
Created on Thu Jan  8 17:30:02 2015

@author: JLavin
"""

from nose.tools import assert_equals
#from hedgeye_analysis import hedgeye_analysis_boilerplate as bp
from hedgeye_analysis.hedgeye_analysis_boilerplate import *
import mock

def test_root_dir_1():
    os.getcwd = mock.Mock(return_value='/mydir/shared')
    assert_equals( root_dir(),
                   '/mydir')

def test_root_dir_2():
    os.getcwd = mock.Mock(return_value='/main/mydir/shared')
    assert_equals( root_dir(),
                   '/main/mydir')

def test_root_dir_3():
    os.getcwd = mock.Mock(return_value='/main/mydir')
    assert_equals( root_dir(),
                   '/main/mydir')

def test_shared_dir():
    os.getcwd = mock.Mock(return_value='/mydir/shared')
    assert_equals( shared_dir(),
                   '/mydir/shared')

def test_copied_dir():
    os.getcwd = mock.Mock(return_value='/mydir/shared')
    assert_equals( copied_dir(),
                   '/mydir/copied')

def test_today_string():
    from datetime import date
    assert_equals( today_string(),
                   date.today().strftime("%Y-%m-%d") )

def test_tomorrow_string():
    assert_equals( tomorrow_string(),
                   tomorrow().strftime("%Y-%m-%d") )

def test_tomorrow():
    assert_equals( tomorrow(),
                   today() + datetime.timedelta(days = 1) )

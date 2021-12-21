"""
    this class contains functions that instantiate custom driver wrapping classes (see test_driver_utils.py)
    call specific functions within those classes (which perform specific actions within the application)
    every function checks that those actions are completed successfully (result1:Bool)
    if so they then call helper functions in test_driver_utils.py to query the database (result2:Bool)

    from those two steps the function obtain two boolean results (result1 and result2), which are then summarised into
    one (T/F) and returned to the calling test. The test will only pass if these testcase functions return TRUE

"""

__author__ = "Chiara Pascucci"

import os
import selenium.common.exceptions
import django

from sharespace.testing.test_db_utils import test_item_creation, test_today_loan_creation, test_loan_picked_up, \
    test_borrower_return, test_confirm_return_lender, test_fut_loan_creation, test_cancel_booking, test_add_pp, \
    test_subs_proposal, test_report_issue_loan_returned, test_delete_purchase_proposal
from sharespace.testing.test_driver_utils import TestDriverChrome


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sharespace_project.settings')
django.setup()


# helper function
def summarise_results(result1:bool, result2:dict):
    if not result2:
        return False
    else:
        driver_result = True
        db_result = all(value == True for value in result2.values())
        return driver_result and db_result


# add item one owner
def testcase1(email, pwd, item_info, driver=None):
    if driver is None:
        # driver class is instantiated
        driver = TestDriverChrome()
    driver.go_home()
    # user 1 is logged in
    driver.login(email, pwd)

    # user 1 adds one item with only one owner (themselves)
    # method returns the id of the item created by driver interaction
    result1 = driver.add_item_one_owner(item_info)
    if result1['added']:
        result2 = test_item_creation(result1['item_id'], item_info)
    else:
        result2 = {}

    driver.close_driver()

    return summarise_results(result1, result2)


# add item multiple owners
def testcase2(email, pwd, item_info, driver=None):
    if driver is None:
        # driver class is instantiated
        driver = TestDriverChrome()
    driver.login(email, pwd)
    driver.go_home()

    # user 1 adds one item with multiple owners
    # method return the id of the item created by driver interaction
    result1 = driver.add_item_mul_owners(item_info)
    if result1['added']:
        result2 = test_item_creation(result1['item_id'], item_info)
    else:
        result2 = {}

    driver.close_driver()

    return summarise_results(result1, result2)


# borrow item from today
def testcase3(email, pwd, username, loan_data: dict, driver=None):

    # new driver instantiated for another user to log in
    if driver is None:
        # driver class is instantiated
        driver = TestDriverChrome()
    driver.go_home()
    # user 3 is logged in
    driver.login(email, pwd)

    # test loan creation
    try:
        result1 = driver.borrow_item_test(loan_data['name'], loan_data['from'], loan_data['until'], username)
    except selenium.common.exceptions.TimeoutException:
        result1 = {'loan_id': None, 'loan_created': False}
    finally:
       # driver.close_driver()
        pass

    if result1['loan_created']:
        result2 = test_today_loan_creation(result1['loan_id'], {'item_name': loan_data['name'], 'req': username})
    else:
        result2 = {}
    return summarise_results(result1, result2)


# confirm pickup
def testcase4(email, pwd, username, driver=None):

    if driver is None:
        # driver class is instantiated
        driver = TestDriverChrome()

    driver.login(email, pwd)

    result1 = driver.item_on_loan_pickup_test(username)

    if result1['loan_picked_up']:
        result2 = test_loan_picked_up(result1['loan_id'])
    else:
        result2 = {}
    return summarise_results(result1, result2)


# borrower confirms they have returned the item they have borrowed
def testcase5(email, pwd, username, driver=None):
    if driver is None:
        # driver class is instantiated
        driver = TestDriverChrome()

    driver.login(email, pwd)
    result1 = driver.borrower_return_loan_test(username)
    if result1['loan_returned']:
        result2 = test_borrower_return(result1['loan_id'])
    else:
        result2 = {}
    driver.close_driver()
    return summarise_results(result1, result2)


# confirm return lender
def testcase6(email, pwd, username, driver=None):

    if driver is None:
        # driver class is instantiated
        driver = TestDriverChrome()
    driver.login(email, pwd)
    result1 = driver.loan_confirm_lender(username)
    print(result1)
    if not result1['notif_slug'] is None:
        result2 = test_confirm_return_lender(result1['notif_slug'])
    else:
        result2 = {}
    driver.close_driver()
    return summarise_results(result1, result2)


# lender confirm return with report
def testcase7(email, pwd, username, driver=None):
    if driver is None:
        # driver class is instantiated
        driver = TestDriverChrome()
    driver.login(email, pwd)
    driver.go_home()
    result1 = driver.loan_confirm_lender_report(username)
    driver.close_driver()
    if result1['confirm']:
        result2 = test_report_issue_loan_returned(result1['notif_slug'])
    else:
        result2 = {}

    return summarise_results(result1, result2)


# future booking
def testcase8(email, pwd, username, loan_data,driver=None):
    if driver is None:
        # driver class is instantiated
        driver = TestDriverChrome()

    driver.login(email, pwd)
    try:
        result1 = driver.borrow_item_test(loan_data['name'], loan_data['from'], loan_data['until'], username)
    except selenium.common.exceptions.TimeoutException:
        result1 = {'loan_id': None, 'loan_created': False}
    finally:
        driver.close_driver()

    if result1['loan_created']:
        result2 = test_fut_loan_creation(result1['loan_id'], {'item_name': loan_data['name'], 'req': username})
    else:
        result2 = {}

    return summarise_results(result1, result2)


# cancel booking
def testcase9(email, pwd, username, driver=None):
    if driver is None:
        # driver class is instantiated
        driver = TestDriverChrome()
    driver.login(email, pwd)
    result1 = driver.cancel_booking_test(username)

    if not result1['loan_id'] is None:
        result2 = test_cancel_booking(result1['loan_id'])
    else:
        result2 = {}
    driver.close_driver()
    return summarise_results(result1, result2)


# user adds a purchase proposal to the website
def testcase10(email, pwd, pp_data, driver=None):
    if driver is None:
        # driver class is instantiated
        driver = TestDriverChrome()
    driver.login(email, pwd)
    result1 = driver.add_pp_test(pp_data)
    driver.close_driver()
    if result1['pp_created']:
        result2 = test_add_pp(result1['pp_id'], pp_data)
    else:
        result2 = {}
    return summarise_results(result1, result2)


def testcase11(email, pwd, username, driver=None):
    if driver is None:
        # driver class is instantiated
        driver = TestDriverChrome()
    driver.login(email, pwd)
    result1 = driver.sub_to_pp_test()
    driver.close_driver()
    if result1['subed']:
        prop_slug = result1['prop_slug']
        result2 = test_subs_proposal(prop_slug, username)

    else:
        result2 = {}

    return summarise_results(result1, result2)


def testcase12(email, pwd, username, driver=None):
    if driver is None:
        # driver class is instantiated
        driver = TestDriverChrome()
    driver.login(email, pwd)
    driver.go_home()
    result1 = driver.delete_pp(username)
    driver.close_driver()
    if result1['pp_del']:
        result2 = test_delete_purchase_proposal(result1['pp_slug'])
    else:
        result2 = {}

    return summarise_results(result1, result2)

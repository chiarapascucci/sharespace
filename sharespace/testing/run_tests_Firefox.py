"""
    please see the doc string of run_tests_chrome.py
    both classes have the same structure. This was created as a separate class for ease of runnign the tests
    with pytest and a different driver

"""

__author__ = "Chiara Pascucci"

from datetime import datetime, timedelta

from sharespace.testing.test_driver_utils import TestDriverME, TestDriverFirefox
from sharespace.testing.tests_cases import testcase1, testcase2, testcase3, testcase4, testcase5, testcase6, testcase7, \
    testcase8, testcase9, testcase10, testcase11, testcase12

user1 = {'email': 'g1@mail.com', 'pwd': 'helloyou123', 'username': 'chiara', }
user2 = {'email': 'gg2@mail.com', 'pwd': 'helloyou123', 'username': 'bob', }
user3 = {'email': 'g3@mail.com', 'pwd': 'helloyou123', 'username': 'aba', }


class TestAddItem():
    add_item_test1 = {'name': "test1", 'description': "test item 1",
                      'adr': "testaddress1", 'phone': "+4407756384920",
                      'cat': 'Kitchen', 'sub_cat': 'utensils',
                      'owner': 'chiara', 'guardian': 'chiara', 'price': '1000'}

    add_item_test2 = {'name': "test2", 'description': "test item 2", 'adr': "testaddress2",
                      'phone': "+4407756384920", 'owner': ['chiara', 'bob'], 'guardian': 'chiara',
                      'cat': 'Kitchen', 'sub_cat': 'utensils', 'price': '2300'}

    def test_add_item_one_owner(self):
        driver = TestDriverFirefox()
        result = testcase1(email=user1['email'], pwd=user1['pwd'], item_info=self.add_item_test1, driver=driver)
        assert result == True

    def test_add_item_mult_owners(self):
        driver = TestDriverFirefox()
        result = testcase2(email=user1['email'], pwd=user1['pwd'], item_info=self.add_item_test2, driver=driver)
        assert result == True


class TestBorrowItem():
    today = datetime.now().strftime("%Y-%m-%d")
    one_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    two_weeks = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    loan1 = {'name': 'test1', 'from': today, 'until': one_week}
    loan2 = {'name': 'test2', 'from': today, 'until': one_week}
    loan3 = {'name': 'test1', 'from': one_week, 'until': two_weeks}

    def test_borrow_item_today(self):
        driver = TestDriverFirefox()
        result = testcase3(email=user3['email'], pwd=user3['pwd'], username=user3['username'], loan_data=self.loan1,
                           driver=driver)
        assert result == True

    def test_confirm_pickup(self):
        driver = TestDriverFirefox()
        # print("\n=============== results of test 4: confirm pick up  =================")
        result = testcase4(email=user3['email'], pwd=user3['pwd'], username=user3['username'], driver=driver)
        assert result == True
        # print("=============================================================================")

    def test_borrower_return(self):
        driver = TestDriverFirefox()
        # print("\n=============== results of test 5: borrower confirms return  =================")
        result = testcase5(email=user3['email'], pwd=user3['pwd'], username=user3['username'], driver=driver)
        assert result == True
        # print("=============================================================================")

    def test_lender_return_no_report(self):
        driver = TestDriverFirefox()
        # print("\n=============== results of test 6: lender confirms return  =================")
        result = testcase6(email=user1['email'], pwd=user1['pwd'], username=user1['username'], driver=driver)
        assert result == True

    # print("=============================================================================")

    def test_lender_return_report(self):

        testcase3(email=user3['email'], pwd=user3['pwd'], username=user3['username'], loan_data=self.loan2, driver=TestDriverFirefox())
        testcase4(email=user3['email'], pwd=user3['pwd'], username=user3['username'], driver=TestDriverFirefox())
        testcase5(email=user3['email'], pwd=user3['pwd'], username=user3['username'], driver=TestDriverFirefox())
        result = testcase7(email=user1['email'], pwd=user1['pwd'], username=user1['username'], driver=TestDriverFirefox())
        assert result == True

    def test_borrow_item_future(self):
        driver = TestDriverFirefox()
        print("=============== results of test 8: borrow item in the future  =================")
        result = testcase8(email=user3['email'], pwd=user3['pwd'], username=user3['username'], loan_data=self.loan3,
                           driver=driver)
        assert result == True
        print("=============================================================================")

    def test_cancel_future_loan(self):
        driver = TestDriverFirefox()
        # print("=============== results of test 9: cancel future loan/booking  =================")
        result = testcase9(email=user3['email'], pwd=user3['pwd'], username=user3['username'], driver=driver)
        assert result == True
        # print("=============================================================================")


class TestPurchaseProposal():
    proposal1_data = {'name': "pptest1", 'descr': "pp test item 1", 'adr': "testaddress1", 'phone': "+4407756384920",
                      'cat': 'Kitchen', 'sub_cat': 'utensils', 'price': '2300'}

    def test_add_proposal(self):
        driver = TestDriverFirefox()
        result = testcase10(email=user2['email'], pwd=user2['pwd'], pp_data=self.proposal1_data, driver=driver)
        assert result == True

    def test_sub_proposal(self):
        driver = TestDriverFirefox()
        result = testcase11(email=user3['email'], pwd=user3['pwd'], username=user3['username'], driver=driver)
        assert result == True

    def test_cancel_proposal(self):
        driver = TestDriverFirefox()
        result = testcase12(email=user2['email'], pwd=user2['pwd'], username=user2['username'], driver=driver)
        assert result == True

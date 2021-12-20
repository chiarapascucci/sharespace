from datetime import datetime, timedelta

from sharespace.testing.test_driver_utils import TestDriverME
from sharespace.testing.tests_cases import testcase1, testcase2, testcase3, testcase4, testcase5, testcase6, testcase7, \
    testcase8, testcase9, testcase10, testcase11, testcase12

user1 = {'email':'g1@mail.com', 'pwd': 'helloyou123', 'username':'chiara', }
user2 = {'email':'gg2@mail.com', 'pwd': 'helloyou123', 'username':'bob', }
user3 = {'email':'g3@mail.com', 'pwd': 'helloyou123', 'username':'aba', }


class TestAddItem():
    add_item_test1 = {'name': "test1", 'description': "test item 1",
                        'adr': "testaddress1", 'phone': "+4407756384920",
                        'cat': 'Kitchen', 'sub_cat': 'utensils',
                        'owner': 'chiara', 'guardian': 'chiara', 'price': '1000'}

    add_item_test2 = {'name': "test2", 'description': "test item 2", 'adr': "testaddress2",
                        'phone': "+4407756384920", 'owner': ['chiara', 'bob'], 'guardian': 'chiara',
                        'cat': 'Kitchen', 'sub_cat': 'utensils', 'price': '2300'}

    def test_add_item_one_owner(self):
        driver = TestDriverME()

        result = testcase1(email=user1['email'], pwd=user1['pwd'], item_info=self.add_item_test1, driver=driver)
        assert result == True

    def test_add_item_mult_owners(self):
        driver = TestDriverME()

        result = testcase2(email=user1['email'], pwd=user1['pwd'], item_info=self.add_item_test2, driver=driver)
        assert result == True


class TestBorrowItem():
    today = datetime.now().strftime("%d%m%Y")
    one_week = (datetime.now() + timedelta(days=7)).strftime("%d%m%Y")
    two_weeks = (datetime.now() + timedelta(days=14)).strftime("%d%m%Y")
    loan1 = {'name': 'test1', 'from': today, 'until': one_week}
    loan2 = {'name': 'test2', 'from': today, 'until': one_week}
    loan3 = {'name': 'test1', 'from': one_week, 'until': two_weeks}

    def test_borrow_item_today(self):
        driver = TestDriverME()
        result = testcase3(email=user3['email'], pwd=user3['pwd'], username=user3['username'], loan_data=self.loan1, driver=driver)
        assert result == True

    def test_confirm_pickup(self):
        driver = TestDriverME()
        result = testcase4(email=user3['email'], pwd=user3['pwd'], username=user3['username'], driver=driver)
        assert result == True

    def test_borrower_return(self):
        driver = TestDriverME()
        result = testcase5(email=user3['email'], pwd=user3['pwd'], username=user3['username'], driver=driver)
        assert result == True

    def test_lender_return_no_report(self):
        driver = TestDriverME()
        result = testcase6(email=user1['email'], pwd=user1['pwd'], username=user1['username'], driver=driver)
        assert result == True

    def test_lender_return_report(self):

        testcase3(email=user3['email'], pwd=user3['pwd'], username=user3['username'], loan_data=self.loan2, driver=TestDriverME())
        testcase4(email=user3['email'], pwd=user3['pwd'], username=user3['username'], driver=TestDriverME())
        testcase5(email=user3['email'], pwd=user3['pwd'], username=user3['username'], driver=TestDriverME())
        result = testcase7(email=user1['email'], pwd=user1['pwd'], username=user1['username'], driver=TestDriverME())
        assert result == True

    def test_borrow_item_future(self):
        driver = TestDriverME()
        result = testcase8(email=user3['email'], pwd=user3['pwd'], username=user3['username'], loan_data=self.loan3, driver=driver)
        assert result == True

    def test_cancel_future_loan(self):
        driver = TestDriverME()
        result = testcase9(email=user3['email'], pwd=user3['pwd'], username=user3['username'], driver=driver)
        assert result == True


class TestPurchaseProposal():
    proposal1_data = {'name': "pptest1", 'descr': "pp test item 1", 'adr': "testaddress1", 'phone': "+4407756384920",
                 'cat': 'Kitchen', 'sub_cat': 'utensils', 'price': '2300'}

    def test_add_proposal(self):
        driver = TestDriverME()
        result = testcase10(email=user2['email'], pwd=user2['pwd'], pp_data=self.proposal1_data, driver=driver)
        assert result == True

    def test_sub_proposal(self):
        driver = TestDriverME()
        result = testcase11(email=user3['email'], pwd=user3['pwd'], username=user3['username'], driver=driver)
        assert result == True

    def test_cancel_proposal(self):
        driver = TestDriverME()
        result = testcase12(email=user2['email'], pwd=user2['pwd'], username= user2['username'], driver=driver)
        assert result == True

"""this file defines the tests (using helper test case functions from test_cases.py and allows the user to run them
    using the pytest framework

    the file is organised in three tests classes:
    - adding items
    - borrowing items
    - adding purchase proposals

    each class contains functions to test specific actions within those areas
    each function calls a specific function from the test_case.py file, which returns True iff all the steps for that action
    could be completed and the database was also updated correctly

    please see the docstring to tests_cases.py for more information

"""

__author__ = "Chiara Pascucci"

from datetime import datetime, timedelta
from sharespace.testing.tests_cases import testcase1, testcase2, testcase3, testcase4, testcase5, testcase6, testcase7, \
    testcase8, testcase9, testcase10, testcase11, testcase12

# gloabl data used for the tests
user1 = {'email': 'g1@mail.com', 'pwd': 'helloyou123', 'username': 'chiara', }
user2 = {'email': 'gg2@mail.com', 'pwd': 'helloyou123', 'username': 'bob', }
user3 = {'email': 'g3@mail.com', 'pwd': 'helloyou123', 'username': 'aba', }

# class to test add item logic
class TestAddItem:
    add_item_test1 = {'name': "test1", 'description': "test item 1",
                      'adr': "testaddress1", 'phone': "+4407756384920",
                      'cat': 'Kitchen', 'sub_cat': 'utensils',
                      'owner': 'chiara', 'guardian': 'chiara', 'price': '1000'}

    add_item_test2 = {'name': "test2", 'description': "test item 2", 'adr': "testaddress2",
                      'phone': "+4407756384920", 'owner': ['chiara', 'bob'], 'guardian': 'chiara',
                      'cat': 'Kitchen', 'sub_cat': 'utensils', 'price': '2300'}

    # class functions that tests adding a new item with one owner
    def test_add_item_one_owner(self):
        result = testcase1(email=user1['email'], pwd=user1['pwd'], item_info=self.add_item_test1)
        assert result == True

    # class functions that test adding a new item with multiple owners
    def test_add_item_mult_owners(self):
        result = testcase2(email=user1['email'], pwd=user1['pwd'], item_info=self.add_item_test2)
        assert result == True


# class to test the borrowign-lending logic in the application
class TestBorrowItem:
    # class level data to generate the appropriate data needed to simulate user input
    today = datetime.now().strftime("%d%m%Y")
    one_week = (datetime.now() + timedelta(days=7)).strftime("%d%m%Y")
    two_weeks = (datetime.now() + timedelta(days=14)).strftime("%d%m%Y")
    loan1 = {'name': 'test1', 'from': today, 'until': one_week}
    loan2 = {'name': 'test2', 'from': today, 'until': one_week}
    loan3 = {'name': 'test1', 'from': one_week, 'until': two_weeks}

    # testing loan creation when borrowing an item from the present day
    def test_borrow_item_today(self):
        result = testcase3(email=user3['email'], pwd=user3['pwd'], username=user3['username'], loan_data=self.loan1)
        assert result == True

    # testing previously booked item pick up
    def test_confirm_pickup(self):
        result = testcase4(email=user3['email'], pwd=user3['pwd'], username=user3['username'])
        assert result == True

    # testing the return of the loaned item to the lender
    def test_borrower_return(self):
        result = testcase5(email=user3['email'], pwd=user3['pwd'], username=user3['username'])
        assert result == True

    # testing the lender confirming the item has been returned
    def test_lender_return_no_report(self):
        result = testcase6(email=user1['email'], pwd=user1['pwd'], username=user1['username'])
        assert result == True

    # a new loan is created from today, the item is picked and returned. The the lender confirmation is simulated again,
    # but this time the lender submits a report
    # this functions tests this logic
    def test_lender_return_report(self):
        testcase3(email=user3['email'], pwd=user3['pwd'], username=user3['username'], loan_data=self.loan2)
        testcase4(email=user3['email'], pwd=user3['pwd'], username=user3['username'])
        testcase5(email=user3['email'], pwd=user3['pwd'], username=user3['username'])
        result = testcase7(email=user1['email'], pwd=user1['pwd'], username=user1['username'])
        assert result == True

    # user books an item in the future
    def test_borrow_item_future(self):
        result = testcase8(email=user3['email'], pwd=user3['pwd'], username=user3['username'], loan_data=self.loan3)
        assert result == True

    # user cancels previously made booking
    def test_cancel_future_loan(self):
        result = testcase9(email=user3['email'], pwd=user3['pwd'], username=user3['username'])
        assert result == True


# purchase proposal actions are tested by this class
class TestPurchaseProposal:
    proposal1_data = {'name': "pptest1", 'descr': "pp test item 1", 'adr': "testaddress1", 'phone': "+4407756384920",
                      'cat': 'Kitchen', 'sub_cat': 'utensils', 'price': '2300'}

    # user adds a purchase proposal
    def test_add_proposal(self):
        result = testcase10(email=user2['email'], pwd=user2['pwd'], pp_data=self.proposal1_data)
        assert result == True

    # user subscribes to a purchase proposal
    def test_sub_proposal(self):
        result = testcase11(email=user3['email'], pwd=user3['pwd'], username=user3['username'])
        assert result == True

    # user deletes the purchase proposal they previously submitted
    def test_cancel_proposal(self):
        result = testcase12(email=user2['email'], pwd=user2['pwd'], username=user2['username'])
        assert result == True

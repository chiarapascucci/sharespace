from datetime import datetime, timedelta
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

        #print("=============== results of test 1: add item with one owner  =================")
        result = testcase1(email=user1['email'], pwd=user1['pwd'], item_info=self.add_item_test1)
        assert result == True
        #print("=============================================================================")

    def test_add_item_mult_owners(self):

        #print("=============== results of test 2: add item with multiple owners owner  =================")
        result = testcase2(email=user1['email'], pwd=user1['pwd'], item_info=self.add_item_test2)
        assert result == True
        #print("=============================================================================")

class TestBorrowItem():
    today = datetime.now().strftime("%d%m%Y")
    one_week = (datetime.now() + timedelta(days=7)).strftime("%d%m%Y")
    two_weeks = (datetime.now() + timedelta(days=14)).strftime("%d%m%Y")
    loan1 = {'name': 'test1', 'from': today, 'until': one_week}
    loan2 = {'name': 'test2', 'from': today, 'until': one_week}
    loan3 = {'name': 'test1', 'from': one_week, 'until': two_weeks}

    def test_borrow_item_today(self):
        #print("\n=============== results of test 3: borrow item from today  =================")
        result = testcase3(email=user3['email'], pwd=user3['pwd'], username=user3['username'], loan_data=self.loan1)
        assert result == True
        #print("=============================================================================")

    def test_confirm_pickup(self):
       # print("\n=============== results of test 4: confirm pick up  =================")
        result = testcase4(email=user3['email'], pwd=user3['pwd'], username=user3['username'])
        assert result == True
        #print("=============================================================================")

    def test_borrower_return(self):
        #print("\n=============== results of test 5: borrower confirms return  =================")
        result = testcase5(email=user3['email'], pwd=user3['pwd'], username=user3['username'])
        assert result == True
        #print("=============================================================================")

    def test_lender_return_no_report(self):
        #print("\n=============== results of test 6: lender confirms return  =================")
        result = testcase6(email=user1['email'], pwd=user1['pwd'], username=user1['username'])
        assert result == True
       # print("=============================================================================")

    def test_lender_return_report(self):
       # print("=============== results of test 7: lender confirms return with report  =================")
        #print("user3 borrows item test2 and returns it")
        testcase3(email=user3['email'], pwd=user3['pwd'], username=user3['username'], loan_data=self.loan2)
        testcase4(email=user3['email'], pwd=user3['pwd'], username=user3['username'])
        testcase5(email=user3['email'], pwd=user3['pwd'], username=user3['username'])
        result = testcase7(email=user1['email'], pwd=user1['pwd'], username=user1['username'])
        assert result == True
        #print("=============================================================================")

    def test_borrow_item_future(self):
        print("=============== results of test 8: borrow item in the future  =================")
        result = testcase8(email=user3['email'], pwd=user3['pwd'], username=user3['username'], loan_data=self.loan3)
        assert result == True
        print("=============================================================================")

    def test_cancel_future_loan(self):
        #print("=============== results of test 9: cancel future loan/booking  =================")
        result = testcase9(email=user3['email'], pwd=user3['pwd'], username=user3['username'])
        assert result == True
        #print("=============================================================================")


class TestPurchaseProposal():
    proposal1_data = {'name': "pptest1", 'descr': "pp test item 1", 'adr': "testaddress1", 'phone': "+4407756384920",
                 'cat': 'Kitchen', 'sub_cat': 'utensils', 'price': '2300'}

    def test_add_proposal(self):
        result = testcase10(email=user2['email'], pwd=user2['pwd'], pp_data=self.proposal1_data)
        assert result == True

    def test_sub_proposal(self):
        result = testcase11(email=user3['email'], pwd=user3['pwd'], username=user3['username'])
        assert result == True


    def test_cancel_proposal(self):
        result = testcase12(email=user2['email'], pwd=user2['pwd'], username= user2['username'])
        assert result == True


from sharespace.models import Item, Loan, Notification
import unittest


def test_item_creation(item_id:str, item_info:dict):
    try:
        item = Item.objects.get(item_id=item_id)
        item_name = item.name == item_info['name']
        item_description = item.description == item_info['description']
        item_cat = item.main_category.name == item_info['cat']
        item_sub_cat = item.sec_category.name == item_info['sub_cat']
        item_owners= False
        for o in item.owner.all():
            item_owners = o.user.username in item_info['owner']

        item_guardian = item.guardian.user.username == item_info['guardian']

        return {'item': True, 'name': item_name, 'descr': item_description, 'cat': item_cat, 'scat':item_sub_cat,
                'owners': item_owners, 'guard': item_guardian}

    except Item.DoesNotExist:
        return {'item':False}


def test_today_loan_creation(loan_id:str, loan_info):
    try:
        loan = Loan.objects.get(loan_id=loan_id)
        result = {
            'loan' : True,
            'name': loan.item_on_loan.name == loan_info['item_name'],
            'requestor': loan.requestor.__str__() == loan_info['req'],
            'status': loan.status == 'pen',
            'overdue': loan.overdue == False,
            'picked' : loan.item_loan_pick_up == False,
            'effects' : loan.applied_effects_flag == True
        }
        return result

    except Loan.DoesNotExist:
        return {'loan': False}


def test_fut_loan_creation(loan_id:str, loan_info):
    try:
        loan = Loan.objects.get(loan_id=loan_id)
        result = {
            'loan' : True,
            'name': loan.item_on_loan.name == loan_info['item_name'],
            'requestor': loan.requestor.__str__() == loan_info['req'],
            'status': loan.status == 'fut',
            'overdue': loan.overdue == False,
            'picked' : loan.item_loan_pick_up == False,
            'effects' : loan.applied_effects_flag == False
        }
        return result

    except Loan.DoesNotExist:
        return {'loan': False}

def test_loan_picked_up(loan_id:str):
    try:
        loan = Loan.objects.get(loan_id=loan_id)
        result = {
            'loan' : True,
            'overdue': loan.overdue == False,
            'picked' : loan.item_loan_pick_up == True,
            'effects' : loan.applied_effects_flag == True,
            'status' : loan.status == 'act'
        }
        return result

    except Loan.DoesNotExist:
        return {'loan': False}


def test_borrower_return(loan_id):

    try:
        loan = Loan.objects.get(loan_id=loan_id)
        result = {
            'loan' : True,
            'overdue': loan.overdue == False,
            'picked' : loan.item_loan_pick_up == True,
            'effects' : loan.applied_effects_flag == True,
            'status': loan.status == 'pen'
        }
        return result

    except Loan.DoesNotExist:
        return {'loan': False}


def test_confirm_return_lender(notif_id):
    try:
        notif = Notification.objects.get(notif_slug=notif_id)
        loan_slug = notif.content_object.loan_slug
        try:
            loan = Loan.objects.get(loan_slug=loan_slug)
            result = {
                'loan': True,
                'overdue': loan.overdue == False,
                'picked': loan.item_loan_pick_up == True,
                'effects': loan.applied_effects_flag == True,
                'status': loan.status == 'com'
            }
            return result

        except Loan.DoesNotExist:
            return {'confirmed_by_lender': False}

    except Notification.DoesNotExist:
        return {'confirmed_by_lender': False}


def test_cancel_booking(loan_id):
    try:
        loan = Loan.objects.get(loan_id = loan_id)
        print(loan)
        return False
    except Loan.DoesNotExist:
        return True
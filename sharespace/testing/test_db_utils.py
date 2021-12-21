"""
    this file contains helper functions to test database changes after certain actions are performed on the
    application. The take an identifier for a certain DB object and a set of data
    they retrieve the relevant DB entry and compare its data against the given data

    they return a dictionary that shows the outcome of each comparison made

"""

__author__ = "Chiara Pascucci"

from sharespace.models import Item, Loan, Notification, PurchaseProposal, UserProfile, CustomUser


def test_item_creation(item_id: str, item_info: dict):
    try:
        item = Item.objects.get(item_id=item_id)
        item_name = item.name == item_info['name']
        item_description = item.description == item_info['description']
        item_cat = item.main_category.name == item_info['cat']
        item_sub_cat = item.sec_category.name == item_info['sub_cat']
        item_owners = False
        for o in item.owner.all():
            item_owners = o.user.username in item_info['owner']

        item_guardian = item.guardian.user.username == item_info['guardian']

        return {'item': True, 'name': item_name, 'descr': item_description, 'cat': item_cat, 'scat': item_sub_cat,
                'owners': item_owners, 'guard': item_guardian}

    except Item.DoesNotExist:
        return {'item': False}


def test_today_loan_creation(loan_id: str, loan_info):
    try:
        loan = Loan.objects.get(loan_id=loan_id)
        result = {
            'loan': True,
            'name': loan.item_on_loan.name == loan_info['item_name'],
            'requestor': loan.requestor.__str__() == loan_info['req'],
            'status': loan.status == 'pen',
            'overdue': loan.overdue == False,
            'picked': loan.item_loan_pick_up == False,
            'effects': loan.applied_effects_flag == True
        }
        return result

    except Loan.DoesNotExist:
        return {'loan': False}


def test_fut_loan_creation(loan_id: str, loan_info):
    try:
        loan = Loan.objects.get(loan_id=loan_id)
        result = {
            'loan': True,
            'name': loan.item_on_loan.name == loan_info['item_name'],
            'requestor': loan.requestor.__str__() == loan_info['req'],
            'status': loan.status == 'fut',
            'overdue': loan.overdue == False,
            'picked': loan.item_loan_pick_up == False,
            'effects': loan.applied_effects_flag == False
        }
        return result

    except Loan.DoesNotExist:
        return {'loan': False}


def test_loan_picked_up(loan_id: str):
    try:
        loan = Loan.objects.get(loan_id=loan_id)
        result = {
            'loan': True,
            'overdue': loan.overdue == False,
            'picked': loan.item_loan_pick_up == True,
            'effects': loan.applied_effects_flag == True,
            'status': loan.status == 'act'
        }
        return result

    except Loan.DoesNotExist:
        return {'loan': False}


def test_borrower_return(loan_id):
    try:
        loan = Loan.objects.get(loan_id=loan_id)
        result = {
            'loan': True,
            'overdue': loan.overdue == False,
            'picked': loan.item_loan_pick_up == True,
            'effects': loan.applied_effects_flag == True,
            'status': loan.status == loan.PENDING
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
                'confirmed_by_lender': True,
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
        loan = Loan.objects.get(loan_id=loan_id)
        return {'cancelled': False}
    except Loan.DoesNotExist:
        return {'cancelled': True}


def test_add_pp(pp_slug, pp_data):
    try:
        proposal = PurchaseProposal.objects.get(proposal_slug=pp_slug)
        result = {
            'proposal_created': True,
            'subs': len(proposal.proposal_subscribers.all()) == 0,
            'description': proposal.proposal_item_description == pp_data['descr'],
            'price': proposal.proposal_price == int(pp_data['price']),
            'cat': proposal.proposal_cat.name == pp_data['cat'],
            'sub_cat': proposal.proposal_sub_cat.name == pp_data['sub_cat'],
            'contact': proposal.proposal_submitter.contact_details == pp_data['phone']
        }

        return result

    except PurchaseProposal.DoesNotExist:
        return {'proposal_created': False}


def test_cancel_proposal(prop_slug):
    try:
        proposal = PurchaseProposal.objects.get(proposal_slug=prop_slug)

        return {'cancelled': False}
    except PurchaseProposal.DoesNotExist:
        return {'cancelled': True}


# after user subscribe to proposal:
# check that subs count == 1
# and that subscribers.all() contains user
def test_subs_proposal(prop_slug, username):
    try:
        prop = PurchaseProposal.objects.get(proposal_slug=prop_slug)
        try:
            user = CustomUser.objects.get(username=username)
            try:
                user_profile = UserProfile.objects.get(user=user)
                print(prop.proposal_subscribers.all())
                print(user_profile)
                result = {
                    'subs_count': len(prop.proposal_subscribers.all()) == 1,
                    'sub': user_profile in prop.proposal_subscribers.all()
                }
                return result
            except UserProfile.DoesNotExist:
                return {'result': False}

        except CustomUser.DoesNotExist:
            return {'result': False}

    except PurchaseProposal.DoesNotExist:
        return {'result': False}


# after user unsubscribe to proposal:
# check that sbs count == 0
# and that subscriber.all() does not contain user
def test_unsub_proposal(prop_slug, username):
    try:
        prop = PurchaseProposal.objects.get(proposal_slug=prop_slug)
        try:
            user = CustomUser.objects.get(username=username)
            try:
                user_profile = UserProfile.objects.get(user=user)

                result = {
                    'subs_count': len(prop.proposal_subscribers.all()) == 0,
                    'sub': user_profile not in prop.proposal_subscribers.all()
                }
                return {'result': result}
            except UserProfile.DoesNotExist:
                return {'result': False}
        except CustomUser.DoesNotExist:
            return {'result': False}

    except PurchaseProposal.DoesNotExist:
        return {'result': False}


# after owner confirms that loan was returned and submits a report
# test that loan was completed as normal (use function above)
# query DB to check that the relevant Report entry was created
def test_report_issue_loan_returned(notif_slug):
    try:
        notif = Notification.objects.get(notif_slug=notif_slug)
        loan = notif.content_object
        confirmed_dict = test_confirm_return_lender(notif_slug)
        confirmed = all(value == True for value in confirmed_dict.values())
        report = loan.loan_reported
        if report is not None:
            return {'confirmed': confirmed, 'report': True}
        else:
            return {'confirmed': confirmed, 'report': False}

    except Notification.DoesNotExist:
        return {'confirmed': False}


def test_delete_purchase_proposal(pp_slug):
    try:
        proposal = PurchaseProposal.objects.get(proposal_slug=pp_slug)
        return {'cancelled': False}
    except PurchaseProposal.DoesNotExist:
        return {'cancelled': True}

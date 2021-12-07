from django.db.models.signals import post_save
from django.dispatch import receiver

from sharespace.models import Notification, Loan, Item


@receiver(post_save, sender=Item)
def notify_owners(sender, instance, created, **kwargs):
    print("signals - 10 - log: item post save signal")
    if created == False:
        #item_updated_notif_factory(instance)
        pass
    else:
        pass


# need to manage pending - changed PEN usage
@receiver(post_save, sender=Loan)
def create_notification_to_guardian(sender, instance, created, **kwargs):
    print("in signal, printing created: ", created)
    if created:
        pass
    else:
        if instance.status == instance.PENDING and not instance.item_loan_pick_up:
            notif = loan_prepare_item_for_pick_up(instance)
            print("signals - 20 - log: created notification for newly created loan, booked from today: \n", notif)

        elif instance.status == instance.PENDING and instance.item_loan_pick_up:
            notif = loan_item_returned_notif_factory(instance)
            print("signals - 30 - log: new notif: your item has been returned: \n", notif)

        elif instance.status == instance.FUTURE:
            notif = loan_item_has_been_booked_notif_factory(instance)
            print("signals - 25 - log: created notification for newly created loan, booked in the future: \n", notif)

        else:
            pass


def item_updated_notif_factory(subject):
    print("signals - 30 - log: called factory for updated item notification")
    owners_list = list(subject.owner.all())
    for owner in owners_list:
        notif = Notification.objects.create(notif_body="changes were made to your item",
                                            notif_title="your item has been updated",
                                            notif_action_needed=False,
                                            notif_target=owner,
                                            notif_origin=owner.user, content_object=subject)
        notif.save()
        notif.notif_target.save()
        print(f"signals - 40 - log: notification created for {owner}")


def loan_item_returned_notif_factory(subject):
    print("factory for item returned notif is called")
    print(" data received:")
    print(subject.item_on_loan.owner.first())
    print(subject.requestor)
    notif = Notification.objects.create(notif_body="action required, your item has been returned",
                                        notif_title="your {} has been returned".format(subject.item_on_loan),
                                        notif_action_needed=True,
                                        notif_target=subject.item_on_loan.guardian,
                                        notif_origin=subject.requestor.user, content_object=subject)

    notif.content_object = subject
    notif.save()
    print(notif)
    print("created item returned notification in factory")
    return notif


def loan_item_has_been_booked_notif_factory(subject):
    print("factory for your item has been booked in the future")
    print(" data received:")
    print(subject.item_on_loan.guardian)
    print(subject.requestor)
    notif = Notification.objects.create(notif_body="Ensure your item is ready for pick-up",
                                        notif_title="your {} has been booked from {}".format(subject.item_on_loan,
                                                                                             subject.out_date),
                                        notif_action_needed=False,
                                        notif_target=subject.item_on_loan.guardian,
                                        notif_origin=subject.requestor.user, content_object=subject)

    notif.content_object = subject
    notif.save()
    print(notif)
    print("created new loan  notification in factory")
    return notif


def loan_prepare_item_for_pick_up(subject):
    print("factory for prepare pick up notif called")
    print(" data received:")
    print(subject.item_on_loan.guardian)
    print(subject.requestor)
    notif = Notification.objects.create(notif_body="Ensure your item is ready for pick-up",
                                        notif_title="Your {} is due to be picked up today".format(subject.item_on_loan),
                                        notif_action_needed=False,
                                        notif_target=subject.item_on_loan.guardian,
                                        notif_origin=subject.requestor.user, content_object=subject)

    notif.content_object = subject
    notif.save()
    print(notif)
    print("created new prepare for pick up  notification in factory")
    return notif

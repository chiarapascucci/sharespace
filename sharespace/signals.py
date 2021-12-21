"""
    this files contains custom call back functions to deal with specific Django's signals
    they generate user notifications

"""

__author__ = "Chiara Pascucci"

from django.db.models.signals import post_save
from django.dispatch import receiver

from sharespace.models import Notification, Loan, Item


@receiver(post_save, sender=Item)
def notify_owners(sender, instance, created, **kwargs):
    if created == False:
        pass
    else:
        pass


@receiver(post_save, sender=Loan)
def create_notification_to_guardian(sender, instance, created, **kwargs):
    if created:
        pass
    else:
        if instance.status == instance.PENDING and not instance.item_loan_pick_up:
            notif = loan_prepare_item_for_pick_up(instance)

        elif instance.status == instance.PENDING and instance.item_loan_pick_up:
            notif = loan_item_returned_notif_factory(instance)

        elif instance.status == instance.FUTURE:
            notif = loan_item_has_been_booked_notif_factory(instance)

        else:
            pass


def item_updated_notif_factory(subject):
    owners_list = list(subject.owner.all())
    for owner in owners_list:
        notif = Notification.objects.create(notif_body="changes were made to your item",
                                            notif_title="your item has been updated",
                                            notif_action_needed=False,
                                            notif_target=owner,
                                            notif_origin=owner.user, content_object=subject)
        notif.save()
        notif.notif_target.save()


def loan_item_returned_notif_factory(subject):
    notif = Notification.objects.create(notif_body="action required, your item has been returned",
                                        notif_title="your {} has been returned".format(subject.item_on_loan),
                                        notif_action_needed=True,
                                        notif_target=subject.item_on_loan.guardian,
                                        notif_origin=subject.requestor.user, content_object=subject)

    notif.content_object = subject
    notif.save()
    return notif


def loan_item_has_been_booked_notif_factory(subject):
    notif = Notification.objects.create(notif_body="Ensure your item is ready for pick-up",
                                        notif_title="your {} has been booked from {}".format(subject.item_on_loan,
                                                                                             subject.out_date),
                                        notif_action_needed=False,
                                        notif_target=subject.item_on_loan.guardian,
                                        notif_origin=subject.requestor.user, content_object=subject)

    notif.content_object = subject
    notif.save()
    return notif


def loan_prepare_item_for_pick_up(subject):
    notif = Notification.objects.create(notif_body="Ensure your item is ready for pick-up",
                                        notif_title="Your {} is due to be picked up today".format(subject.item_on_loan),
                                        notif_action_needed=False,
                                        notif_target=subject.item_on_loan.guardian,
                                        notif_origin=subject.requestor.user, content_object=subject)

    notif.content_object = subject
    notif.save()
    return notif

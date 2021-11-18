from django.db.models.signals import post_save
from django.dispatch import receiver

from sharespace.models import Notification, Loan


@receiver(post_save, sender=Loan)
def create_notification_to_owners(sender, instance, created, **kwargs):
    print("in signal, printing created: ", created)
    if created == True:

        notif = loan_active_notif_factory(instance)
        print("new loan activation notification created by signal :", notif)
    else:
        if instance.status == 'pen':
            notif = loan_complete_notif_factory(instance)
            print("new loan return notification created by signal :", notif)
        elif instance.status == 'act':
            notif = loan_active_notif_factory(instance)




def loan_complete_notif_factory(subject):
    print("factory for completed loan method is called")
    print(" data received:")
    print(subject.item_on_loan.owner.first())
    print(subject.requestor)
    notif = Notification.objects.create(notif_body="action required, loan complete", notif_title="your item has been returned",
                                notif_action_needed=True,
                                notif_target=subject.item_on_loan.owner.first(),
                                notif_origin=subject.requestor.user, content_object=subject)

    notif.content_object = subject
    notif.save()
    print(notif)
    print("created loan comp notification in factory")
    return notif


def loan_active_notif_factory(subject):
    print("factory for new loan method is called")
    print(" data received:")
    print(subject.item_on_loan.owner.first())
    print(subject.requestor)
    notif = Notification.objects.create(notif_body="Ensure your item is ready for pick-up",
                                        notif_title="your item has been booked",
                                        notif_action_needed=False,
                                        notif_target=subject.item_on_loan.owner.first(),
                                        notif_origin=subject.requestor.user, content_object = subject)

    notif.content_object = subject
    notif.save()
    print(notif)
    print("created new loan  notification in factory")
    return notif
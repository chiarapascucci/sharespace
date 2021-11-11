from django.db.models.signals import post_save
from django.dispatch import receiver

from sharespace.models import LoanActiveNotification, Loan


@receiver(post_save, sender=Loan)
def create_notification_to_owners(sender, instance, created, **kwargs):
    if created:
        origin = instance.item_on_loan.owner.first()
        destination = instance.requestor
        LoanActiveNotification.objects.create(subject=instance, from_user=origin, to_user=destination)
        print("new loan activation notification created by signal")
    else:
        pass



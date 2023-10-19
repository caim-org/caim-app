from django.core import mail
from django.test import TestCase

from caim_base.notifications import notify_caim_foster_application_accepted
from caim_base.tests.factories import FosterApplicationFactory


class EmailTesting(TestCase):
    """
    Test that emails are always sent for certain events.
    follow this: https://docs.djangoproject.com/en/4.1/topics/testing/tools/#email-services
    """

    def test_foster_application_complete(self):
        foster_application = FosterApplicationFactory()
        foster_application.save()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "New Fosterer Application")
        self.assertIn(f"Foster First Name: {foster_application.fosterer.firstname}\n", mail.outbox[0].body)
        self.assertIn(f"Animal requested: {foster_application.animal.get_absolute_url()}\n", mail.outbox[0].body)

    def test_foster_application_accepted(self):
        foster_application = FosterApplicationFactory()
        foster_application.status = foster_application.Statuses.ACCEPTED
        foster_application.save()
        notify_caim_foster_application_accepted(foster_application)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, "New Fosterer Application")
        self.assertEqual(mail.outbox[1].subject, "New Foster Application Approved")
        self.assertIn(f"AWG: {foster_application.animal.awg.name}\n", mail.outbox[1].body)
        self.assertIn(
            f"Animal: {foster_application.animal.name}, {foster_application.animal.animal_type}\n", mail.outbox[1].body
        )
        self.assertIn(
            f"Fosterer: {foster_application.fosterer}, {foster_application.fosterer.city} {foster_application.fosterer.state}\n",
            mail.outbox[1].body,
        )

    def test_foster_profile_complete(self):
        pass

    def notify_new_awg_application(self):
        pass

    def notify_animal_comment(self):
        pass

    def notify_animal_comment_reply(self):
        pass

    def notify_animal_published(self):
        pass

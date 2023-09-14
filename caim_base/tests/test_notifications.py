from django.test import TestCase
from caim_base.tests.factories import FosterApplicationFactory
from django.core import mail


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
        self.assertIn(
            f"Foster First Name: {foster_application.fosterer.firstname}\n",
            mail.outbox[0].body,
        )
        self.assertIn(
            f"Animal requested: {foster_application.animal.get_absolute_url()}\n",
            mail.outbox[0].body,
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

from __future__ import annotations
from templated_email import send_templated_mail

from django.conf import settings
import caim_base.models.fosterer as fosterer

NOTIFICATIONS_SOURCE_EMAIL = "notifications@caim.org"
INTERNAL_NOTIFICATIONS_EMAIL = "hello@caim.org"


def notify_new_awg_application(awg):
    send_templated_mail(
        template_name="new_awg_application",
        recipient_list=[INTERNAL_NOTIFICATIONS_EMAIL],
        context={"awg": awg},
        from_email=NOTIFICATIONS_SOURCE_EMAIL,
    )


def notify_animal_comment(comment):
    # AWG staff
    animal = comment.animal
    awg = animal.awg
    members = awg.awgmember_set.all()
    emails = [str(member.user.email) for member in members]
    send_templated_mail(
        template_name="new_animal_comment",
        recipient_list=emails,
        context={"awg": awg, "animal": animal, "comment": comment},
        from_email=NOTIFICATIONS_SOURCE_EMAIL,
    )


def notify_animal_comment_reply(subcomment):
    comment = subcomment.comment
    animal = comment.animal
    subcomments = comment.get_sub_comments()
    emails = [str(subcomment.user.email) for subcomment in subcomments]
    emails.append(str(comment.user.email))
    emails = list(set(emails))
    send_templated_mail(
        template_name="new_animal_comment_reply",
        recipient_list=emails,
        context={"animal": animal},
        from_email=NOTIFICATIONS_SOURCE_EMAIL,
    )


def notify_animal_published(animal):
    pass


def notify_new_fosterer_profile(fosterer):
    send_templated_mail(
        template_name="new_fosterer_profile",
        recipient_list=[INTERNAL_NOTIFICATIONS_EMAIL],
        context={"fosterer": fosterer},
        from_email=NOTIFICATIONS_SOURCE_EMAIL,
    )


def notify_fosterer_of_animal_suggestion(
    suggested_animal: fosterer.FosterApplicationAnimalSuggestion,
):
    send_templated_mail(
        template_name="application_animal_suggestion",
        from_email=NOTIFICATIONS_SOURCE_EMAIL,
        recipient_list=[suggested_animal.application.fosterer.email],
        context={
            "suggestion": suggested_animal,
            "url_prefix": settings.URL_PREFIX,
        },
    )


def notify_caim_of_animal_suggestion(
    suggested_animal: fosterer.FosterApplicationAnimalSuggestion,
):
    send_templated_mail(
        template_name="application_animal_suggestion_internal",
        from_email=NOTIFICATIONS_SOURCE_EMAIL,
        recipient_list=[INTERNAL_NOTIFICATIONS_EMAIL],
        context={
            "suggestion": suggested_animal,
            "url_prefix": settings.URL_PREFIX,
        },
    )


def notify_caim_foster_application_accepted(application: fosterer.FosterApplication):
    send_templated_mail(
        template_name="application_accepted_internal",
        from_email=NOTIFICATIONS_SOURCE_EMAIL,
        recipient_list=[INTERNAL_NOTIFICATIONS_EMAIL],
        context={
            "app": application,
        },
    )


def notify_caim_foster_application_rejected(application: fosterer.FosterApplication):
    send_templated_mail(
        template_name="application_rejected_internal",
        from_email=NOTIFICATIONS_SOURCE_EMAIL,
        recipient_list=[INTERNAL_NOTIFICATIONS_EMAIL],
        context={
            "app": application,
        },
    )


def notify_new_fosterer_application(application):
    send_templated_mail(
        template_name="new_fosterer_application",
        recipient_list=["hello@caim.org", "al@caim.org"],
        context={"application": application},
        from_email="notifications@caim.org",
    )

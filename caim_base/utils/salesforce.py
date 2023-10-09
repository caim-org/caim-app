from __future__ import annotations
from logging import getLogger
from functools import cache
from django.conf import settings
from simple_salesforce import Salesforce
from simple_salesforce import SalesforceMalformedRequest
from .. import models

logger = getLogger(__name__)


@cache
def _salesforce_connection():
    """create salesforce connection with auth"""
    return Salesforce(
        username=settings.SALESFORCE_USERNAME,
        password=settings.SALESFORCE_PASSWORD,
        security_token=settings.SALESFORCE_SECURITY_TOKEN,
    )


def _create_contact(salesforce_contact, connection):
    logger.info("Enter create contact")

    salesforce_contact["FosterProfile"] = "Incomplete"

    try:
        result = connection.Contact.create(salesforce_contact)

        errors = result.get(
            "errors",
            [
                "key_not_found",
            ],
        )
        if len(errors) > 0:
            logger.error("Create contact errors: %s", ", ".join(errors))
            return

        salesforce_id = result.get("id")
        return salesforce_id
    except SalesforceMalformedRequest:
        logger.exception("Unable to create contact")


def _update_contact(salesforce_id, salesforce_contact, connection):
    try:
        # 204 (no content) results from successful update
        # exceptions thrown on failure
        connection.Contact.update(salesforce_id, salesforce_contact)
    except Exception:
        logger.exception("Not able to update contact")


def _user_from_form(user_form):
    """compile user data from form into object for salesforce"""
    form_data = user_form.cleaned_data

    return {
        "FirstName": form_data.get("first_name"),
        "LastName": form_data.get("last_name"),
        "Email": form_data.get("email"),
        "MailingCity": form_data.get("city"),
        "MailingState": form_data.get("state"),
        "MailingPostalCode": form_data.get("zip_code"),
    }


def _user_profile_to_salesforce_contact(user_profile: models.UserProfile):
    return {
        "FirstName": user_profile.user.first_name,
        "LastName": user_profile.user.last_name,
        "Email": user_profile.user.email,
        "MailingCity": user_profile.city,
        "MailingState": user_profile.state,
        "MailingPostalCode": user_profile.zip_code,
    }


def update_fosterer_profile_complete(user: models.User):
    if not settings.SALESFORCE_ENABLED:
        logger.info("Salesforce not enabled for this environment, skipping")
        return

    try:
        user_profile = models.UserProfile.objects.get(user=user)
        connection = _salesforce_connection()
        connection.Contact.update(
            user_profile.salesforce_id, {"FosterProfile": "Complete"}
        )
    except models.UserProfile.DoesNotExist:
        logger.info("Unable to retrieve UserProfile for user %s", user)
    except Exception:
        logger.exception("Not able to update contact")


def create_or_update_contact(user_profile: models.UserProfile):
    if not settings.SALESFORCE_ENABLED:
        logger.info("Salesforce not enabled for this environment, skipping")
        return

    salesforce_contact = _user_profile_to_salesforce_contact(user_profile)

    if user_profile.salesforce_id is not None:
        _update_contact(
            user_profile.salesforce_id, salesforce_contact, _salesforce_connection()
        )
    else:
        logger.info("salesforce_id is not present, creating new contact")
        salesforce_id = _create_contact(salesforce_contact, _salesforce_connection())
        if salesforce_id:
            logger.info("salesforce id created")
            # update profile with salesforce id
            user_profile.salesforce_id = salesforce_id
            user_profile.save()

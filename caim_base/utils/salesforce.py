from logging import getLogger
from django.conf import settings
from simple_salesforce import Salesforce
from functools import cache

logger = getLogger(__name__)

@cache
def _salesforce_connection():
    """create salesforce connection with auth"""
    return Salesforce(
        username=settings.SALESFORCE_USERNAME,
        password=settings.SALESFORCE_PASSWORD,
        security_token=settings.SALESFORCE_SECURITY_TOKEN,
    )

def _create_contact(user_profile, user_form, connection = _salesforce_connection()):
    logger.info("Enter create contact")
    sf_user = _user_from_form(user_form)

    result = connection.Contact.create(sf_user)

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
    if salesforce_id:
        # update profile with salesforce id
        user_profile.salesforce_id = salesforce_id
        user_profile.save()

    else:
        logger.info("Salesforce id not found")
        return

def _update_contact(salesforce_id, user_form, connection = _salesforce_connection()):
    sf_user = _user_from_form(user_form)

    try:
        # 204 (no content) results from successful update
        # exceptions thrown on failure
        connection.Contact.update(salesforce_id, sf_user)
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

def create_or_update_contact(user_profile, user_form):
    if not settings.SALESFORCE_ENABLED:
        logger.info("Salesforce not enabled for this environment, skipping")
        return

    if user_profile.salesforce_id is not None:
        _update_contact(user_profile.salesforce_id, user_form)
    else:
        _create_contact(user_profile, user_form)

from django.conf import settings
from simple_salesforce import Salesforce


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


def _salesforce_connection():
    """create salesforce connection with auth"""

    return Salesforce(
        username=settings.SALESFORCE_USERNAME,
        password=settings.SALESFORCE_PASSWORD,
        security_token=settings.SALESFORCE_SECURITY_TOKEN,
    )


def create_contact(user_profile, user_form):
    sf = _salesforce_connection()
    sf_user = _user_from_form(user_form)

    result = sf.Contact.create(sf_user)

    errors = result.get(
        "errors",
        [
            "key_not_found",
        ],
    )
    if len(errors) > 0:
        # TODO log
        return

    salesforce_id = result.get("id")
    if salesforce_id:
        # update profile with salesforce id
        user_profile.salesforce_id = salesforce_id
        user_profile.save()

    else:
        # TODO log
        return


def update_contact(salesforce_id, user_form):
    sf = _salesforce_connection()
    sf_user = _user_from_form(user_form)

    try:
        # 204 (no content) results from successful update
        # exceptions thrown on failure
        sf.Contact.update(salesforce_id, sf_user)
    except Exception:
        pass
        # TODO log error

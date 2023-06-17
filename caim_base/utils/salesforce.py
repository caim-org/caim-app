from django.conf import settings
from simple_salesforce import Salesforce


def create_contact(user_profile, user_form):
    form_data = user_form.cleaned_data

    sf_username = settings.SALESFORCE_USERNAME
    sf_password = settings.SALESFORCE_PASSWORD
    sf_security_token = settings.SALESFORCE_SECURITY_TOKEN

    sf = Salesforce(
        username=settings.SALESFORCE_USERNAME,
        password=settings.SALESFORCE_PASSWORD,
        security_token=settings.SALESFORCE_SECURITY_TOKEN,
    )

    sf_user = {
        "FirstName": form_data.get("first_name"),
        "LastName": form_data.get("last_name"),
        "Email": form_data.get("email"),
        "MailingCity": form_data.get("city"),
        "MailingState": form_data.get("state"),
        "MailingPostalCode": form_data.get("zip_code"),
    }

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

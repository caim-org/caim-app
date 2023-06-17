from django.conf import settings
from simple_salesforce import Salesforce


def create_contact(user_form):
    sf_username = settings.SALESFORCE_USERNAME
    sf_password = settings.SALESFORCE_PASSWORD
    sf_security_token = settings.SALESFORCE_SECURITY_TOKEN

    sf = Salesforce(
            username=settings.SALESFORCE_USERNAME,
            password=settings.SALESFORCE_PASSWORD,
            security_token=settings.SALESFORCE_SECURITY_TOKEN
            )

    description = sf.Contact.describe()

    for field in description['fields']:
        print(field['name'])

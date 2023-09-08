import csv
from django.http import HttpResponse
from ...models.user import User, UserProfile
from ...models.fosterer import FostererProfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test


# Download a list of users for upload to salesforce
@login_required()
@user_passes_test(lambda u: u.is_superuser)
def view(request):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="caim-user-list.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(
        [
            "UserId",
            "Email",
            "UserName",
            "DateJoined",
            "DateLastLogin",
            "HasUserProfile",
            "HasFostererProfile",
            "HasAWGMembership",
            "AWG_Ein",
            "AWG_Name",
            "AWG_Type",
        ]
    )

    users = User.objects.all()
    for user in users:
        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            user_profile = None

        try:
            fosterer_profile = FostererProfile.objects.get(user=user)
        except FostererProfile.DoesNotExist:
            fosterer_profile = None

        awg_memberships = user.awgmember_set.all()

        basic_row = [
            user.id,
            user.email,
            user.username,
            user.date_joined,
            user.last_login,
            "TRUE" if user_profile else "FALSE",
            "TRUE" if fosterer_profile else "FALSE",
        ]

        if len(awg_memberships):
            for awg_membership in awg_memberships:
                writer.writerow(
                    [
                        *basic_row,
                        "TRUE",
                        awg_membership.awg.company_ein,
                        awg_membership.awg.name,
                        awg_membership.awg.awg_type,
                    ]
                )
        else:
            writer.writerow([*basic_row, "FALSE"])

    return response

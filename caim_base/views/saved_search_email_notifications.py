# This view is called daily


from templated_email import send_templated_mail

from ..models import SavedSearch
from ..animal_search import query_animals


def send_email(saved_search, animals):
    send_templated_mail(
        template_name="saved_search_daily_digest",
        recipient_list=[saved_search.user.email],
        context={
            "animals": animals,
            "user": saved_search.user,
            "saved_search": saved_search,
        },
        from_email="notifications@caim.org",
    )


def check_new_animals_send_email(saved_search):
    animals = query_animals(
        user=saved_search.user,
        animal_type=str(saved_search.animal_type).upper()
        if saved_search.animal_type
        else None,
        breed=saved_search.breed.slug if saved_search.breed else None,
        zip=saved_search.zip_code,
        radius=saved_search.radius or "any",
        age=saved_search.age,
        size=saved_search.size,
        sex=saved_search.sex,
        euth_date_within_days=saved_search.euth_date_within_days,
        goodwith_cats=saved_search.goodwith_cats,
        goodwith_dogs=saved_search.goodwith_dogs,
        goodwith_kids=saved_search.goodwith_kids,
        # todo published since
    ).all()

    if len(animals) > 0:
        print(f"{saved_search.name} #{saved_search.id}: Animals found matching")
        # Animals to send!
        send_email(saved_search, animals)
    else:
        print(f"{saved_search.name} #{saved_search.id}: No animals found matching")


def send_saved_search_email_notifications(request):
    # @todo just the ones not checked since last time
    saved_searches = SavedSearch.objects.all()

    print(saved_searches)
    for saved_search in saved_searches:
        check_new_animals_send_email(saved_search)

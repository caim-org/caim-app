from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from templated_email import send_templated_mail
from ..models.animals import SavedSearch
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
        radius=saved_search.radius,
        age=saved_search.age,
        size=saved_search.size,
        sex=saved_search.sex,
        euth_date_within_days=saved_search.euth_date_within_days,
        goodwith_cats=saved_search.goodwith_cats,
        goodwith_dogs=saved_search.goodwith_dogs,
        goodwith_kids=saved_search.goodwith_kids,
        # published_since = saved_search.last_checked_at
    ).all()

    # Update the last_checked_at date to now for this search
    # Update this before sending, so that bugs or errors thrown whilst processing
    # dont result in many emails being sent (eg at most once)
    saved_search.last_checked_at = datetime.utcnow()
    saved_search.save()

    if len(animals) > 0:
        print(
            f"{saved_search.name} #{saved_search.id}: Animals found for search. Sending."
        )
        send_email(saved_search, animals)
    else:
        print(
            f"{saved_search.name} #{saved_search.id}: No animals found for search. Skipping."
        )


# This view is called every hour by a cron rule (EventBridge rule)
@require_http_methods(["POST"])
@csrf_exempt
def send_saved_search_email_notifications(request):
    saved_searches = SavedSearch.objects.all()

    for saved_search in saved_searches:
        print(f"{saved_search.name} #{saved_search.id}: Processing")
        if saved_search.is_ready_to_check():
            print("Checking search as ready to check")
            check_new_animals_send_email(saved_search)
        else:
            print("Skipping as not ready to check")

    return JsonResponse({"ok": True})

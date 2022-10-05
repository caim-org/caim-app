from datetime import datetime
from django.core.exceptions import BadRequest, PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, render
from ..models import Animal, AnimalComment
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from ..notifications import notify_animal_comment


@login_required()
@require_http_methods(["POST"])
def add(request):
    if not request.POST["animalId"]:
        raise BadRequest("Missing params")
    animal = Animal.objects.filter(id=request.POST["animalId"]).first()
    if not animal:
        raise BadRequest("Params invalid")
    body = request.POST["body"].strip()
    if not body:
        raise BadRequest("Params invalid")
    comment = AnimalComment(user=request.user, animal=animal, body=body)
    comment.save()

    # try:
    notify_animal_comment(comment)
    # except:
    #    print("Could not send notifications")

    return redirect(f"{animal.get_absolute_url()}#comment-{comment.id}")


@login_required()
@require_http_methods(["POST", "GET"])
def edit(request, comment_id):
    try:
        comment = AnimalComment.objects.get(id=comment_id)
    except AnimalComment.DoesNotExist:
        raise Http404("Comment not found")
    animal = comment.animal

    if not comment.can_be_edited_by(request.user):
        raise PermissionDenied("User does not have permission to edit this comment")

    if request.method == "POST" and request.POST["body"]:
        comment.body = request.POST["body"].strip()
        comment.edited_at = datetime.now()
        comment.save()
        return redirect(f"{animal.get_absolute_url()}#comment-{comment.id}")
    else:
        return render(
            request,
            "comments/edit.html",
            {
                "pageTitle": "Delete comment",
                "comment": comment,
                "animal": animal,
            },
        )


@login_required()
@require_http_methods(["POST", "GET"])
def delete(request, comment_id):
    if not request.user.is_authenticated:
        raise PermissionDenied("Must be logged in")
    try:
        comment = AnimalComment.objects.get(id=comment_id)
    except AnimalComment.DoesNotExist:
        raise Http404("Comment not found")
    animal = comment.animal

    if not comment.can_be_deleted_by(request.user):
        raise PermissionDenied("User does not have permission to delete this comment")

    if request.method == "POST":
        comment.delete()
        return redirect(f"{animal.get_absolute_url()}#comments")
    else:
        return render(
            request,
            "comments/delete.html",
            {
                "pageTitle": "Delete comment",
                "comment": comment,
                "animal": animal,
            },
        )

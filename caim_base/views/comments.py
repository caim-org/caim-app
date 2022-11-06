from django.urls import reverse, reverse_lazy
from datetime import datetime
from django.core.exceptions import BadRequest, PermissionDenied
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.shortcuts import redirect, render
from ..models.animals import Animal, AnimalComment, AnimalSubComment
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from ..notifications import notify_animal_comment, notify_animal_comment_reply


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


class CreateSubComment(LoginRequiredMixin, CreateView):
    model = AnimalSubComment
    fields = ["body"]

    def form_valid(self, form):
        is_ajax = self.request.headers.get("x-requested-with") == "XMLHttpRequest"
        if is_ajax:
            comment_id = self.request.POST.get("comment_id")
            comment = AnimalComment.objects.get(pk=comment_id)
            form.instance.comment = comment
            form.instance.user = self.request.user
            form.instance.body = self.request.POST.get("body")
            notify_animal_comment_reply(form.instance)
        return super(CreateSubComment, self).form_valid(form)

    def get_success_url(self):
        comment = AnimalComment.objects.get(pk=self.kwargs["comment_id"])
        return reverse_lazy("animal", kwargs={"animal_id": comment.animal.id})


class SubCommentEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = AnimalSubComment
    fields = ["body"]
    template_name = "comments/edit_reply.html"

    def test_func(self):
        reply = self.get_object()
        if reply.can_be_edited_by(self.request.user):
            return True
        else:
            return False


class SubCommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = AnimalSubComment
    template_name = "comments/delete_reply.html"
    fields = []

    def test_func(self):
        reply = self.get_object()
        if reply.can_be_deleted_by(self.request.user):
            return True
        else:
            return False

    def get_success_url(self):
        reply = self.get_object()
        return reverse_lazy("animal", kwargs={"animal_id": reply.comment.animal.id})

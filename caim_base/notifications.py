from templated_email import send_templated_mail


def notify_new_awg_application(awg):
    send_templated_mail(
        template_name="new_awg_application",
        recipient_list=["hello@caim.org"],
        context={"awg": awg},
        from_email="notifications@caim.org",
    )


def notify_animal_comment(comment):
    # AWG staff
    animal = comment.animal
    awg = animal.awg
    members = awg.awgmember_set.all()
    emails = [str(member.user.email) for member in members]
    send_templated_mail(
        template_name="new_animal_comment",
        recipient_list=emails,
        context={"awg": awg, "animal": animal, "comment": comment},
        from_email="notifications@caim.org",
    )


def notify_animal_comment_reply(subcomment):
    comment = subcomment.comment
    animal = comment.animal
    subcomments = comment.get_sub_comments()
    emails = [str(subcomment.user.email) for subcomment in subcomments]
    emails.append(str(comment.user.email))
    emails = list(set(emails))
    send_templated_mail(
        template_name="new_animal_comment_reply",
        recipient_list=emails,
        context={"animal": animal},
        from_email="notifications@caim.org",
    )


def notify_animal_published(animal):
    pass


def notify_new_fosterer_profile(fosterer):
    send_templated_mail(
        template_name="new_fosterer_profile",
        recipient_list=["hello@caim.org", "al@caim.org"],
        context={"fosterer": fosterer},
        from_email="notifications@caim.org",
    )

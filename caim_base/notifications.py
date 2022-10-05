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
    # @todo add parent comment author
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


def notify_animal_published(animal):
    pass

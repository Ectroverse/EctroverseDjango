def get_userstatus_from_id_or_name(detail):
    try:
        detail = int(detail)
    except ValueError:
        detail = str(detail)

    faction_setting = None
    err_msg = ""

    if isinstance(detail, int):
        if UserStatus.objects.filter(id=detail).first() is None:
            err_msg = "The faction id " + str(detail) + " doesn't exist for setting # " + str(i) + "!"
        else:
            faction_setting = UserStatus.objects.filter(id=detail).first()
    else:
        if UserStatus.objects.filter(user_name=detail).first() is None:
            err_msg = "The faction name " + str(detail) + " doesn't exist for setting # " + str(i) + "!"
        else:
            faction_setting = UserStatus.objects.filter(user_name=detail).first()

    return faction_setting, err_msg
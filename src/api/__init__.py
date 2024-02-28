# TODO: this is a placeholder replacement for the original
#   get_user_preferences_attributes() return value from the
#   internal cas repo, as this was angewandte_auth specific.
def get_user_preferences_attributes(user):
    attrs = {
        'display_name': user.get_full_name(),
        'name': user.get_full_name(),
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'title': None,
        'permissions': [],
        'groups': [],
    }
    if hasattr(user, 'userpreferencesdata'):
        attrs.update(user.userpreferencesdata.attrs_dict)
    if not attrs.get('settings', {}).get('showroom', {}).get('activate_profile'):
        # set showroom_id to None if page is not activated
        attrs['showroom_id'] = None
    return attrs

def get_attributes(user, service):
    """
    Get CAS Attributes sent to services

    :param user: User instance
    :param service: Current service
    :param version: Which type of key naming to use
    :return: Dictionary of attributes to send
    """
    return {
        "display_name": user.get_full_name(),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "groups": list(user.groups.values_list('name', flat=True)),
    }

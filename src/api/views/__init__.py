from django.contrib.auth import get_user_model
from django.db.models import Q


def autosuggest_user_search(searchstr):
    # This is kind of buggy, but a fix, after removing apimapper.
    # As autosuggest is only a transitional phase, before completely switching to autocomplete,
    # now both expertise and users
    # can be queried in the old autosuggest the same way they were with the fetch_responses().

    User = get_user_model()  # noqa: N806
    search_result = User.objects.filter(
        Q(first_name__icontains=searchstr) | Q(last_name__icontains=searchstr),
    )
    return [
        {
            'UUID': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'label': user.get_full_name(),
        }
        for user in search_result
    ]

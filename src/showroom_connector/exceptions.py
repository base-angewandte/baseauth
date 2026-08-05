class ShowroomError(Exception):
    pass


class ShowroomAuthenticationError(ShowroomError):
    pass


class ShowroomUndefinedError(ShowroomError):
    pass


class ShowroomNotFoundError(ShowroomError):
    pass

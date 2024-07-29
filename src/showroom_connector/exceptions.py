class ShowroomException(Exception):
    pass


class ShowroomAuthenticationException(ShowroomException):
    pass


class ShowroomUndefinedException(ShowroomException):
    pass


class ShowroomNotFoundException(ShowroomException):
    pass

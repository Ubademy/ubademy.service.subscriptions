class UserAlreadyEnrolledError(Exception):
    message = "The user you specified is already enrolled."

    def __str__(self):
        return UserAlreadyEnrolledError.message


class UserNotEnrolledError(Exception):
    message = "The user you specified is not enrolled."

    def __str__(self):
        return UserNotEnrolledError.message

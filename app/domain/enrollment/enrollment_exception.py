class UserAlreadyEnrolledError(Exception):
    message = "The user you specified is already enrolled."

    def __str__(self):
        return UserAlreadyEnrolledError.message

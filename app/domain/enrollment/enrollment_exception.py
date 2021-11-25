class UserAlreadyEnrolledError(Exception):
    message = "The user you specified is already enrolled."

    def __str__(self):
        return UserAlreadyEnrolledError.message


class UserNotEnrolledError(Exception):
    message = "The user you specified is not enrolled."

    def __str__(self):
        return UserNotEnrolledError.message


class NoEnrollmentPermissionError(Exception):
    message = "User needs a better subscription in order to enroll in this course."

    def __str__(self):
        return NoEnrollmentPermissionError.message

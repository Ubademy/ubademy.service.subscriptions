class NoStudentsInCourseError(Exception):
    message = "The course you specified has no students."

    def __str__(self):
        return NoStudentsInCourseError.message


class UserNotFoundError(Exception):
    message = "The user you specified was never enrolled in any course."

    def __str__(self):
        return NoStudentsInCourseError.message


class StudentNotEnrolledError(Exception):
    message = "The user you specified is not enrolled in any course."

    def __str__(self):
        return NoStudentsInCourseError.message


class InvalidCredentialsError(Exception):
    message = "Invalid credentials."

    def __str__(self):
        return InvalidCredentialsError.message

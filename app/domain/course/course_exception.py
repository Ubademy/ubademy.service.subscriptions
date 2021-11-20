class CourseNotFoundError(Exception):
    message = "The course you specified does not exist."

    def __str__(self):
        return CourseNotFoundError.message


class CoursesNotFoundError(Exception):
    message = "No courses were found."

    def __str__(self):
        return CoursesNotFoundError.message

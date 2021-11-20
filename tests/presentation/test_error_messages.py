from app.presentation.schema.course.course_error_message import (
    ErrorMessageCourseNotFound,
    ErrorMessageCoursesNotFound,
)
from app.presentation.schema.enrollment.enrollment_error_message import (
    ErrorMessageUserAlreadyEnrolled,
)
from app.presentation.schema.user.enrollment_error_message import (
    ErrorMessageInvalidCredentials,
)


class TestErrorMessages:
    def test_error_messages(self):
        assert ErrorMessageCourseNotFound is not ErrorMessageCoursesNotFound
        assert ErrorMessageUserAlreadyEnrolled is not ErrorMessageInvalidCredentials

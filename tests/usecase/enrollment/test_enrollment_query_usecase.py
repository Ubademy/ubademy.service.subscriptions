from unittest.mock import MagicMock, Mock

import pytest

from app.domain.user.user_exception import (
    NoStudentsInCourseError,
    StudentNotEnrolledError,
)
from app.infrastructure.enrollment.enrollment_query_service import (
    EnrollmentQueryServiceImpl,
)
from app.usecase.enrollment.enrollment_query_usecase import EnrollmentQueryUseCaseImpl
from tests.params import no_enrollments


class TestEnrollmentQueryUseCase:
    def test_fetch_users_from_course_should_raise_no_students_in_course_error(self):
        session = MagicMock()
        session.query().filter_by().all = Mock(side_effect=no_enrollments)
        enr_query_service = EnrollmentQueryServiceImpl(session)
        enr_query = EnrollmentQueryUseCaseImpl(enr_query_service)
        with pytest.raises(NoStudentsInCourseError):
            enr_query.fetch_users_from_course(id="course_1", only_active=True)

    def test_fetch_courses_from_user_should_raise_no_students_in_course_error(self):
        session = MagicMock()
        session.query().filter_by().all = Mock(side_effect=no_enrollments)
        enr_query_service = EnrollmentQueryServiceImpl(session)
        enr_query = EnrollmentQueryUseCaseImpl(enr_query_service)
        with pytest.raises(StudentNotEnrolledError):
            enr_query.fetch_courses_from_user(id="user_1")

    def test_get_enrollment_metrics(self):
        session = MagicMock()
        session.query().filter().group_by().all = Mock(return_value=[("course_1", 1)])
        enr_query_service = EnrollmentQueryServiceImpl(session)
        enr_query = EnrollmentQueryUseCaseImpl(enr_query_service)

        metrics, count = enr_query.get_enrollment_metrics(
            limit=1, min_timestamp=0, max_timestamp=100
        )

        assert len(metrics) == 1
        assert count == 1
        assert metrics[0].course_id == "course_1"

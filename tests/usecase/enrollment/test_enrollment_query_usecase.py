from unittest.mock import MagicMock, Mock

from app.infrastructure.enrollment.enrollment_query_service import (
    EnrollmentQueryServiceImpl,
)
from app.usecase.enrollment.enrollment_query_usecase import EnrollmentQueryUseCaseImpl
from tests.params import filter_by_course_id, filter_by_user_id


class TestEnrollmentQueryUseCase:
    def test_fetch_students_from_course_should_return_only_active_students(self):
        session = MagicMock()
        session.query().filter_by = Mock(side_effect=filter_by_course_id)
        enr_query_service = EnrollmentQueryServiceImpl(session)
        enr_query = EnrollmentQueryUseCaseImpl(enr_query_service)
        students = enr_query.fetch_students_from_course(id="course_1", only_active=True)

        assert len(students) == 1
        assert students[0] == "user_1"

    def test_fetch_courses_from_student_should_return_only_active_students(self):
        session = MagicMock()
        session.query().filter_by = Mock(side_effect=filter_by_user_id)
        enr_query_service = EnrollmentQueryServiceImpl(session)
        enr_query = EnrollmentQueryUseCaseImpl(enr_query_service)
        courses = enr_query.fetch_courses_from_student(id="user_1", only_active=True)

        assert len(courses) == 1
        assert courses[0] == "course_1"

from unittest.mock import MagicMock, Mock

import pytest
from sqlalchemy.exc import NoResultFound

from app.domain.enrollment.enrollment_exception import (
    UserAlreadyEnrolledError,
    UserNotEnrolledError,
)
from app.infrastructure.enrollment.enrollment_repository import (
    EnrollmentCommandUseCaseUnitOfWorkImpl,
    EnrollmentRepositoryImpl,
)
from app.usecase.enrollment.enrollment_command_usecase import (
    EnrollmentCommandUseCaseImpl,
)
from tests.params import already_enrolled, filter_by_id_user_1_course_1, no_enrollments


class TestEnrollmentCommandUseCase:
    def test_enroll_should_return_enrollment(self):
        session = MagicMock()
        session.query().filter_by = Mock(side_effect=no_enrollments)
        enrollment_repository = EnrollmentRepositoryImpl(session)
        uow = EnrollmentCommandUseCaseUnitOfWorkImpl(
            session=session, enrollment_repository=enrollment_repository
        )
        enr_command = EnrollmentCommandUseCaseImpl(uow=uow)

        enr = enr_command.enroll("user_1", "course_1")

        assert enr.user_id == "user_1"
        assert enr.course_id == "course_1"

    def test_enroll_should_raise_user_already_enrolled_error(self):
        session = MagicMock()
        session.query().filter_by().one = Mock(side_effect=already_enrolled)
        enrollment_repository = EnrollmentRepositoryImpl(session)
        uow = EnrollmentCommandUseCaseUnitOfWorkImpl(
            session=session, enrollment_repository=enrollment_repository
        )
        enr_command = EnrollmentCommandUseCaseImpl(uow=uow)

        with pytest.raises(UserAlreadyEnrolledError):
            enr_command.enroll("user_1", "course_1")

    def test_unenroll_should_return_enrollment(self):
        session = MagicMock()
        session.query().filter_by = Mock(side_effect=filter_by_id_user_1_course_1)
        enrollment_repository = EnrollmentRepositoryImpl(session)
        uow = EnrollmentCommandUseCaseUnitOfWorkImpl(
            session=session, enrollment_repository=enrollment_repository
        )
        enr_command = EnrollmentCommandUseCaseImpl(uow=uow)

        enr = enr_command.unenroll("user_1", "course_1")

        assert enr.user_id == "user_1"
        assert enr.course_id == "course_1"
        assert not enr.active

    def test_unenroll_should_raise_user_not_enrolled_error(self):
        session = MagicMock()
        session.query().filter_by().one = Mock(side_effect=NoResultFound)
        enrollment_repository = EnrollmentRepositoryImpl(session)
        uow = EnrollmentCommandUseCaseUnitOfWorkImpl(
            session=session, enrollment_repository=enrollment_repository
        )
        enr_command = EnrollmentCommandUseCaseImpl(uow=uow)

        with pytest.raises(UserNotEnrolledError):
            enr_command.unenroll("user_1", "course_1")

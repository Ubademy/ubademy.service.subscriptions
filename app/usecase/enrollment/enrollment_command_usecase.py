from abc import ABC, abstractmethod
from typing import Optional, cast

import shortuuid

from app.domain.enrollment.enrollment import Enrollment
from app.domain.enrollment.enrollment_exception import (
    UserAlreadyEnrolledError,
    UserNotEnrolledError,
)
from app.domain.enrollment.enrollment_repository import EnrollmentRepository
from app.usecase.enrollment.enrollment_query_model import EnrollmentReadModel


class EnrollmentCommandUseCaseUnitOfWork(ABC):

    enrollment_repository: EnrollmentRepository

    @abstractmethod
    def begin(self):
        raise NotImplementedError

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError


class EnrollmentCommandUseCase(ABC):
    @abstractmethod
    def enroll(self, user_id: str, course_id: str) -> Optional[EnrollmentReadModel]:
        raise NotImplementedError

    @abstractmethod
    def unenroll(self, user_id: str, course_id: str) -> Optional[EnrollmentReadModel]:
        raise NotImplementedError

    @abstractmethod
    def unenroll_all(self, course_id: str):
        raise NotImplementedError


class EnrollmentCommandUseCaseImpl(EnrollmentCommandUseCase):
    def __init__(
        self,
        uow: EnrollmentCommandUseCaseUnitOfWork,
    ):
        self.uow: EnrollmentCommandUseCaseUnitOfWork = uow

    def enroll(self, user_id: str, course_id: str) -> Optional[EnrollmentReadModel]:
        try:
            uuid = shortuuid.uuid()
            enrollment = Enrollment(
                id=uuid,
                user_id=user_id,
                course_id=course_id,
                active=True,
            )

            if self.uow.enrollment_repository.has_active_user(
                user_id=user_id, course_id=course_id
            ):
                raise UserAlreadyEnrolledError
            self.uow.enrollment_repository.enroll(enrollment)
            self.uow.commit()

            created_enrollment = self.uow.enrollment_repository.find_by_id(uuid)
        except:
            self.uow.rollback()
            raise

        return EnrollmentReadModel.from_entity(cast(Enrollment, created_enrollment))

    def unenroll(self, user_id: str, course_id: str) -> Optional[EnrollmentReadModel]:
        try:
            if not self.uow.enrollment_repository.has_active_user(
                user_id=user_id, course_id=course_id
            ):
                raise UserNotEnrolledError
            enrollment = self.uow.enrollment_repository.unenroll(
                user_id=user_id, course_id=course_id
            )
            self.uow.commit()

        except:
            self.uow.rollback()
            raise

        return EnrollmentReadModel.from_entity(cast(Enrollment, enrollment))

    def unenroll_all(self, course_id: str):
        try:
            self.uow.enrollment_repository.unenroll_all(course_id=course_id)
            self.uow.commit()
        except:
            self.uow.rollback()
            raise

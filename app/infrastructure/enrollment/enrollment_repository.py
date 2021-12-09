from typing import Optional

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.domain.enrollment.enrollment import Enrollment
from app.domain.enrollment.enrollment_exception import UserNotEnrolledError
from app.domain.enrollment.enrollment_repository import EnrollmentRepository
from app.infrastructure.enrollment.enrollment_dto import EnrollmentDTO
from app.usecase.enrollment.enrollment_command_usecase import (
    EnrollmentCommandUseCaseUnitOfWork,
)


class EnrollmentRepositoryImpl(EnrollmentRepository):
    def __init__(self, session: Session):
        self.session: Session = session

    def has_active_user(self, user_id: str, course_id: str) -> bool:
        try:
            self.session.query(EnrollmentDTO).filter_by(
                user_id=user_id, course_id=course_id, active=True
            ).one()
        except NoResultFound:
            return False
        return True

    def enroll(self, enrollment: Enrollment):
        enr_dto = EnrollmentDTO.from_entity(enrollment)
        try:
            self.session.add(enr_dto)
        except:
            raise

    def unenroll(self, user_id: str, course_id: str) -> Optional[Enrollment]:
        try:
            enr_dto = (
                self.session.query(EnrollmentDTO)
                .filter_by(user_id=user_id, course_id=course_id, active=True)
                .one()
            )
            enr_dto.active = False
        except NoResultFound:
            raise UserNotEnrolledError
        except:
            raise

        return enr_dto.to_entity()

    def unenroll_all(self, course_id: str):
        try:
            enr_dtos = (
                self.session.query(EnrollmentDTO)
                .filter_by(course_id=course_id, active=True)
                .all()
            )
            for i in enr_dtos:
                i.active = False
        except:
            raise

    def find_by_id(self, uuid: str) -> Optional[Enrollment]:
        try:
            enr_dto = self.session.query(EnrollmentDTO).filter_by(id=uuid).one()
        except NoResultFound:
            return None
        except:
            raise

        return enr_dto.to_entity()


class EnrollmentCommandUseCaseUnitOfWorkImpl(EnrollmentCommandUseCaseUnitOfWork):
    def __init__(
        self,
        session: Session,
        enrollment_repository: EnrollmentRepository,
    ):
        self.session: Session = session
        self.enrollment_repository: EnrollmentRepository = enrollment_repository

    def begin(self):
        self.session.begin()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

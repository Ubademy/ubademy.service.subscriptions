from datetime import datetime
from typing import Union

from sqlalchemy import BigInteger, Boolean, Column, String

from app.domain.enrollment.enrollment import Enrollment
from app.infrastructure.database import Base
from app.usecase.enrollment.enrollment_query_model import EnrollmentReadModel


def unixtimestamp() -> int:
    return int(datetime.now().timestamp() * 1000)


class EnrollmentDTO(Base):

    __tablename__ = "enrollments"
    id: Union[str, Column] = Column(String, primary_key=True, autoincrement=False)
    user_id: Union[str, Column] = Column(String, nullable=False, autoincrement=False)
    course_id: Union[str, Column] = Column(String, nullable=False, autoincrement=False)
    active: Union[bool, Column] = Column(Boolean, nullable=False)
    updated_at: Union[int, Column] = Column(BigInteger, nullable=False)

    def to_entity(self) -> Enrollment:
        return Enrollment(
            id=self.id,
            user_id=self.user_id,
            course_id=self.course_id,
            active=self.active,
            updated_at=self.updated_at,
        )

    def to_read_model(self) -> EnrollmentReadModel:
        return EnrollmentReadModel(
            id=self.id,
            user_id=self.user_id,
            course_id=self.course_id,
            active=self.active,
            updated_at=self.updated_at,
        )

    @staticmethod
    def from_entity(enrollment: Enrollment) -> "EnrollmentDTO":
        now = unixtimestamp()
        return EnrollmentDTO(
            id=enrollment.id,
            user_id=enrollment.user_id,
            course_id=enrollment.course_id,
            active=enrollment.active,
            updated_at=now,
        )

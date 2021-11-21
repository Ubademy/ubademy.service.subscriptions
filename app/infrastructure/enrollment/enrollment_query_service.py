from typing import List

from sqlalchemy.orm.session import Session

from ...usecase.enrollment.enrollment_query_model import EnrollmentReadModel
from ...usecase.enrollment.enrollment_query_service import EnrollmentQueryService
from .enrollment_dto import EnrollmentDTO


class EnrollmentQueryServiceImpl(EnrollmentQueryService):
    def __init__(self, session: Session):
        self.session: Session = session

    def fetch_enrollments_from_course(self, id: str) -> List[EnrollmentReadModel]:
        try:
            enr_dtos = self.session.query(EnrollmentDTO).filter_by(course_id=id).all()
        except:
            raise
        if len(enr_dtos) == 0:
            return []

        return list(map(lambda enr_dto: enr_dto.to_read_model(), enr_dtos))

    def fetch_enrollments_from_user(self, id: str) -> List[EnrollmentReadModel]:
        try:
            enr_dtos = self.session.query(EnrollmentDTO).filter_by(user_id=id).all()
        except:
            raise
        if len(enr_dtos) == 0:
            return []

        return list(map(lambda enr_dto: enr_dto.to_read_model(), enr_dtos))

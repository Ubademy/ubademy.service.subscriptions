from typing import List, Tuple

from sqlalchemy import func
from sqlalchemy.orm.session import Session

from ...usecase.enrollment.enrollment_query_model import EnrollmentReadModel
from ...usecase.enrollment.enrollment_query_service import EnrollmentQueryService
from ...usecase.metrics.enrollment_metrics_query_model import EnrollmentMetricsReadModel
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

    def get_enrollment_metrics(
        self, limit: int
    ) -> Tuple[List[EnrollmentMetricsReadModel], int]:
        try:
            enr_tuples = (
                self.session.query(
                    EnrollmentDTO.course_id, func.count(EnrollmentDTO.course_id)
                )
                .group_by(EnrollmentDTO.course_id)
                .all()
            )
            enrollments = list(
                map(
                    lambda e: EnrollmentMetricsReadModel(course_id=e[0], count=e[1]),
                    enr_tuples,
                )
            )
            enrollments = sorted(enrollments, key=lambda x: x.count, reverse=True)

        except:
            raise

        return enrollments[0:limit], len(enrollments)

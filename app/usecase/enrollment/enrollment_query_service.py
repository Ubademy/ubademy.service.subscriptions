from abc import ABC, abstractmethod
from typing import List, Tuple

from ..metrics.enrollment_metrics_query_model import EnrollmentMetricsReadModel
from .enrollment_query_model import EnrollmentReadModel


class EnrollmentQueryService(ABC):
    @abstractmethod
    def fetch_enrollments_from_course(self, id: str) -> List[EnrollmentReadModel]:
        raise NotImplementedError

    @abstractmethod
    def fetch_enrollments_from_user(self, id: str) -> List[EnrollmentReadModel]:
        raise NotImplementedError

    @abstractmethod
    def get_enrollment_metrics(
        self,
        limit: int,
        min_timestamp: int,
        max_timestamp: int,
    ) -> Tuple[List[EnrollmentMetricsReadModel], int]:
        raise NotImplementedError

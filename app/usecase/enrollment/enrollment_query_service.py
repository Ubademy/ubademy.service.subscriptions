from abc import ABC, abstractmethod
from typing import List

from .enrollment_query_model import EnrollmentReadModel


class EnrollmentQueryService(ABC):
    @abstractmethod
    def fetch_enrollments_from_course(self, id: str) -> List[EnrollmentReadModel]:
        raise NotImplementedError

    @abstractmethod
    def fetch_enrollments_from_student(self, id: str) -> List[EnrollmentReadModel]:
        raise NotImplementedError

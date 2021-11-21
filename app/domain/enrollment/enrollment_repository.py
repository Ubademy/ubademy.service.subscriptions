from abc import ABC, abstractmethod
from typing import Optional

from app.domain.enrollment.enrollment import Enrollment


class EnrollmentRepository(ABC):
    @abstractmethod
    def has_active_user(self, user_id: str, course_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def enroll(self, enrollment: Enrollment):
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, uuid: str) -> Optional[Enrollment]:
        raise NotImplementedError

    @abstractmethod
    def unenroll(self, user_id: str, course_id: str) -> Optional[Enrollment]:
        raise NotImplementedError

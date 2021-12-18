from abc import ABC, abstractmethod
from typing import List

from ...domain.user.user_exception import (
    NoStudentsInCourseError,
    StudentNotEnrolledError,
)
from .enrollment_query_service import EnrollmentQueryService


class EnrollmentQueryUseCase(ABC):
    @abstractmethod
    def fetch_users_from_course(self, id: str, only_active: bool) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def fetch_courses_from_user(self, id: str) -> dict:
        raise NotImplementedError


class EnrollmentQueryUseCaseImpl(EnrollmentQueryUseCase):
    def __init__(self, enrollment_query_service: EnrollmentQueryService):
        self.enrollment_query_service: EnrollmentQueryService = enrollment_query_service

    def fetch_users_from_course(self, id: str, only_active: bool) -> List[str]:
        try:
            enrollments = self.enrollment_query_service.fetch_enrollments_from_course(
                id
            )
            if only_active:
                enrollments = list(filter(lambda enr: enr.is_active(), enrollments))
            if len(enrollments) == 0:
                raise NoStudentsInCourseError
            r = list(map(lambda enr: enr.get_user_id(), enrollments))

        except:
            raise

        return r

    def fetch_courses_from_user(self, id: str) -> dict:
        try:
            enrollments = self.enrollment_query_service.fetch_enrollments_from_user(id)
            enrolled = list(filter(lambda enr: enr.is_active(), enrollments))
            unenrolled = list(filter(lambda enr: not enr.is_active(), enrollments))

            enr_list = {
                "enrolled": list(map(lambda enr: enr.get_course_id(), enrolled)),
                "unenrolled": list(map(lambda enr: enr.get_course_id(), unenrolled)),
            }
            enr_list["unenrolled"] = list(
                filter(lambda e: e not in enr_list["enrolled"], enr_list["unenrolled"])
            )

            if len(enrollments) == 0:
                raise StudentNotEnrolledError

        except:
            raise

        return enr_list

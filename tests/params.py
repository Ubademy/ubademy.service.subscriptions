from unittest.mock import MagicMock, Mock

from sqlalchemy.exc import NoResultFound

from app.domain.enrollment.enrollment import Enrollment
from app.infrastructure.enrollment.enrollment_dto import EnrollmentDTO
from app.infrastructure.subscription.subscription_dto import SubscriptionDTO

enr_1_active = Enrollment(
    id="enr_1",
    user_id="user_1",
    course_id="course_1",
    active=True,
)

enr_1_inactive = Enrollment(
    id="enr_1",
    user_id="user_1",
    course_id="course_1",
    active=False,
)

enr_2_active = Enrollment(
    id="enr_2",
    user_id="user_2",
    course_id="course_2",
    active=True,
)

enr_dto_1_active = EnrollmentDTO(
    id="enr_1",
    user_id="user_1",
    course_id="course_1",
    active=True,
    updated_at=123,
)

enr_dto_1_inactive = EnrollmentDTO(
    id="enr_1_inactive",
    user_id="user_1",
    course_id="course_1",
    active=False,
    updated_at=123,
)

sub_dto_1_active = SubscriptionDTO(
    id="enr_1",
    user_id="user_1",
    sub_id=0,
    active=True,
    updated_at=123,
)

sub_dto_0_active = SubscriptionDTO(
    id="enr_1",
    user_id="user_1",
    sub_id=0,
    active=True,
    updated_at=123,
)

sub_dto_1_inactive = SubscriptionDTO(
    id="enr_1",
    user_id="user_1",
    sub_id=0,
    active=False,
    updated_at=123,
)


enrollment_dtos = [enr_dto_1_active, enr_dto_1_inactive]

q_enr_1 = MagicMock()
q_enr_1.one = Mock(return_value=enr_dto_1_active)

filtered = []

q_all_enr = MagicMock()
q_all_enr.all = Mock(return_value=filtered)


q_sub_1 = MagicMock()
q_sub_1.one = Mock(return_value=sub_dto_1_active)


def no_enrollments(id=None, user_id=None, course_id=None, active=None):
    if active:
        raise NoResultFound
    if id == "random":
        return user_id, course_id
    return q_enr_1


def no_susbcriptions(id=None, user_id=None, sub_id=None, active=None):
    if active and sub_id is not None:
        raise NoResultFound
    if id == "random":
        return user_id, sub_id
    return q_sub_1


def already_enrolled(id=None, user_id=None, course_id=None, active=None):
    if id == "random":
        return user_id, course_id, active
    return True


def already_subscribed(id=None, user_id=None, sub_id=None, active=None):
    if id == "random":
        return user_id, sub_id, active
    return True


mocked_enr_1_active = MagicMock()
mocked_enr_1_active.one = Mock(return_value=enr_dto_1_active)

mocked_sub_0_active = MagicMock()
mocked_sub_0_active.one = Mock(return_value=sub_dto_0_active)

mocked_sub_1_inactive = MagicMock()
mocked_sub_1_inactive.one = Mock(return_value=sub_dto_1_inactive)


def filter_by_id_user_1_course_1(user_id=None, course_id=None, active=None):
    if user_id == "user_1" and course_id == "course_1" and active:
        return mocked_enr_1_active
    raise NoResultFound


def filter_by_id_user_1_sub_1(id=None, user_id=None, sub_id=None, active=None):
    if id is not None and sub_id is None:
        return mocked_sub_0_active
    if user_id == "user_1" and active and sub_id is None:
        return mocked_sub_1_inactive
    raise NoResultFound


def filter_by_user_id(user_id: str):
    filtered.clear()
    for i in enrollment_dtos:
        if i.user_id == user_id:
            filtered.append(i)
    return q_all_enr


def filter_by_course_id(course_id: str):
    filtered.clear()
    for i in enrollment_dtos:
        if i.course_id == course_id:
            filtered.append(i)
    return q_all_enr

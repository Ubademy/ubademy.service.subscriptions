import ast
import json
import logging
import os
from datetime import datetime
from logging import config
from typing import Iterator, List

import requests
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm.session import Session
from starlette.requests import Request

from app.domain.course import CourseNotFoundError
from app.domain.enrollment.enrollment_exception import (
    NoEnrollmentPermissionError,
    UserAlreadyEnrolledError,
    UserNotEnrolledError,
)
from app.domain.enrollment.enrollment_repository import EnrollmentRepository
from app.domain.subscription.subscription_exception import (
    SubTypeNotFoundError,
    UserAlreadySubscribedError,
    UserNotSubscribedError,
)
from app.domain.subscription.subscription_repository import SubscriptionRepository
from app.domain.user.user_exception import (
    InvalidCredentialsError,
    NoStudentsInCourseError,
    StudentNotEnrolledError,
)
from app.infrastructure.database import SessionLocal, create_tables
from app.infrastructure.enrollment.enrollment_query_service import (
    EnrollmentQueryServiceImpl,
)
from app.infrastructure.enrollment.enrollment_repository import (
    EnrollmentCommandUseCaseUnitOfWorkImpl,
    EnrollmentRepositoryImpl,
)
from app.infrastructure.subscription.subscription_query_service import (
    SubscriptionQueryServiceImpl,
)
from app.infrastructure.subscription.subscription_repository import (
    SubscriptionCommandUseCaseUnitOfWorkImpl,
    SubscriptionRepositoryImpl,
)
from app.presentation.schema.course.course_error_message import (
    ErrorMessageCourseNotFound,
)
from app.presentation.schema.enrollment.enrollment_error_message import (
    ErrorMessageUserAlreadyEnrolled,
    ErrorMessageUserNotEnrolled,
)
from app.presentation.schema.subscription.subscription_error_message import (
    ErrorMessageSubTypeNotFound,
    ErrorMessageUserAlreadySubscribed,
    ErrorMessageUserNotSubscribed,
)
from app.presentation.schema.user.enrollment_error_message import (
    ErrorMessageInvalidCredentials,
)
from app.usecase.course.course_query_model import CoursesListReadModel
from app.usecase.enrollment.enrollment_command_usecase import (
    EnrollmentCommandUseCase,
    EnrollmentCommandUseCaseImpl,
    EnrollmentCommandUseCaseUnitOfWork,
)
from app.usecase.enrollment.enrollment_query_model import EnrollmentReadModel
from app.usecase.enrollment.enrollment_query_service import EnrollmentQueryService
from app.usecase.enrollment.enrollment_query_usecase import (
    EnrollmentQueryUseCase,
    EnrollmentQueryUseCaseImpl,
)
from app.usecase.metrics.enrollment_metrics_query_model import (
    LimitedEnrollmentMetricsReadModel,
)
from app.usecase.subscription.subscription_command_usecase import (
    SubscriptionCommandUseCase,
    SubscriptionCommandUseCaseImpl,
    SubscriptionCommandUseCaseUnitOfWork,
)
from app.usecase.subscription.subscription_query_model import (
    SubscriptionReadModel,
    SubTypeReadModel,
)
from app.usecase.subscription.subscription_query_service import SubscriptionQueryService
from app.usecase.subscription.subscription_query_usecase import (
    SubscriptionQueryUseCase,
    SubscriptionQueryUseCaseImpl,
)
from app.usecase.user.user_query_model import UserReadModel

config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

app = FastAPI(title="subscriptions")
create_tables()


def get_session() -> Iterator[Session]:
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def subscription_query_usecase(
    session: Session = Depends(get_session),
) -> SubscriptionQueryUseCase:
    subscription_query_usecase: SubscriptionQueryService = SubscriptionQueryServiceImpl(
        session
    )
    return SubscriptionQueryUseCaseImpl(subscription_query_usecase)


def subscription_command_usecase(
    session: Session = Depends(get_session),
) -> SubscriptionCommandUseCase:
    subscription_repository: SubscriptionRepository = SubscriptionRepositoryImpl(
        session
    )
    uow: SubscriptionCommandUseCaseUnitOfWork = (
        SubscriptionCommandUseCaseUnitOfWorkImpl(
            session, subscription_repository=subscription_repository
        )
    )
    return SubscriptionCommandUseCaseImpl(uow)


def enrollment_query_usecase(
    session: Session = Depends(get_session),
) -> EnrollmentQueryUseCase:
    enrollment_query_service: EnrollmentQueryService = EnrollmentQueryServiceImpl(
        session
    )
    return EnrollmentQueryUseCaseImpl(enrollment_query_service)


def enrollment_command_usecase(
    session: Session = Depends(get_session),
) -> EnrollmentCommandUseCase:
    enrollment_repository: EnrollmentRepository = EnrollmentRepositoryImpl(session)
    uow: EnrollmentCommandUseCaseUnitOfWork = EnrollmentCommandUseCaseUnitOfWorkImpl(
        session, enrollment_repository=enrollment_repository
    )
    return EnrollmentCommandUseCaseImpl(uow)


try:
    microservices = ast.literal_eval(os.environ["MICROSERVICES"])
except KeyError as e:
    microservices = {}


def get_courses(cids, limit, offset):
    if len(cids) == 0:
        cids.append("-")
    try:
        return requests.get(
            microservices.get("courses") + "courses/",
            params={"ids": cids, "limit": limit, "offset": offset},
        )
    except:
        raise


@app.get(
    "/subscriptions",
    response_model=List[SubTypeReadModel],
    status_code=status.HTTP_200_OK,
    tags=["subscriptions"],
)
async def get_subscription_types(
    sub_query: SubscriptionQueryUseCase = Depends(subscription_query_usecase),
):
    return sub_query.get_subscriptions()


class PaymentError(Exception):
    message = "Payment error."

    def __str__(self):
        return PaymentError.message


async def pay(user_id, price, creator_id=None):
    price_in_eth = f"{price:.12f}"[0:12]

    body = {
        "senderId": user_id,
        "amountInEthers": price_in_eth,
    }
    if creator_id is not None:
        body["receiverId"] = creator_id
    logger.info(body)
    return requests.post(
        microservices.get("payments") + "payments/deposit",
        json=body,
    )


@app.post(
    "/subscriptions",
    response_model=SubscriptionReadModel,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {
            "model": ErrorMessageUserAlreadySubscribed,
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorMessageSubTypeNotFound,
        },
    },
    tags=["subscriptions"],
)
async def subscribe(
    user_id: str,
    sub_id: int,
    sub_query: SubscriptionQueryUseCase = Depends(subscription_query_usecase),
    sub_command: SubscriptionCommandUseCase = Depends(subscription_command_usecase),
):
    try:
        sub_query.sub_id_exists(sub_id)
        sub = sub_command.subscribe(user_id=user_id, sub_id=sub_id)
        price: float = 0
        for i in sub_query.get_subscriptions():
            if i.id == sub_id:
                price = i.price
        if price > 0:
            p = await pay(user_id, price)
            if p.status_code != 200:
                raise PaymentError

    except UserAlreadySubscribedError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )
    except UserNotSubscribedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except SubTypeNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except PaymentError as e:
        logger.error(e)
        logger.error(p.json())
        sub_command.unsubscribe(user_id=user_id)
        raise HTTPException(
            status_code=p.status_code,
            detail=p.json(),
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return sub


@app.get(
    "/subscriptions/{user_id}",
    response_model=SubTypeReadModel,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_409_CONFLICT: {
            "model": ErrorMessageUserNotSubscribed,
        },
    },
    tags=["subscriptions"],
)
async def get_subscription(
    user_id: str,
    sub_query: SubscriptionQueryUseCase = Depends(subscription_query_usecase),
    sub_command: SubscriptionCommandUseCase = Depends(subscription_command_usecase),
):
    try:
        sub_id = sub_command.user_sub_type(user_id=user_id)
        for i in sub_query.get_subscriptions():
            if i.id == sub_id:
                return i
        raise SubTypeNotFoundError
    except UserNotSubscribedError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except SubTypeNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@app.patch(
    "/subscriptions/{user_id}",
    response_model=SubscriptionReadModel,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_409_CONFLICT: {
            "model": ErrorMessageUserNotSubscribed,
        },
    },
    tags=["subscriptions"],
)
async def unsubscribe(
    user_id: str,
    sub_command: SubscriptionCommandUseCase = Depends(subscription_command_usecase),
):
    try:
        sub = sub_command.unsubscribe(user_id=user_id)
    except UserNotSubscribedError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except SubTypeNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return sub


def apply_discount(price, user_sub_type, course_sub_type):
    if course_sub_type == 0:
        price = price * (1 - user_sub_type.discount_default / 100)
    if course_sub_type == 1:
        price = price * (1 - user_sub_type.discount_plus / 100)

    return price


@app.post(
    "/subscriptions/{course_id}/enrollments",
    response_model=EnrollmentReadModel,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {
            "model": ErrorMessageUserAlreadyEnrolled,
        },
    },
    tags=["enrollments"],
)
async def enroll(
    course_id: str,
    user_id: str,
    enr_command: EnrollmentCommandUseCase = Depends(enrollment_command_usecase),
    sub_query: SubscriptionQueryUseCase = Depends(subscription_query_usecase),
    sub_command: SubscriptionCommandUseCase = Depends(subscription_command_usecase),
):
    try:
        r = get_courses(course_id, 1, 0)
        c = r.json().get("courses")
        logger.info(c)
        if len(c) == 0:
            raise CourseNotFoundError
        sub_command.check_enr_permission(c[0].get("subscription_id"), user_id)
        enrollment = enr_command.enroll(user_id=user_id, course_id=course_id)
        sub_id = sub_command.user_sub_type(user_id=user_id)
        for i in sub_query.get_subscriptions():
            if i.id == sub_id:
                sub = i
        price = apply_discount(c[0].get("price"), sub, c[0].get("subscription_id"))
        if price > 0:
            p = await pay(user_id, price, creator_id=c[0].get("creator_id"))
            if p.status_code != 200:
                raise PaymentError

    except UserAlreadyEnrolledError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )
    except UserNotSubscribedError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except CourseNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except NoEnrollmentPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )
    except PaymentError as e:
        logger.error(e)
        logger.error(p.json())
        enr_command.unenroll(user_id=user_id, course_id=course_id)
        raise HTTPException(
            status_code=p.status_code,
            detail=p.json(),
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return enrollment


@app.patch(
    "/subscriptions/{course_id}/enrollments/{user_id}",
    response_model=EnrollmentReadModel,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_409_CONFLICT: {
            "model": ErrorMessageUserNotEnrolled,
        },
    },
    tags=["enrollments"],
)
async def unenroll(
    course_id: str,
    user_id: str,
    enr_command: EnrollmentCommandUseCase = Depends(enrollment_command_usecase),
):
    try:
        enrollment = enr_command.unenroll(user_id=user_id, course_id=course_id)
    except UserNotEnrolledError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return enrollment


def notify_users(users: List[str], course_name: str):
    body = {
        "usersToNotify": users,
        "courseName": course_name,
        "courseNewState": "Cancelled",
    }
    requests.post(
        microservices.get("notifications") + "notifications/course-state-change",
        json=body,
    )


@app.patch(
    "/subscriptions/{course_id}/enrollments",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_409_CONFLICT: {
            "model": ErrorMessageUserNotEnrolled,
        },
    },
    tags=["enrollments"],
)
async def unenroll_all(
    course_id: str,
    course_name: str,
    enr_command: EnrollmentCommandUseCase = Depends(enrollment_command_usecase),
    enr_query: EnrollmentQueryUseCase = Depends(enrollment_query_usecase),
):
    try:
        users = enr_query.fetch_users_from_course(id=course_id, only_active=True)
        enr_command.unenroll_all(course_id=course_id)
        notify_users(users, course_name)
    except NoStudentsInCourseError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@app.get(
    "/subscriptions/{course_id}/enrollments/cancel-fee",
    response_model=float,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorMessageCourseNotFound,
        },
    },
    tags=["enrollments"],
)
async def get_cancel_fee(
    course_id: str,
    price: float,
    sub_id: int,
    enr_query: EnrollmentQueryUseCase = Depends(enrollment_query_usecase),
    sub_command: SubscriptionCommandUseCase = Depends(subscription_command_usecase),
    sub_query: SubscriptionQueryUseCase = Depends(subscription_query_usecase),
):
    try:
        users = enr_query.fetch_users_from_course(id=course_id, only_active=True)
        subs = sub_query.get_subscriptions()
        total = 0
        for i in users:
            total += apply_discount(price, sub_command.user_sub_type(i), subs[sub_id])
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return total


def get_users(uids, request):
    try:
        h = {"authorization": request.headers.get("authorization")}
        ids = ""
        for i in uids:
            ids = ids + i + ","
        logger.info(uids)
        return requests.get(
            microservices.get("users") + "users/filter-by-ids",
            headers=h,
            params={"ids": ids[:-1]},
        )
    except:
        raise


@app.get(
    "/subscriptions/{course_id}/enrollments/course/id-only",
    response_model=List[str],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorMessageCourseNotFound,
        },
    },
    tags=["enrollments"],
)
async def get_users_enrolled_id_only(
    course_id: str,
    only_active: bool = True,
    enr_query: EnrollmentQueryUseCase = Depends(enrollment_query_usecase),
):
    try:
        users = enr_query.fetch_users_from_course(id=course_id, only_active=only_active)
    except NoStudentsInCourseError as e:
        logger.info(e)
        return []
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return users


@app.get(
    "/subscriptions/{course_id}/enrollments/course",
    response_model=List[UserReadModel],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorMessageCourseNotFound,
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorMessageInvalidCredentials,
        },
    },
    tags=["enrollments"],
)
async def get_users_enrolled(
    request: Request,
    course_id: str,
    only_active: bool = True,
    enr_query: EnrollmentQueryUseCase = Depends(enrollment_query_usecase),
):
    try:
        users = enr_query.fetch_users_from_course(id=course_id, only_active=only_active)
        server_response = get_users(uids=users, request=request)
        logger.info(server_response)
        logger.info(server_response.status_code)
        if server_response.status_code == status.HTTP_403_FORBIDDEN:
            raise InvalidCredentialsError
    except NoStudentsInCourseError as e:
        logger.info(e)
        return []
    except InvalidCredentialsError as e:
        logger.info(e)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return json.loads(server_response.text)


@app.get(
    "/subscriptions/{user_id}/enrollments/user",
    response_model=CoursesListReadModel,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorMessageCourseNotFound,
        },
    },
    tags=["enrollments"],
)
async def get_courses_enrolled(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    enr_query: EnrollmentQueryUseCase = Depends(enrollment_query_usecase),
):
    try:
        enr_list = enr_query.fetch_courses_from_user(id=user_id)
        enrolled = get_courses(cids=enr_list["enrolled"], limit=limit, offset=offset)
        unenrolled = get_courses(
            cids=enr_list["unenrolled"], limit=limit, offset=offset
        )

    except StudentNotEnrolledError as e:
        logger.info(e)
        return CoursesListReadModel.empty()
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return CoursesListReadModel.from_responses(enrolled, unenrolled)


@app.get(
    "/subscriptions/metrics/",
    response_model=LimitedEnrollmentMetricsReadModel,
    status_code=status.HTTP_200_OK,
    tags=["metrics"],
)
async def get_enrollment_metrics(
    limit: int = 10,
    min_timestamp: int = 0,
    max_timestamp: int = None,
    query_usecase: EnrollmentQueryUseCase = Depends(enrollment_query_usecase),
):
    try:
        if max_timestamp is None:
            max_timestamp = int(datetime.now().timestamp() * 1000)
        metrics, count = query_usecase.get_enrollment_metrics(
            limit=limit, min_timestamp=min_timestamp, max_timestamp=max_timestamp
        )
        cids = list(map(lambda m: m.course_id, metrics))
        courses = get_courses(cids, limit, 0)

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return LimitedEnrollmentMetricsReadModel.from_lists(
        json.loads(courses.text), metrics, count
    )

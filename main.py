import ast
import json
import logging
import os
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
from app.usecase.course.course_query_model import PaginatedCourseReadModel
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
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return sub


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
    response_model=PaginatedCourseReadModel,
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
    only_active: bool = True,
    limit: int = 50,
    offset: int = 0,
    enr_query: EnrollmentQueryUseCase = Depends(enrollment_query_usecase),
):
    try:
        courses = enr_query.fetch_courses_from_user(id=user_id, only_active=only_active)
        server_response = get_courses(cids=courses, limit=limit, offset=offset)

    except StudentNotEnrolledError as e:
        logger.info(e)
        return PaginatedCourseReadModel(courses=[], count=0)
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return json.loads(server_response.text)

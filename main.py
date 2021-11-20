import ast
import json
import logging
import os
from logging import config
from typing import Iterator

import requests
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm.session import Session
from starlette.requests import Request

from app.domain.enrollment.enrollment_exception import UserAlreadyEnrolledError
from app.domain.enrollment.enrollment_repository import EnrollmentRepository
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
from app.presentation.schema.course.course_error_message import (
    ErrorMessageCourseNotFound,
)
from app.presentation.schema.enrollment.enrollment_error_message import (
    ErrorMessageUserAlreadyEnrolled,
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
from app.usecase.user.user_query_model import PaginatedUserReadModel

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


@app.post(
    "/subscriptions/enroll",
    response_model=EnrollmentReadModel,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {
            "model": ErrorMessageUserAlreadyEnrolled,
        },
    },
    tags=["enrollments"],
)
async def enroll_user(
    course_id: str,
    user_id: str,
    enr_command: EnrollmentCommandUseCase = Depends(enrollment_command_usecase),
):
    try:
        enrollment = enr_command.enroll(user_id=user_id, course_id=course_id)
    except UserAlreadyEnrolledError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return enrollment


def get_users(uids, request, limit, offset):
    try:
        h = {"authorization": request.headers.get("authorization")}
        ids = ""
        for i in uids:
            ids = ids + i + ","
        logger.info(uids)
        return requests.get(
            microservices.get("users") + "users/filter-by-ids",
            headers=h,
            params={"ids": ids[:-1], "limit": limit, "offset": offset},
        )
    except:
        raise


def get_courses(cids, limit, offset):
    try:
        logger.info(microservices)
        logger.info(type(microservices))
        logger.info(microservices.get("courses"))
        return requests.get(
            microservices.get("courses") + "courses/",
            params={"ids": cids, "limit": limit, "offset": offset},
        )
    except:
        raise


@app.get(
    "/subscriptions/enrollments/course",
    response_model=PaginatedUserReadModel,
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
    id: str,
    only_active: bool = True,
    limit: int = 50,
    offset: int = 0,
    enr_query: EnrollmentQueryUseCase = Depends(enrollment_query_usecase),
):
    try:
        users = enr_query.fetch_students_from_course(id=id, only_active=only_active)
        server_response = get_users(
            uids=users, request=request, limit=limit, offset=offset
        )
        logger.info(server_response)
        logger.info(server_response.status_code)
        if server_response.status_code == status.HTTP_403_FORBIDDEN:
            raise InvalidCredentialsError
    except NoStudentsInCourseError as e:
        logger.info(e)
        return PaginatedUserReadModel(users=[], count=0)
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
    "/subscriptions/enrollments/student",
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
    id: str,
    only_active: bool = True,
    limit: int = 50,
    offset: int = 0,
    enr_query: EnrollmentQueryUseCase = Depends(enrollment_query_usecase),
):
    try:
        courses = enr_query.fetch_courses_from_student(id=id, only_active=only_active)
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

from pydantic import BaseModel, Field

from app.domain.enrollment.enrollment_exception import (
    UserAlreadyEnrolledError,
    UserNotEnrolledError,
)


class ErrorMessageUserAlreadyEnrolled(BaseModel):
    detail: str = Field(example=UserAlreadyEnrolledError.message)


class ErrorMessageUserNotEnrolled(BaseModel):
    detail: str = Field(example=UserNotEnrolledError.message)

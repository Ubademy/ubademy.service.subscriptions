from pydantic import BaseModel, Field

from app.domain.enrollment.enrollment_exception import UserAlreadyEnrolledError


class ErrorMessageUserAlreadyEnrolled(BaseModel):
    detail: str = Field(example=UserAlreadyEnrolledError.message)

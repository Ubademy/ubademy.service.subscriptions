from pydantic import BaseModel, Field

from app.domain.user.user_exception import InvalidCredentialsError


class ErrorMessageInvalidCredentials(BaseModel):
    detail: str = Field(example=InvalidCredentialsError.message)

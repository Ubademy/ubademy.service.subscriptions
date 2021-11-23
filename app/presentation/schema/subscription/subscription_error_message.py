from pydantic import BaseModel, Field

from app.domain.subscription.subscription_exception import (
    SubTypeNotFoundError,
    UserAlreadySubscribedError,
    UserNotSubscribedError,
)


class ErrorMessageUserNotSubscribed(BaseModel):
    detail: str = Field(example=UserNotSubscribedError.message)


class ErrorMessageUserAlreadySubscribed(BaseModel):
    detail: str = Field(example=UserAlreadySubscribedError.message)


class ErrorMessageSubTypeNotFound(BaseModel):
    detail: str = Field(example=SubTypeNotFoundError.message)

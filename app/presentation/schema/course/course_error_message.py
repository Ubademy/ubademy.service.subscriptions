from pydantic import BaseModel, Field

from app.domain.course import CourseNotFoundError, CoursesNotFoundError


class ErrorMessageCourseNotFound(BaseModel):
    detail: str = Field(example=CourseNotFoundError.message)


class ErrorMessageCoursesNotFound(BaseModel):
    detail: str = Field(example=CoursesNotFoundError.message)

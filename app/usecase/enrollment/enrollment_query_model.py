from typing import cast

from pydantic import BaseModel, Field

from app.domain.enrollment.enrollment import Enrollment


class EnrollmentReadModel(BaseModel):

    id: str = Field(example="vytxeTZskVKR7C7WgdSP3d")
    user_id: str = Field(example="h77HHmN5gU890OlSmwE5Gbv")
    course_id: str = Field(example="oGY7u51HmoDIDbNMDIZc09V")
    active: bool = Field(example=True)
    updated_at: int = Field(example=1136214245000)

    class Config:
        orm_mode = True

    def is_active(self):
        return self.active

    def get_user_id(self):
        return self.user_id

    def get_course_id(self):
        return self.course_id

    @staticmethod
    def from_entity(enrollment: Enrollment) -> "EnrollmentReadModel":
        return EnrollmentReadModel(
            id=enrollment.id,
            user_id=enrollment.user_id,
            course_id=enrollment.course_id,
            active=enrollment.active,
            updated_at=cast(int, enrollment.updated_at),
        )

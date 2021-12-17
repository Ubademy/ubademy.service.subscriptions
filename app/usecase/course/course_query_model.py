import json
from typing import List

from pydantic import BaseModel, Field


class CourseReadModel(BaseModel):

    id: str = Field(example="vytxeTZskVKR7C7WgdSP3d")
    creator_id: str = Field(example="creator1")
    name: str = Field(example="C Programming For Beginners - Master the C Language")
    price: int = Field(ge=0, example=10)
    subscription_id: int = Field(ge=0, le=2, example=1)
    active: bool = Field(example=True)
    language: str = Field(example="English")
    description: str = Field(example="Learn how to program with C")
    categories: List[str] = Field(example=["Programming"])
    recommendations: dict = Field(example={"recommended": 100, "total": 120})
    presentation_video: str = Field(
        example="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    )
    image: str = Field(
        example="https://static01.nyt.com/images/2017/09/26/science/26TB-PANDA/26TB-PANDA-superJumbo.jpg"
    )
    created_at: int = Field(example=1136214245000)
    updated_at: int = Field(example=1136214245000)

    class Config:
        orm_mode = True


class PaginatedCourseReadModel(BaseModel):
    courses: List[CourseReadModel] = Field(example=CourseReadModel.schema())
    count: int = Field(ge=0, example=1)

    @staticmethod
    def empty():
        return PaginatedCourseReadModel(courses=[], count=0)


class CoursesListReadModel(BaseModel):
    enrolled: PaginatedCourseReadModel = Field(
        example=PaginatedCourseReadModel.schema()
    )
    unenrolled: PaginatedCourseReadModel = Field(
        example=PaginatedCourseReadModel.schema()
    )

    @staticmethod
    def empty():
        return CoursesListReadModel(
            enrolled=PaginatedCourseReadModel.empty(),
            unenrolled=PaginatedCourseReadModel.empty(),
        )

    @staticmethod
    def from_responses(enrolled, unenrolled):
        return CoursesListReadModel(
            enrolled=json.loads(enrolled.text), unenrolled=json.loads(unenrolled.text)
        )

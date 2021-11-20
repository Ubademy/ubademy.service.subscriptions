from typing import List

from pydantic import BaseModel, Field


class CourseReadModel(BaseModel):

    id: str = Field(example="vytxeTZskVKR7C7WgdSP3d")
    creator_id: str = Field(example="creator1")
    name: str = Field(example="C Programming For Beginners - Master the C Language")
    price: int = Field(ge=0, example=10)
    language: str = Field(example="English")
    description: str = Field(example="Learn how to program with C")
    categories: List[str] = Field(example=["Programming"])
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

from typing import List

from pydantic import BaseModel, Field


class UserReadModel(BaseModel):

    id: str = Field(example="Kgj1yXyrZ4NBeplhONPJ4xeLuQv2")
    username: str = Field(example="jany99")
    name: str = Field(example="Jane")
    lastName: str = Field(example="Doe")
    active: bool = Field(example=True)
    role: int = Field(example=1)
    dateOfBirth: str = Field(example="Wed Nov 10 2021")
    country: str = Field(example="Argentina")
    language: str = Field(example="Spanish")
    mail: str = Field(example="jane@doe.com")
    favouriteCourses: List[str] = Field(example=["BeplhONPJ4xeLu", "gj1yXyrZ4"])

    class Config:
        orm_mode = True

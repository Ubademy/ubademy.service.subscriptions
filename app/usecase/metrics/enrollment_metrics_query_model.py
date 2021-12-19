from typing import List

from pydantic import BaseModel, Field


class EnrollmentMetricsReadModel(BaseModel):

    course_id: str = Field(example="74qc6u7PduDhRAtq3VcMBQ")
    count: int = Field(example=10)


class LimitedEnrollmentMetricsReadModel(BaseModel):

    courses: List[EnrollmentMetricsReadModel] = Field(
        example=[EnrollmentMetricsReadModel.schema()]
    )
    count: int = Field(example=10)

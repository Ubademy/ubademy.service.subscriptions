import logging
from typing import List

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class EnrollmentMetricsReadModel(BaseModel):

    course_id: str = Field(example="74qc6u7PduDhRAtq3VcMBQ")
    name: str = Field(default=" ", example="FastAPI Course")
    count: int = Field(example=10)


class LimitedEnrollmentMetricsReadModel(BaseModel):

    courses: List[EnrollmentMetricsReadModel] = Field(
        example=[EnrollmentMetricsReadModel.schema()]
    )
    count: int = Field(example=10)

    @staticmethod
    def from_lists(courses, metrics, count):

        for i in courses["courses"]:
            for j in metrics:
                if j.course_id == i["id"]:
                    j.name = i["name"]
        return LimitedEnrollmentMetricsReadModel(
            courses=metrics,
            count=count,
        )

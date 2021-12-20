from app.usecase.metrics.enrollment_metrics_query_model import (
    EnrollmentMetricsReadModel,
    LimitedEnrollmentMetricsReadModel,
)
from tests.params import course_sub_1


class TestLimitedEnrollmentMetricsReadModel:
    def test_from_lists(self):
        metrics = LimitedEnrollmentMetricsReadModel.from_lists(
            {"courses": [{"id": course_sub_1.id, "name": course_sub_1.name}]},
            [EnrollmentMetricsReadModel(course_id=course_sub_1.id, count=1)],
            count=1,
        )
        assert len(metrics.courses) == 1
        assert metrics.courses[0].name == course_sub_1.name

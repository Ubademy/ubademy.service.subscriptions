from tests.params import enr_1_active, enr_1_inactive, enr_2_active


class TestEnrollment:
    def test_enrollment_entity_should_be_identified_by_id(self):
        assert enr_1_active == enr_1_inactive
        assert enr_1_active != enr_2_active

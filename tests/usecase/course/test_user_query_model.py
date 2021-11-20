from app.usecase.course.course_query_model import CourseReadModel


class TestCourseQueryModel:
    def test_create_entity(self):
        course = CourseReadModel(
            id="vytxeTZskVKR7C7WgdSP3d",
            creator_id="creator1",
            name="Programming",
            price=10,
            language="English",
            description="Learn how to program with C",
            categories=["Programming"],
            presentation_video="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            image="https://static01.nyt.com/images/2017/09/26/science/26TB-PANDA/26TB-PANDA-superJumbo.jpg",
            created_at=1136214245000,
            updated_at=1136214245000,
        )
        assert course.id == "vytxeTZskVKR7C7WgdSP3d"

from app.usecase.user.user_query_model import UserReadModel


class TestUserQueryModel:
    def test_create_entity(self):
        user = UserReadModel(
            id="user_1",
            username="user_1",
            name="Jane",
            lastName="Doe",
            active=True,
            role=1,
            dateOfBirth="Today",
            country="Arg",
            language="Es",
            mail="hola@gmail.com",
            favouriteCourses=[],
        )
        assert user.id == "user_1"

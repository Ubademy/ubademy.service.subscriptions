from app.usecase.subscription.subscription_query_model import SubTypeReadModel


class TestSubscriptionQueryModel:
    def test_create_sub_type_entity(self):
        sub_type = SubTypeReadModel(
            id=1,
            name="Ubademy+",
            description="Yes",
            price=12,
            badge="https://taller-de-programacion-2.github.io/works/statement/2021/2/tp/ubademy.png",
        )
        assert sub_type.id == 1

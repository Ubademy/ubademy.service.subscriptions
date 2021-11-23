from unittest.mock import MagicMock

from app.infrastructure.subscription.subscription_query_service import (
    SubscriptionQueryServiceImpl,
)
from app.usecase.subscription.subscription_query_usecase import (
    SubscriptionQueryUseCaseImpl,
)


class TestSubscriptionQueryUseCase:
    def test_get_sub_types_should_return_subtypes(self):
        session = MagicMock()
        sub_query_service = SubscriptionQueryServiceImpl(session)
        sub_query = SubscriptionQueryUseCaseImpl(sub_query_service)
        sub_types = sub_query.get_subscriptions()
        assert len(sub_types) == 3

from unittest.mock import MagicMock

import pytest

from app.domain.subscription.subscription_exception import SubTypeNotFoundError
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

    def test_sub_id_exists_should_return_true(self):
        session = MagicMock()
        sub_query_service = SubscriptionQueryServiceImpl(session)
        sub_query = SubscriptionQueryUseCaseImpl(sub_query_service)
        assert sub_query.sub_id_exists(0)

    def test_sub_id_exists_should_raise_sub_type_not_found_error(self):
        session = MagicMock()
        sub_query_service = SubscriptionQueryServiceImpl(session)
        sub_query = SubscriptionQueryUseCaseImpl(sub_query_service)
        with pytest.raises(SubTypeNotFoundError):
            sub_query.sub_id_exists(3)

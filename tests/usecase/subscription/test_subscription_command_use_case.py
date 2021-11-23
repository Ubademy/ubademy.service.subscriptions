from unittest.mock import MagicMock, Mock

import pytest
from sqlalchemy.exc import NoResultFound

from app.domain.subscription.subscription_exception import (
    UserAlreadySubscribedError,
    UserNotSubscribedError,
)
from app.infrastructure.subscription.subscription_repository import (
    SubscriptionCommandUseCaseUnitOfWorkImpl,
    SubscriptionRepositoryImpl,
)
from app.usecase.subscription.subscription_command_usecase import (
    SubscriptionCommandUseCaseImpl,
)
from tests.params import already_subscribed, filter_by_id_user_1_sub_1, no_susbcriptions


class TestSubscriptionCommandUseCase:
    def test_subscribe_should_return_subscription(self):
        session = MagicMock()
        session.query().filter_by = Mock(side_effect=no_susbcriptions)
        subscription_repository = SubscriptionRepositoryImpl(session)
        uow = SubscriptionCommandUseCaseUnitOfWorkImpl(
            session=session, subscription_repository=subscription_repository
        )
        sub_command = SubscriptionCommandUseCaseImpl(uow=uow)

        sub = sub_command.subscribe("user_1", 0)

        assert sub.user_id == "user_1"
        assert sub.sub_id == 0

    def test_subscribe_should_raise_user_already_enrolled_error(self):
        session = MagicMock()
        session.query().filter_by().one = Mock(side_effect=already_subscribed)
        subscription_repository = SubscriptionRepositoryImpl(session)
        uow = SubscriptionCommandUseCaseUnitOfWorkImpl(
            session=session, subscription_repository=subscription_repository
        )
        sub_command = SubscriptionCommandUseCaseImpl(uow=uow)

        with pytest.raises(UserAlreadySubscribedError):
            sub_command.subscribe("user_1", 0)

    def test_unsubscribe_should_return_subscription(self):
        session = MagicMock()
        session.query().filter_by = Mock(side_effect=filter_by_id_user_1_sub_1)
        subscription_repository = SubscriptionRepositoryImpl(session)
        uow = SubscriptionCommandUseCaseUnitOfWorkImpl(
            session=session, subscription_repository=subscription_repository
        )
        sub_command = SubscriptionCommandUseCaseImpl(uow=uow)

        sub = sub_command.unsubscribe("user_1")

        assert sub.user_id == "user_1"
        assert sub.sub_id == 0
        assert sub.active

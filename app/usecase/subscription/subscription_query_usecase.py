from abc import ABC, abstractmethod
from typing import List

from app.usecase.subscription.subscription_query_model import SubTypeReadModel
from app.usecase.subscription.subscription_query_service import SubscriptionQueryService


class SubscriptionQueryUseCase(ABC):
    @abstractmethod
    def get_subscriptions(self) -> List[SubTypeReadModel]:
        raise NotImplementedError


class SubscriptionQueryUseCaseImpl(SubscriptionQueryUseCase):
    def __init__(self, subscription_query_service: SubscriptionQueryService):
        self.subscription_query_service: SubscriptionQueryService = (
            subscription_query_service
        )

    def get_subscriptions(self) -> List[SubTypeReadModel]:
        return self.subscription_query_service.get_subscriptions()

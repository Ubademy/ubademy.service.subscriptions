from abc import ABC, abstractmethod
from typing import List

from app.domain.subscription.subscription_exception import SubTypeNotFoundError
from app.usecase.subscription.subscription_query_model import SubTypeReadModel
from app.usecase.subscription.subscription_query_service import SubscriptionQueryService


class SubscriptionQueryUseCase(ABC):
    @abstractmethod
    def get_subscriptions(self) -> List[SubTypeReadModel]:
        raise NotImplementedError

    @abstractmethod
    def sub_id_exists(self, sub_id: int):
        raise NotImplementedError


class SubscriptionQueryUseCaseImpl(SubscriptionQueryUseCase):
    def __init__(self, subscription_query_service: SubscriptionQueryService):
        self.subscription_query_service: SubscriptionQueryService = (
            subscription_query_service
        )

    def get_subscriptions(self) -> List[SubTypeReadModel]:
        return self.subscription_query_service.get_subscriptions()

    def sub_id_exists(self, sub_id: int):
        subs = self.get_subscriptions()
        for i in subs:
            if i.id == sub_id:
                return True
        raise SubTypeNotFoundError

from abc import ABC, abstractmethod
from typing import List

from .subscription_query_model import SubTypeReadModel


class SubscriptionQueryService(ABC):
    @abstractmethod
    def get_subscriptions(self) -> List[SubTypeReadModel]:
        raise NotImplementedError

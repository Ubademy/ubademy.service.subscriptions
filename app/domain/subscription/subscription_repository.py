from abc import ABC, abstractmethod

from app.domain.subscription.subscription import Subscription


class SubscriptionRepository(ABC):
    @abstractmethod
    def subscribe(self, subscription: Subscription):
        raise NotImplementedError

    @abstractmethod
    def has_active_user(self, user_id: str, sub_id: int = None) -> bool:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, uuid) -> Subscription:
        raise NotImplementedError

    @abstractmethod
    def unsubscribe(self, user_id: str) -> Subscription:
        raise NotImplementedError

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> Subscription:
        raise NotImplementedError

import logging
from abc import ABC, abstractmethod
from typing import cast

import shortuuid
from sqlalchemy.exc import NoResultFound

from app.domain.enrollment.enrollment_exception import NoEnrollmentPermissionError
from app.domain.subscription.subscription import Subscription
from app.domain.subscription.subscription_exception import (
    UserAlreadySubscribedError,
    UserNotSubscribedError,
)
from app.domain.subscription.subscription_repository import SubscriptionRepository
from app.usecase.subscription.subscription_query_model import SubscriptionReadModel

logger = logging.getLogger(__name__)


class SubscriptionCommandUseCaseUnitOfWork(ABC):

    subscription_repository: SubscriptionRepository

    @abstractmethod
    def begin(self):
        raise NotImplementedError

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError


class SubscriptionCommandUseCase(ABC):
    @abstractmethod
    def subscribe(self, user_id: str, sub_id: int):
        raise NotImplementedError

    @abstractmethod
    def unsubscribe(self, user_id: str):
        raise NotImplementedError

    @abstractmethod
    def check_enr_permission(self, sub_id: int, user_id: str):
        raise NotImplementedError


class SubscriptionCommandUseCaseImpl(SubscriptionCommandUseCase):
    def __init__(
        self,
        uow: SubscriptionCommandUseCaseUnitOfWork,
    ):
        self.uow: SubscriptionCommandUseCaseUnitOfWork = uow

    def subscribe(self, user_id: str, sub_id: int):
        try:
            uuid = shortuuid.uuid()
            sub = Subscription(
                id=uuid,
                user_id=user_id,
                sub_id=sub_id,
                active=True,
            )

            if self.uow.subscription_repository.has_active_user(
                user_id=user_id, sub_id=sub_id
            ):
                raise UserAlreadySubscribedError
            if sub_id != 0:
                self.uow.subscription_repository.unsubscribe(user_id)
            elif self.uow.subscription_repository.has_active_user(user_id=user_id):
                self.uow.subscription_repository.unsubscribe(user_id)
            self.uow.subscription_repository.subscribe(sub)
            self.uow.commit()

            created_sub = self.uow.subscription_repository.find_by_id(uuid)
        except:
            self.uow.rollback()
            raise

        return SubscriptionReadModel.from_entity(cast(Subscription, created_sub))

    def unsubscribe(self, user_id: str):
        try:
            sub = self.subscribe(user_id, 0)
        except UserAlreadySubscribedError:
            raise UserNotSubscribedError
        except:
            raise
        return sub

    def check_enr_permission(self, sub_id: int, user_id: str):
        try:
            s = self.uow.subscription_repository.find_by_user_id(user_id)
            if sub_id >= 1 and s.sub_id < 1:
                raise NoEnrollmentPermissionError

        except NoResultFound:
            raise UserNotSubscribedError
        except:
            raise

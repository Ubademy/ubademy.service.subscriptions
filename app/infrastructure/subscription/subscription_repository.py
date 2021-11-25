from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from app.domain.subscription.subscription import Subscription
from app.domain.subscription.subscription_exception import UserNotSubscribedError
from app.domain.subscription.subscription_repository import SubscriptionRepository
from app.infrastructure.subscription.subscription_dto import SubscriptionDTO
from app.usecase.subscription.subscription_command_usecase import (
    SubscriptionCommandUseCaseUnitOfWork,
)


class SubscriptionRepositoryImpl(SubscriptionRepository):
    def __init__(self, session: Session):
        self.session: Session = session

    def subscribe(self, subscription: Subscription):
        sub_dto = SubscriptionDTO.from_entity(subscription)
        try:
            self.session.add(sub_dto)
        except:
            raise

    def unsubscribe(self, user_id: str) -> Subscription:
        try:
            sub_dto = (
                self.session.query(SubscriptionDTO)
                .filter_by(user_id=user_id, active=True)
                .one()
            )
            sub_dto.active = False
        except NoResultFound:
            raise UserNotSubscribedError
        except:
            raise

        return sub_dto.to_entity()

    def has_active_user(self, user_id: str, sub_id: int = None) -> bool:
        try:
            if sub_id is not None:
                self.session.query(SubscriptionDTO).filter_by(
                    user_id=user_id, sub_id=sub_id, active=True
                ).one()
            else:
                self.session.query(SubscriptionDTO).filter_by(
                    user_id=user_id, active=True
                ).one()
        except NoResultFound:
            return False
        return True

    def find_by_id(self, uuid: str):
        try:
            sub_dto = self.session.query(SubscriptionDTO).filter_by(id=uuid).one()
        except NoResultFound:
            return None
        except:
            raise

        return sub_dto.to_entity()

    def find_by_user_id(self, user_id: str) -> Subscription:
        try:
            sub_dto = (
                self.session.query(SubscriptionDTO)
                .filter_by(user_id=user_id, active=True)
                .one()
            )
        except:
            raise

        return sub_dto.to_entity()


class SubscriptionCommandUseCaseUnitOfWorkImpl(SubscriptionCommandUseCaseUnitOfWork):
    def __init__(
        self,
        session: Session,
        subscription_repository: SubscriptionRepository,
    ):
        self.session: Session = session
        self.subscription_repository: SubscriptionRepository = subscription_repository

    def begin(self):
        self.session.begin()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

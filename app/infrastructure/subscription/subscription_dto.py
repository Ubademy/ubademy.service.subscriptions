from datetime import datetime
from typing import Union

from sqlalchemy import BigInteger, Boolean, Column, Integer, String

from app.domain.subscription.subscription import Subscription
from app.infrastructure.database import Base
from app.usecase.subscription.subscription_query_model import SubscriptionReadModel


def unixtimestamp() -> int:
    return int(datetime.now().timestamp() * 1000)


class SubscriptionDTO(Base):

    __tablename__ = "subscriptions"
    id: Union[str, Column] = Column(String, primary_key=True, autoincrement=False)
    user_id: Union[str, Column] = Column(String, nullable=False, autoincrement=False)
    sub_id: Union[int, Column] = Column(Integer, nullable=False, autoincrement=False)
    active: Union[bool, Column] = Column(Boolean, nullable=False)
    updated_at: Union[int, Column] = Column(BigInteger, nullable=False)

    def to_entity(self) -> Subscription:
        return Subscription(
            id=self.id,
            user_id=self.user_id,
            sub_id=self.sub_id,
            active=self.active,
            updated_at=self.updated_at,
        )

    def to_read_model(self) -> SubscriptionReadModel:
        return SubscriptionReadModel(
            id=self.id,
            user_id=self.user_id,
            sub_id=self.sub_id,
            active=self.active,
            updated_at=self.updated_at,
        )

    @staticmethod
    def from_entity(sub: Subscription) -> "SubscriptionDTO":
        now = unixtimestamp()
        return SubscriptionDTO(
            id=sub.id,
            user_id=sub.user_id,
            sub_id=sub.sub_id,
            active=sub.active,
            updated_at=now,
        )

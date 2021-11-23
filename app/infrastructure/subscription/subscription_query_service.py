from typing import List

from sqlalchemy.orm.session import Session

from ...usecase.subscription.subscription_query_model import SubTypeReadModel
from ...usecase.subscription.subscription_query_service import SubscriptionQueryService
from .subtypes import subtype_default, subtype_pass, subtype_plus


class SubscriptionQueryServiceImpl(SubscriptionQueryService):
    def __init__(self, session: Session):
        self.session: Session = session

    def get_subscriptions(self) -> List[SubTypeReadModel]:
        return [subtype_default, subtype_plus, subtype_pass]

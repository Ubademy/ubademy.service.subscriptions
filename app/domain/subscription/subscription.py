from typing import Optional


class Subscription:
    def __init__(
        self,
        id: str,
        user_id: str,
        sub_id: int,
        active: bool,
        updated_at: Optional[int] = None,
    ):
        self.id: str = id
        self.user_id: str = user_id
        self.sub_id: int = sub_id
        self.active: bool = active
        self.updated_at: Optional[int] = updated_at

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Subscription):
            return self.id == o.id

        return False

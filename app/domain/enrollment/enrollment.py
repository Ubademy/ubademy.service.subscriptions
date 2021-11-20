from typing import Optional


class Enrollment:
    def __init__(
        self,
        id: str,
        user_id: str,
        course_id: str,
        active: bool,
        updated_at: Optional[int] = None,
    ):
        self.id: str = id
        self.user_id: str = user_id
        self.course_id: str = course_id
        self.active: bool = active
        self.updated_at: Optional[int] = updated_at

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Enrollment):
            return self.id == o.id

        return False

from typing import cast

from pydantic import BaseModel, Field

from app.domain.subscription.subscription import Subscription


class SubTypeReadModel(BaseModel):
    id: int = Field(ge=0, le=2, example=2)
    name: str = Field(example="Ubademy Pass")
    description: str = Field(
        example="Immerse yourself in a library of hundreds of high-quality courses. Enjoy the "
        "discounts on all courses when you join Ubademy Pass."
    )
    price: float = Field(ge=0, example=20)
    badge: str = Field(
        example="https://taller-de-programacion-2.github.io/works/statement/2021/2/tp/ubademy.png"
    )


class SubscriptionReadModel(BaseModel):

    id: str = Field(example="vytxeTZskVKR7C7WgdSP3d")
    user_id: str = Field(example="h77HHmN5gU890OlSmwE5Gbv")
    sub_id: int = Field(example=1)
    active: bool = Field(example=True)
    updated_at: int = Field(example=1136214245000)

    class Config:
        orm_mode = True

    def is_active(self):
        return self.active

    def get_user_id(self):
        return self.user_id

    @staticmethod
    def from_entity(sub: Subscription) -> "SubscriptionReadModel":
        return SubscriptionReadModel(
            id=sub.id,
            user_id=sub.user_id,
            sub_id=sub.sub_id,
            active=sub.active,
            updated_at=cast(int, sub.updated_at),
        )

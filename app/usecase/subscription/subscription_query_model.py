from pydantic import BaseModel, Field


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

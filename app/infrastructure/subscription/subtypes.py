from app.usecase.subscription.subscription_query_model import SubTypeReadModel

subtype_default = SubTypeReadModel(
    id=0,
    name="Default",
    description="Default subscription. You cannot enroll in courses+",
    price=0,
    discount_default=0,
    discount_plus=0,
    badge="https://taller-de-programacion-2.github.io/works/statement/2021/2/tp/ubademy.png",
)

subtype_plus = SubTypeReadModel(
    id=1,
    name="Ubademy+",
    description="Join any course you want with Ubademy+ and enjoy the discounts!",
    price=0.03,
    discount_default=20,
    discount_plus=0,
    badge="https://taller-de-programacion-2.github.io/works/statement/2021/2/tp/ubademy.png",
)

subtype_pass = SubTypeReadModel(
    id=2,
    name="Ubademy Pass",
    description="Immerse yourself in a library of hundreds of high-quality courses. Enjoy the discounts on all "
    "courses when you join Ubademy Pass.",
    price=0.06,
    discount_default=50,
    discount_plus=20,
    badge="https://taller-de-programacion-2.github.io/works/statement/2021/2/tp/ubademy.png",
)

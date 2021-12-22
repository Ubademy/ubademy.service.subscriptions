# ubademy.service.subscriptions
[![codecov](https://codecov.io/gh/Ubademy/ubademy.service.subscriptions/branch/master/graph/badge.svg?token=QW73TC1O31)](https://codecov.io/gh/Ubademy/ubademy.service.subscriptions) [![Tests](https://github.com/Ubademy/ubademy.service.subscriptions/actions/workflows/test.yml/badge.svg)](https://github.com/Ubademy/ubademy.service.subscriptions/actions/workflows/test.yml) [![Linters](https://github.com/Ubademy/ubademy.service.subscriptions/actions/workflows/linters.yml/badge.svg)](https://github.com/Ubademy/ubademy.service.subscriptions/actions/workflows/linters.yml) [![Deploy](https://github.com/Ubademy/ubademy.service.subscriptions/actions/workflows/deploy.yml/badge.svg)](https://github.com/Ubademy/ubademy.service.subscriptions/actions/workflows/deploy.yml)

Subscriptions microservice for [Ubademy](https://ubademy.github.io/)

This service manages:
* User Subscriptions
* Course Enrollments


For further information visit [Ubademy Subscriptions](https://ubademy.github.io/services/subscriptions)

Deployed at: [ubademy-service-subscriptions](https://ubademy-service-subscriptions.herokuapp.com/docs#) :rocket:



### Technologies

* [FastAPI](https://fastapi.tiangolo.com/)
* [SQLAlchemy](https://www.sqlalchemy.org/): PostgreSQL Database
* [Poetry](https://python-poetry.org/)
* [Docker](https://www.docker.com/)
* [Heroku](https://www.heroku.com/)

### Architecture

Directory structure (based on [Onion Architecture](https://jeffreypalermo.com/2008/07/the-onion-architecture-part-1/)):

```tree
├── main.py
├── routes
├── app
│   ├── domain
│   │   ├── course
│   │   │   └── course_exception.py
│   │   ├── enrollment
│   │   │   ├── enrollment.py
│   │   │   ├── enrollment_exception.py
│   │   │   └── enrollment_repository.py
│   │   ├── subscription
│   │   │   ├── subscription.py
│   │   │   ├── subscription_exception.py
│   │   │   └── subscription_repository.py
│   │   └── user
│   │       └── user_exception.py
│   ├── infrastructure
│   │   ├── enrollment
│   │   │   ├── enrollment_dto.py
│   │   │   ├── enrollment_query_service.py
│   │   │   └── cenrollment_repository.py
│   │   ├── subscription
│   │   │   ├── subscription_dto.py
│   │   │   ├── subscription_query_service.py
│   │   │   └── subscription_repository.py
│   │   └── database.py
│   ├── presentation
│   │   └── schema
│   │       ├── course
│   │       │   └── course_error_message.py
│   │       ├── enrollment
│   │       │   └── enrollment_error_message.py
│   │       ├── subscription
│   │       │   └── subscription_error_message.py
│   │       └── user
│   │           └── user_error_message.py
│   └── usecase
│       ├── course
│       │   └── course_query_model.py
│       ├── enrollment
│       │   ├── enrollment_command_usecase.py
│       │   ├── enrollment_query_model.py
│       │   ├── enrollment_query_service.py
│       │   └── enrollment_query_usecase.py
│       ├── metrics
│       │   └── enrollment_metrics_query_model.py
│       ├── subscription
│       │   ├── subscription_command_usecase.py
│       │   ├── subscription_query_model.py
│       │   ├── subscription_query_service.py
│       │   └── subscription_query_usecase.py
│       └── user
│           └── user_query_model.py
└── tests
```

## Installation

### Dependencies:
* [python3.9](https://www.python.org/downloads/release/python-390/) and utils
* [Docker](https://www.docker.com/)
* [Docker-Compose](https://docs.docker.com/compose/)
* [Poetry](https://python-poetry.org/)

Once you have installed these tools, make will take care of the rest :relieved:

``` bash
make install
```

## Usage

### Run the API locally
``` bash
make run
```

### Reset Database and then run locally
``` bash
make reset
```

### Run format, tests and linters
``` bash
make checks
```

### Access API Swagger
Once the API is running you can check all available endpoints at [http://127.0.0.1:8000/docs#/](http://127.0.0.1:8000/docs#/)

class UserAlreadySubscribedError(Exception):
    message = "The user you specified is already subscribed."

    def __str__(self):
        return UserAlreadySubscribedError.message


class UserNotSubscribedError(Exception):
    message = "The user you specified is not subscribed."

    def __str__(self):
        return UserNotSubscribedError.message


class SubTypeNotFoundError(Exception):
    message = "The Subscription type you specified does not exist."

    def __str__(self):
        return SubTypeNotFoundError.message

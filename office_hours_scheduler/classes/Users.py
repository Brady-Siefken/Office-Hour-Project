from scheduler_app.models import User
from classes.constants import USER_TYPES


class UserClass:

    def __init__(self, email, password=None, name=None, user_type=None):

        if not User.objects.filter(email=email).exists():
            if password is None or name is None or user_type is None:
                self.user = None
                return
            if user_type not in USER_TYPES:
                raise ValueError(f"Invalid user_type '{user_type}'")

        self.user, _ = User.objects.get_or_create(
            email=email,
            defaults={
                "password": password,
                "name": name,
                "user_type": user_type,
            }
        )

    def getEmail(self):
        return self.user.email

    def getPassword(self):
        return self.user.password

    def getName(self):
        return self.user.name

    def getType(self):
        return self.user.user_type

    def setName(self, name):
        self.user.name = name
        self.user.save()

    def setPassword(self, password):
        self.user.password = password
        self.user.save()

    def setEmail(self, email):
        if User.objects.filter(email=email).exists():
            raise ValueError("Email already in use")
        self.user.email = email
        self.user.save()

    def setType(self, user_type):
        if user_type not in USER_TYPES:
            raise ValueError(f"Invalid user_type '{user_type}'")
        self.user.user_type = user_type
        self.user.save()
    def exists(self):
        return self.user is not None

    def __str__(self):
        return self.user.name
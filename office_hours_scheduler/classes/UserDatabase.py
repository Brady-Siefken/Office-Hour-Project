# classes/UserDatabase.py
from scheduler_app.models import User
from classes.Users import UserClass
from classes.constants import USER_TYPES


def doesUserWithEmailExist(email):
    return User.objects.filter(email=email).exists()


def getUser(email):
    if not doesUserWithEmailExist(email):
        return None
    return UserClass(email)


def validatePassword(email, password):
    user = getUser(email)
    return user.getPassword() == password


def getAllUsers():
    return [UserClass(u.email) for u in User.objects.all()]


def getUsersByType(user_type):
    if user_type not in USER_TYPES:
        raise ValueError(f"Invalid user_type '{user_type}'")
    return [UserClass(u.email) for u in User.objects.filter(user_type=user_type)]


def countByType(user_type):
    if user_type not in USER_TYPES:
        raise ValueError(f"Invalid user_type '{user_type}'")
    return User.objects.filter(user_type=user_type).count()


def createUser(email, password, name, user_type):
    if doesUserWithEmailExist(email):
        raise ValueError("User already exists")
    UserClass(email, password, name, user_type)


def deleteUser(email):
    if not doesUserWithEmailExist(email):
        raise ValueError("User does not exist")
    User.objects.filter(email=email).delete()
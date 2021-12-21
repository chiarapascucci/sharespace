"""
    custom user manager for customer user class
    this class handles user object instantiation (including password hashing)

"""

__author__ = "Chiara Pascucci"

from django.contrib.auth.base_user import BaseUserManager


class MyUserManager(BaseUserManager):

    def create_user(self, email, password, username, **extra_fields):
        if not email:
            raise ValueError("you need an email")
        if not username:
            raise ValueError("you need a user name")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, username, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, username, **extra_fields)


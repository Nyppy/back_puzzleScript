import secrets
import string

import jwt

from datetime import datetime
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.core import validators
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
        Django требует, чтобы пользовательские `User`
        определяли свой собственный класс Manager.
        Унаследовав от BaseUserManager, мы получаем много кода,
        используемого Django для создания `User`.

        Все, что нам нужно сделать, это переопределить функцию
        `create_user`, которую мы будем использовать
        для создания объектов `User`.
    """

    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Данный адрес электронной почты должен быть установлен')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        """
            Создает и возвращает `User` с адресом электронной почты,
            именем пользователя и паролем.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
        Определяет наш пользовательский класс User.
        Требуется имя пользователя, адрес электронной почты и пароль.
    """

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(
        validators=[validators.validate_email],
        unique=True,
        blank=False
    )
    phone = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    authorization = models.TextField()

    # Свойство `USERNAME_FIELD` сообщает нам, какое поле мы будем использовать для входа.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    # Сообщает Django, что класс UserManager, определенный выше,
    # должен управлять объектами этого типа.
    objects = UserManager()

    def get_data(self):
        self.set_auth()
        return {
            'id': self.pk,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'authorization': self.authorization,
        }

    def __str__(self):
        """
            Возвращает строковое представление этого `User`.
            Эта строка используется, когда в консоли выводится `User`.
        """
        return self.email

    def get_full_name(self):
        """
            Этот метод требуется Django для таких вещей,
            как обработка электронной почты.
            Обычно это имя и фамилия пользователя.
        """
        return "{} {}".format(self.first_name,  self.last_name)

    def get_short_name(self):
        """
            Этот метод требуется Django для таких вещей,
            как обработка электронной почты.
            Как правило, это будет имя пользователя.
        """
        return "{} {}.".format(self.first_name,  self.last_name)

    def set_auth(self):
        self.authorization = self._generate_jwt_token()
        self.save()

    def _generate_jwt_token(self):
        """
            Создает веб-токен JSON, в котором хранится идентификатор
            этого пользователя и срок его действия
            составляет 60 дней в будущем.
        """
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token


class FileManager(models.Model):
    video = models.FileField()
    text_doc = models.FileField(upload_to='media/doc', null=True)
    audio = models.CharField(max_length=255, null=True)
    full_text = models.TextField()
    short_text = models.CharField(max_length=255, null=True)
    profile = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.pk)

    class Meta:
        db_table = "file_manager"

    @property
    def get_data(self):
        return {
            'id': self.pk,
            'full_text': self.full_text,
            'short_text': self.short_text
        }

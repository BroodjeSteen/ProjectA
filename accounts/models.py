from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class Message(models.Model):
	name = models.CharField(max_length=50)
	message = models.TextField(max_length=140)
	created = models.DateTimeField(default=timezone.now)
	approved = models.BooleanField(default=False, null=True, blank=True)
	reviewed = models.DateTimeField(null=True, blank=True)
	station = models.CharField(max_length=8)
	moderator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

class CustomUserManager(BaseUserManager):
	def _create_user(self, email, password, first_name, last_name, **extra_fields):
		if not email:
			raise ValueError('Email must be provided')
		elif not password:
			raise ValueError('Password must be provided')
		elif not first_name:
			raise ValueError('First name must be provided')
		elif not last_name:
			raise ValueError('Last name must be provided')

		user = self.model(
			email = self.normalize_email(email),
			first_name = first_name,
			last_name = last_name,
			**extra_fields)

		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, email, password, first_name, last_name, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_active', True)
		extra_fields.setdefault('is_superuser', False)
		return self._create_user(email, password, first_name, last_name, **extra_fields)

	def create_superuser(self, email, password, first_name, last_name, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_active', True)
		extra_fields.setdefault('is_superuser', True)
		return self._create_user(email, password, first_name, last_name, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
	email = models.EmailField(unique=True, max_length=255)
	first_name  = models.CharField(max_length=30, null=True, blank=True)
	last_name   = models.CharField(max_length=50, null=True, blank=True)

	is_staff = models.BooleanField(default=True)
	is_active = models.BooleanField(default=True)
	is_superuser = models.BooleanField(default=False)

	objects = CustomUserManager()

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['first_name', 'last_name']

	class Meta:
		verbose_name = 'User'
		verbose_name_plural = 'Users'

	def clean(self, user, form):
		current_email = user.email
		user.email = form.cleaned_data.get('email')
		user.first_name = form.cleaned_data.get('first_name')
		user.last_name = form.cleaned_data.get('last_name')
		user.is_active = form.cleaned_data.get('is_active')
		user.is_superuser = form.cleaned_data.get('is_superuser')
		if User.objects.filter(email=user.email).exclude(email=current_email).exists():
			form.add_error('email', 'Email address is already taken')

	def __str__(self):
		return self.first_name + ' ' + self.last_name + ' | ' + self.email
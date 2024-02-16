# myapp/models.py
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.is_active=True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    location = models.CharField(max_length=1000, null=True, blank=True)
    quote = models.CharField(max_length=500, null=True, blank=True)
    bio = models.CharField(max_length=500, null=True, blank=True)
    avatar = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    blink_board = models.CharField(max_length=1000, null=True, blank=True)
    blink_board_image = models.ImageField(upload_to='blink_board_image', null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']


#class Friend(models.Model):
#     PENDING = 'Pending'
#     ACCEPTED = 'Accepted'
#     STATUS_CHOICES = [
#         (PENDING, 'Pending'),
#         (ACCEPTED, 'Accepted'),
#     ]
#
#     from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_as_user')
#     to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_as_friend')
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
#
#     def __str__(self):
#         return f"{self.user.username} - {self.friend.username}"


class Friends(models.Model):
    PENDING = 'Pending'
    ACCEPTED = 'Accepted'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
    ]

    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends_as_user')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends_as_friend')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    class Meta:
        # Define a unique constraint to create a composite primary key
        unique_together= ['to_user', 'from_user']

    def __str__(self):
        return f"{self.from_user.username} - {self.to_user.username}"



# class FriendRequest(models.Model):
#     PENDING = 'Pending'
#     ACCEPTED = 'Accepted'
#     REJECTED = 'Rejected'
#     STATUS_CHOICES = [
#         (PENDING, 'Pending'),
#         (ACCEPTED, 'Accepted'),
#         (REJECTED, 'Rejected'),
#     ]
#
#     from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
#     to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
#
#     def __str__(self):
#         return f"{self.from_user.username} to {self.to_user.username} - {self.status}"
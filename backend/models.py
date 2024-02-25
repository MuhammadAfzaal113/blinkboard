# myapp/models.py
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
import os

from blinkboard.settings import config


class Util:
    def make_ref(base='ABCDEFG2345HJKLMN6789PQRSTUVWXYZ'):
        import time
        b = len(base)
        raw = int(time.time() * 1e5 - 1.45e14)
        n = pow(raw, b, (b ** 7 - b ** 6 - 1)) + b ** 6
        ref = ""
        check = 0
        while n:
            check = (check + n) % b
            ref = base[n % b] + ref
            n //= b
            time.sleep(0.000000000001)
        return "-" + ref + base[(-check) % b]


def rename_media_file(instance, filename):
    try:
        if filename is None:
            # upload_to = 'SEQ-images/'
            filename = 'temp/blank.png'
            ext = filename.split('.')[-1]
            # get filename
            if instance.pk:
                filename = '{}.{}'.format(str(uuid.uuid4().hex) + '-ref' + Util.make_ref().replace("~", "-"), ext)
            else:
                # set filename as random string
                filename = '{}.{}'.format(str(uuid.uuid4().hex) + '-ref' + Util.make_ref().replace("~", "-"), ext)
                # filename = '{}.{}'.format(created_by, ext)
            # return the whole path to the file
        else:
            # upload_to = 'SEQ-images/'
            ext = filename.split('.')[-1]
            # get filename
            if instance.pk:
                filename = '{}.{}'.format(str(uuid.uuid4().hex) + '-ref' + Util.make_ref().replace("~", "-"), ext)
            else:
                # set filename as random string
                filename = '{}.{}'.format(str(uuid.uuid4().hex) + '-ref' + Util.make_ref().replace("~", "-"), ext)
                # filename = '{}.{}'.format(created_by, ext)
            # return the whole path to the file
        return os.path.join(filename)
    except Exception as ex:
        print(' Exception in rename image file : ', ex)


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.is_active = True
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
    avatar = models.FileField(upload_to=rename_media_file, max_length=5000, null=True,
                              default='https://d12uotnmkhw4d2.cloudfront.net/blank.png')
    blink_board = models.CharField(max_length=1000, null=True, blank=True)
    blink_board_image = models.FileField(upload_to=rename_media_file, max_length=5000, null=True,
                                         default='https://d12uotnmkhw4d2.cloudfront.net/blank.png')
    updated_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']


# class Friend(models.Model):
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
        unique_together = ['to_user', 'from_user']

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


def get_saved_photo(param, target='avatar'):
    try:
        if param:
            if isinstance(param, list):
                if target == 'avatar':
                    photo_details = User.objects.filter(avatar__in=param).all().values()
                elif target == 'blink_board_image':
                    photo_details = User.objects.filter(blink_board_image__in=param).all().values()

                # photo = photo_details[0] if photo_details else None
                photo_list = list()
                for photo in photo_details:
                    photo['media_file'] = f"https://{config['AWS_STORAGE_BUCKET_NAME']}.s3.amazonaws.com/" + \
                                          photo_details[0]['media_file'] if \
                        photo_details else None
                    photo_list.append(photo)
                return photo_list

            else:
                if target == 'avatar':
                    photo_details = User.objects.filter(avatar=param).all().values()
                elif target == 'blink_board_image':
                    photo_details = User.objects.filter(blink_board_image=param).all().values()
                photo = photo_details[0] if photo_details else None
                if photo:
                    photo['media_file'] = f"https://{config['AWS_STORAGE_BUCKET_NAME']}.s3.amazonaws.com/" + \
                                          photo_details[0]['media_file'] if \
                        photo_details else None
                    return photo
                else:
                    return None
        else:
            return None
    except Exception as e:
        print(f'[get_user_photo] throws exception {e}')
        return None

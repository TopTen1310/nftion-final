from allauth.account.models import EmailAddress
from django.db import models, IntegrityError
from django.contrib.auth.models import AbstractUser
from PIL import Image
from cloudinary.models import CloudinaryField
# from home.services import compressImage


class MyUser(AbstractUser):
    username = models.CharField(max_length=30, unique=False, null=True, blank=True)
    first_name = models.CharField(max_length=150, unique=False)
    email = models.EmailField(max_length=255, unique=True)
    REQUIRED_FIELDS = ['first_name', 'username']
    USERNAME_FIELD = 'email'

    def __str__(self):
        return str(self.first_name)


class Profile(models.Model):
    name = models.CharField(max_length=255)
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    avatar = CloudinaryField('image')
    bio = models.TextField(null=True, blank=True)
    wishlist_nft = models.ManyToManyField('home.Nft', related_name='wishlist_nft', verbose_name="User's wishlist nft")

    def save(self, *args, **kwargs):
        super().save()

    def __str__(self):
        return str(self.user.first_name)

    def set_user_profile_data(self, avatar, name, bio, username):
        self.user.username = username
        if avatar:
            self.avatar = avatar
        self.name = name
        self.bio = bio
        self.save()
        self.user.save()

    def get_email(self):
        return self.user.email

    def add_to_wishlist_nft(self, nft):
        self.wishlist_nft.add(nft)

    def get_wishlist_nft(self):
        return self.wishlist_nft.all()

    def remove_from_wishlist(self, nft):
        self.wishlist_nft.remove(nft)

    def get_profile_status(self):
        """ Active/Non active account """
        return EmailAddress.objects.filter(email=self.get_email()).first().verified


class ActivationCode(models.Model):
    ACTION_CHOICES = (
        ('email', 'email'),
        ('password', 'password'),
    )
    user = models.ForeignKey('Profile', on_delete=models.CASCADE)
    confirmation_code = models.CharField(max_length=4, null=True, blank=True)
    action = models.CharField(max_length=155, choices=ACTION_CHOICES, verbose_name='Activation code action')
    expired = models.BooleanField(default=False)
    change_to = models.CharField(max_length=155, verbose_name='Temporary data')

    def __str__(self):
        return self.user, self.confirmation_code

    def reset_temp_data(self):
        self.change_to = ''
        self.save()

    def set_expired(self):
        self.expired = True
        self.save()

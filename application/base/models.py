import os
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=True, max_length=254)
    bio = models.CharField(max_length=150, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        if self.profile_image:
            bd_profile_image = User.objects.get(email=self.email).profile_image

            if self.profile_image != bd_profile_image:
                uploaded_file = Image.open(self.profile_image)
                webp_output = BytesIO()
                uploaded_file.save(webp_output, format="webp", quality=80)
                webp_output.seek(0)

                # Create a new ImageField instance with the WebP content
                image_name, mail = str(self.email).split('@')
                self.profile_image = SimpleUploadedFile(
                    os.path.join(f'{image_name}_{mail}.webp'), webp_output.read(), content_type='image/webp'
                )

        super(User, self).save(*args, **kwargs)

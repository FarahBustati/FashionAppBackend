from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Clothes(models.Model):
    name = models.CharField(max_length=100)
    description=models.TextField()
    image_url=models.ImageField(upload_to='media/image/',null=False,blank=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Saved(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clothes = models.ForeignKey(Clothes, on_delete=models.CASCADE)
    Created_at= models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'clothes')

    def __str__(self):
        return f"{self.user.username}: {self.clothes.name}"


class Experiment(models.Model):
    user_photo_path=models.ImageField(upload_to='media/user_photo/')
    clothes_photo_path=models.ImageField(upload_to="media/cloths_photo/")
    models_photo_path=models.ImageField(upload_to='media/model_photo')

    def __str__(self):
        return self.models_photo_path


class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    experiment=models.ForeignKey(Experiment,on_delete=models.CASCADE)
    Created_at=models.DateField(auto_now_add=True)


class Feedback(models.Model):
    experiment =models.ForeignKey(Experiment,on_delete=models.CASCADE)
    rate = models.PositiveSmallIntegerField()
    description=models.TextField(null=True,blank=True)



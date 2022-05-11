from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.shortcuts import reverse
from versatileimagefield.fields import VersatileImageField

from file.models import File
from user.models import Person as User


class Post(models.Model):
    title = models.CharField(max_length=150, db_index=True)
    image = VersatileImageField(
        "Image",
        upload_to="uploads/images/",
        width_field="width",
        height_field="height",
        blank=True,
        null=True,
    )
    height = models.PositiveIntegerField("Image Height", blank=True, null=True)
    width = models.PositiveIntegerField("Image Width", blank=True, null=True)
    slug = models.SlugField(max_length=150, blank=False, unique=True)
    body = models.TextField(blank=True, db_index=True)
    date_pub = models.DateTimeField(auto_now_add=True)
    post_views = models.IntegerField(default=0)
    isMD = models.BooleanField(default=False)
    # Rating
    rating = models.FloatField(
        default=0, validators=[MaxValueValidator(5), MinValueValidator(0)]
    )
    rating_count = models.IntegerField(default=0)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    def count_rating(self, rate):
        self.rating = round(
            (self.rating * self.rating_count + rate) / (self.rating_count + 1)
        )
        self.rating_count += 1
        super(Post, self).save()

    def update_rating(self, old_rate, new_rate):
        self.rating = round(
            (self.rating * self.rating_count - old_rate + new_rate) / self.rating_count,
            2,
        )
        super(Post, self).save(update_fields=["rating"])

    def get_absolute_url(self):
        return reverse("post_view_url", kwargs={"slug": self.slug})

    def remove_rate(self, rate):
        self.rating = (self.rating * self.rating_count - rate) / (self.rating_count - 1)
        self.rating_count -= 1
        super(Post, self).save()

    def comments_sum(self):
        return len(Comment.objects.filter(post_id=self.id))

    def __str__(self):
        return self.title


class PostFile(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse("file_view", kwargs={"slug": self.file.slug})


class UserRate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    rating = models.IntegerField(
        blank=False, validators=[MaxValueValidator(5), MinValueValidator(0)]
    )

    def __str__(self):
        return self.user.username + " " + self.post.title + " " + str(self.rating)

    def get_absolute_url(self):
        return reverse("post_view_url", kwargs={"slug": self.post.slug})


class Comment(models.Model):
    name = models.CharField(max_length=100, blank=True)
    body = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
    from_user = models.BooleanField(default=False)
    sum_rate = models.IntegerField(default=0)

    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        return f"Comment {self.body} by {self.name}"

    def get_absolute_url(self):
        return reverse("post_view_url", kwargs={"slug": self.post.slug})


class CommentRate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    rate = models.BooleanField(blank=False)

    def __str__(self):
        if self.rate:
            return f"Thumb up by {self.user.username} on {self.comment}"
        else:
            return f"Thumb down by {self.user.username} on {self.comment}"

    def get_absolute_url(self):
        return reverse("post_view_url", kwargs={"slug": self.post.slug})

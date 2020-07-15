from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200,
                             verbose_name="Название"
                             )
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField("date published",
                                    auto_now_add=True
                                    )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="posts"
                               )
    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              related_name="group_posts",
                              blank=True,
                              null=True
                              )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Запись"
        verbose_name_plural = "Записи"

    def __str__(self):
        return self.text
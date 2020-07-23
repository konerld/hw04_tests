from django.forms import ModelForm
from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ("group", "text") #'image')
        help_texts = {
            "text": "Текст записи",
            "group": "Сообщества",
            # "image": "Изображение"
        }
        labels = {
            "text": "Текст записи",
            "group": "Сообщества",
            # "image": "Изображение"
        }
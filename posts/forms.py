from django.forms import ModelForm
from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ("group", "text")
        help_texts = {
            "text": "Текст записи",
            "group": "Сообщества",
        }
        labels = {
            "text": "Текст записи",
            "group": "Сообщества",
        }
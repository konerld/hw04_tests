from django.test import TestCase, Client
from posts.models import Post, User
from datetime import datetime as dt

now = dt.now()


class PageTest(TestCase):
    def setUp(self):
        self.time_stamp = str(dt.timestamp(now)).replace('.', '')
        self.client = Client()
        self.user = User.objects.create_user(
            username='skywalker',
            password='123456'
        )
        self.post = Post.objects.create(
            text=f"Test post at {self.time_stamp}",
            author=self.user
        )

    def test_client_page(self):
        """
        Тест проверяет, что осле регистрации пользователя создается
        его персональная страница (profile)
        """
        response = self.client.get("/skywalker/")
        self.assertEqual(response.status_code,
                         200,
                         "Страница '/skywalker/' не найдена!")

    def test_create_post_by_auth_user(self):
        """
        Тест проверяет, что авторизованный
        пользователь может опубликовать пост (new)
        """
        if self.client.login(username='skywalker', password='123456'):
            response = self.client.get('/new/')
            self.assertEqual(response.status_code,
                             200,
                             'Авторизованный пользователь не может создать post')
        else:
            self.assertTrue(False, 'Пользователь skywalker - не авторизован!')

    def test_create_post_by_non_auth_user(self):
        """
        Тест проверяет, что НЕ авторизованный
        пользователь НЕ может опубликовать пост (new)
        """
        self.client.logout()
        response = self.client.get('/new/')
        self.assertRedirects(response,
                             '/auth/login/?next=/new/',
                             msg_prefix="Не авторизованный пользователь"
                                        "не переадресовывается на страницу "
                                        "входа (login)!")

    def test_post_exists_at_homepage(self):
        """
        Тест проверяет, что после публикации поста новая запись появляется:
        - на главной странице сайта (index)
        """
        response = self.client.get('/')
        self.assertIn(self.post,
                      response.context['page'],
                      'Пост НЕ отображается на домашней странице!')
        self.assertEqual(self.post,
                         response.context['page'][0],
                         "Текст поста НЕ отображается на домашней странице!")

    def test_post_exists_on_profile_page(self):
        """
        Тест проверяет, что после публикации поста новая запись появляется:
        - на персональной странице пользователя (profile)
        """
        response = self.client.get(f'/skywalker/')
        self.assertIn(self.post,
                      response.context['page'],
                      "Пост НЕ отображается на странице пользователя!")
        self.assertEqual(self.post,
                         response.context['page'][0],
                         "Текст поста НЕ отображается на странице пользователя!")

    def test_post_exists_on_post_self_page(self):
        """
        Тест проверяет, что после публикации поста новая запись появляется:
        - на отдельной странице поста (post)
        """
        response = self.client.get(f'/skywalker/{self.post.id}/')

        self.assertEqual(self.post,
                         response.context['post'],
                         "Пост не отображается на собственной странице!")

    def test_auth_user_can_edit_own_post(self):
        """
        Тест проверяет, что авторизованный пользователь может отредактировать
        свой пост и его содержимое изменится на всех связанных страницах
        """
        self.client.login(username='skywalker', password='123456')
        response = self.client.get(f'/skywalker/{self.post.id}/edit/')
        self.assertEqual(response.status_code,
                         200,
                         'У пользователя нет доступа к '
                         'редактированию своего поста!')
        new_text = 'This is text after edit.'
        response = self.client.post(f'/skywalker/{self.post.id}/edit/', {'text': new_text})
        response = self.client.get(f'/skywalker/{self.post.id}/edit/')
        self.assertIn(bytes(new_text, encoding='UTF-8'), response.content)

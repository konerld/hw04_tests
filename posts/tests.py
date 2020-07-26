from django.test import TestCase, Client
from posts.models import Post, User
from django.urls import reverse


class PageTest(TestCase):
    def setUp(self):
        self.auth_client = Client()
        self.user = User.objects.create_user(
            username='skywalker',
            password='123456'
        )
        self.auth_client.force_login(self.user)
        self.non_auth_client = Client()

        self.post = Post.objects.create(
            text=f"Test post at blablabla",
            author=self.user
        )

    def test_client_page(self):
        """
        Тест проверяет, что осле регистрации пользователя создается
        его персональная страница (profile)
        """
        response = self.auth_client.get(
            reverse(
                "profile",
                kwargs={'username': self.user.username}
            )
        )
        self.assertEqual(response.status_code,
                         200,
                         "Страница '/skywalker/' не найдена!")

    def test_create_post_by_auth_user(self):
        """
        Тест проверяет, что авторизованный
        пользователь может опубликовать пост (new)
        """
        response = self.auth_client.post(
            reverse("new_post"),
            data={
                'group': '',
                'text': 'test'
            },
            follow=True
        )
        self.assertEqual(response.status_code,
                         200,
                         "Ошибка создания поста!")
        created_post = Post.objects.all().first()
        response = self.auth_client.get(
            reverse(
                "post",
                kwargs={
                    'username': self.user.username,
                    'post_id': created_post.id}
            )
        )
        self.assertContains(response, 'test', status_code=200)

    def test_create_post_by_non_auth_user(self):
        """
        Тест проверяет, что НЕ авторизованный
        пользователь НЕ может опубликовать пост (new)
        """
        self.auth_client.logout()
        response = self.auth_client.get(
            reverse("new_post")
        )
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
        response = self.auth_client.get(reverse('index'))
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
        response = self.auth_client.get(
            reverse(
                "profile",
                kwargs={'username': self.user.username}
            )
        )
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
        response = self.auth_client.get(
            reverse(
                "post",
                kwargs={
                    'username': self.post.author.username,
                    'post_id': self.post.id}
            )
        )
        self.assertEqual(self.post,
                         response.context['post'],
                         "Пост не отображается на собственной странице!")

    def test_auth_user_can_edit_own_post(self):
        """
        Тест проверяет, что авторизованный пользователь может отредактировать
        свой пост и его содержимое изменится на всех связанных страницах
        """
        self.auth_client.login(username='skywalker', password='123456')
        response = self.auth_client.get(
            reverse(
                "post_edit",
                kwargs={
                    'username': self.post.author.username,
                    'post_id': self.post.id
                }
            )
        )
        self.assertEqual(response.status_code,
                         200,
                         'У пользователя нет доступа к '
                         'редактированию своего поста!')
        new_text = 'This is text after edit.'
        response = self.auth_client.post(
            reverse(
                "post_edit",
                kwargs={
                    'username': self.post.author.username,
                    'post_id': self.post.id
                }
            ),
            data={'text': new_text}
        )

        response = self.auth_client.get(
            reverse(
                "post",
                kwargs={
                    'username': self.post.author.username,
                    'post_id': self.post.id}
            )
        )
        self.assertContains(response, new_text, status_code=200)

    def test_404(self):
        no_page = '/unknown/'
        response = self.auth_client.get(no_page)
        self.assertEqual(response.status_code,
                         404,
                         f'Страница {no_page} существует '
                         ' проверьте ошибку 404 на другой странице!')

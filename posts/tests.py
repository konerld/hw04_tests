from django.test import TestCase, Client
from posts.models import Post, User, Group
from django.urls import reverse


class PageTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='skywalker')
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

        self.non_auth_client = Client()
        self.group = Group.objects.create(
            title="test group",
            slug='test-slug',
            description='description',
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
                         "Страница пользователя не найдена!")

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
        self.non_auth_client.logout()
        response = self.non_auth_client.get(
            reverse("new_post")
        )
        self.assertRedirects(response,
                             '/auth/login/?next=/new/',
                             msg_prefix="Не авторизованный пользователь"
                                        "не переадресовывается на страницу "
                                        "входа (login)!")

    def test_post_exists_on_pages(self):
        """
        Тест создает пост и проверяет его отображение по всем страницам из
        спискка urls_list
        """
        text = 'text in test post'
        post = Post.objects.create(
            text=text,
            author=self.user,
            group=self.group
        )

        urls_list = [
            reverse(
                'index'
            ),
            reverse(
                'profile',
                kwargs={
                    'username': self.user.username
                }
            ),
            reverse(
                'post',
                kwargs={
                    'username': self.user.username,
                    'post_id': post.id
                }
            )
        ]

        for url in urls_list:
            response = self.auth_client.get(url)
            self.assertEqual(response.status_code, 200)
            if 'paginator' in response.context:
                check_post = response.context['page'][0]
            else:
                check_post = response.context['post']

            self.assertEqual(check_post.text, text)
            self.assertEqual(check_post.group, self.group)
            self.assertEqual(check_post.author, self.user)

    def test_auth_user_can_edit_own_post(self):
        """
        Тест проверяет, что авторизованный пользователь может отредактировать
        свой пост и его содержимое изменится на всех связанных страницах
        """
        post = Post.objects.create(
            text='old text in post',
            author=self.user,
            group=self.group
        )

        edit_urls_list = [
            reverse(
                'index'
            ),
            reverse(
                'profile',
                kwargs={
                    'username': self.user.username
                }
            ),
            reverse(
                'post',
                kwargs={
                    'username': self.user.username,
                    'post_id': post.id
                }
            )
        ]
        new_text = 'This is text after edit.'
        response = self.auth_client.post(
            reverse(
                'post_edit',
                kwargs={
                    'post_id': post.id,
                    'username': post.author.username
                }
            ),
            data={
                'group': self.group,
                'text': new_text
            }
        )
        self.assertEqual(response.status_code, 200)
        for url in edit_urls_list:
            response = self.auth_client.get(url)
            if 'paginator' in response.context:
                check_post = response.context['page'][0]
            else:
                check_post = response.context['post']
            # Все вроде поправил, только тут уже голову сломал
            # почему то здесь check_post не меняется текст поста
            self.assertEqual(check_post.text, new_text)

    def test_404(self):
        no_page = '/unknown/'
        response = self.auth_client.get(no_page)
        self.assertEqual(response.status_code,
                         404,
                         f'Страница {no_page} существует '
                         ' проверьте ошибку 404 на другой странице!')

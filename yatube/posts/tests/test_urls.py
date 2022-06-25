from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client

from ..models import Group, Post, User

User = get_user_model()


class PostURLTests(TestCase):
    """Тестируем URLs приложения posts."""
    @classmethod
    def setUpClass(cls):
        """Создаем тестовые экземпляры моделей User,Group,Post."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='noname')
        cls.user_not_author = User.objects.create_user(username='noname_2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-groupname-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        """Создаем тестовые экземпляры анонимного и авторизованных
        пользователей."""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2.force_login(self.user_not_author)
        cache.clear()

    def test_urls_exist_at_desired_location_anonymous(self):
        """Проверяем доступность всех адресов для анонимного пользователя."""
        guest_urls = {
            '/': HTTPStatus.OK.value,
            f'/group/{self.group.slug}/': HTTPStatus.OK.value,
            f'/profile/{self.user.username}/': HTTPStatus.OK.value,
            f'/posts/{self.post.id}/': HTTPStatus.OK.value,
            f'/posts/{self.post.id}/edit/': HTTPStatus.FOUND.value,
            '/create/': HTTPStatus.FOUND.value,
            '/unexisting_page/': HTTPStatus.NOT_FOUND.value,
        }
        for address, status_code in guest_urls.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_urls_exist_at_desired_location_authorized(self):
        """Проверяем доступность приватных адресов для авторизованного
        пользователя."""
        authorized_urls = {
            f'/posts/{self.post.id}/edit/': HTTPStatus.OK.value,
            '/create/': HTTPStatus.OK.value,
        }
        for address, status_code in authorized_urls.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_urls_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_post_edit_url_redirects_anonymous(self):
        """Страница по адресу /posts/post_id/edit перенаправит анонимного
        пользователя на страницу логина.
        """
        address = f'/posts/{self.post.id}/edit/'
        response = self.guest_client.get(address, follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/edit/')

    def test_post_edit_url_redirects_authorized_not_author(self):
        """Страница по адресу /posts/post_id/edit перенаправит авторизованного
        пользователя, не автора, на страницу поста.
        """
        address = f'/posts/{self.post.id}/edit/'
        response = self.authorized_client_2.get(address, follow=True)
        self.assertRedirects(
            response, f'/posts/{self.post.id}/')

    def test_post_edit_url_uses_correct_template_post_author(self):
        """Страница по адресу /posts/post_id/edit использует
        соответствующий шаблон для автора поста.
        """
        address = f'/posts/{self.post.id}/edit/'
        response = self.authorized_client.get(address)
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_urls_redirect_authorized(self):
        """Страницы profile_follow, profile_unfollow, add_comment перенаправят
        авторизованного пользователя.
        """
        adresses = {
            f'/posts/{self.post.id}/comment/':
                f'/posts/{self.post.id}/',
            f'/profile/{self.user.username}/follow/':
                f'/profile/{self.user.username}/',
            f'/profile/{self.user.username}/unfollow/':
                f'/profile/{self.user.username}/',
        }
        for address, redirect_adress in adresses.items():
            with self.subTest(address=address):
                response = self.authorized_client_2.get(address)
                self.assertRedirects(response, redirect_adress)

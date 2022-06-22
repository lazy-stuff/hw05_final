import shutil
import tempfile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django import forms

from ..models import Group, Post, User, Follow

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    """Тестируем view-функции приложения posts."""
    @classmethod
    def setUpClass(cls):
        """Создаем тестовые экземпляры моделей User,Group,Post."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='noname')
        cls.user_not_author = User.objects.create_user(username='noname_2')
        cls.user_not_follower = User.objects.create_user(username='noname_3')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-groupname-slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-groupname-slug-2',
            description='Тестовое описание - 2',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded
        )
        cls.follower = Follow.objects.create(
            user=cls.user_not_author,
            author=cls.user
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Создаем тестовые экземпляры анонимного и авторизованного
        пользователей."""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_2 = Client()
        self.authorized_client_3 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2.force_login(self.user_not_author)
        self.authorized_client_3.force_login(self.user_not_follower)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:follow_index'): 'posts/follow.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}):
            'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.user.username}):
            'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}):
            'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}):
            'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def post_assert_method_context(self, first_object):
        """Проверка вывода в шаблон id, текста, группы и автора."""
        self.assertEqual(first_object.id, self.post.id)
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.group, self.post.group)
        self.assertEqual(first_object.author, self.post.author)
        self.assertEqual(first_object.image, self.post.image)

    def post_assert_method_form(self, response):
        """Проверка вывода в шаблон корректной формы."""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.post_assert_method_context(first_object)

    def test_group_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][0]
        self.post_assert_method_context(first_object)

    def test_group_2_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group_2.slug}))
        first_object = response.context['page_obj']
        self.assertFalse(self.post.text in first_object)

    def test_profile_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        first_object = response.context['page_obj'][0]
        self.post_assert_method_context(first_object)

    def test_post_detail_show_correct_context_anonymous(self):
        """Шаблон post_detail для анонимного пользователя
        сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        first_object = response.context['post']
        self.post_assert_method_context(first_object)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}))
        first_object = response.context['post']
        self.post_assert_method_context(first_object)
        self.post_assert_method_form(response)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.post_assert_method_form(response)

    def test_index_page_cache(self):
        """Проверка кэширования страницы index."""
        response = self.authorized_client.get(reverse('posts:index'))
        page_content = response.content
        Post.objects.create(
            text='Ещё один тестовый текст',
            author=self.user
        )
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(page_content, response.content)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(page_content, response.content)

    def test_profile_follower_authorized(self):
        """Проверка функции подписки/удаления подписки
        на странице profile."""
        self.authorized_client_2.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        following = Follow.objects.filter(
            user=self.user_not_author, author=self.user)
        self.assertTrue(following.exists())
        following.delete()
        following = Follow.objects.filter(
            user=self.user_not_author, author=self.user)
        self.assertFalse(following.exists())

    def test_follow_index_page_content(self):
        """Проверка, что новая запись автора появляется у
        подписчиков и не появляется в ленте тех, кто не подписан."""
        Post.objects.create(
            text='Новый пост автора',
            author=self.user
        )
        response_follower = self.authorized_client_2.get(
            reverse('posts:follow_index')
        )
        last_post = response_follower.context['page_obj'][0]
        self.assertEqual(last_post.text, 'Новый пост автора')
        response_non_follower = self.authorized_client_3.get(
            reverse('posts:follow_index')
        )
        self.assertFalse(
            'Новый пост автора' in response_non_follower.context['page_obj']
        )


class PaginatorViewsTest(TestCase):
    """Тестируем паджинатор приложения posts."""
    @classmethod
    def setUpClass(cls):
        """Создаем тестовые экземпляры моделей User,Group,Post."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='noname')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-groupname-slug',
            description='Тестовое описание',
        )
        for i in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост №{i}.',
                group=cls.group)

    def setUp(self):
        """Создаем тестовый экземпляр анонимного пользователя."""
        self.guest_client = Client()
        cache.clear()

    def test_first_page_contains_ten_records(self):
        """Проверка: количество постов на первой странице равно 10."""
        pages_names = {
            'index': reverse('posts:index'),
            'group_list': reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}),
            'profile': reverse(
                'posts:profile', kwargs={'username': self.user.username}),
        }
        for reverse_name in pages_names.values():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """Проверка: количество постов на первой странице равно 3."""
        pages_names = {
            'index': (reverse('posts:index') + '?page=2'),
            'group_list': (reverse(
                'posts:group_list', kwargs={'slug': self.group.slug})
                + '?page=2'),
            'profile': (reverse(
                'posts:profile', kwargs={'username': self.user.username})
                + '?page=2'),
        }
        for reverse_name in pages_names.values():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 3)

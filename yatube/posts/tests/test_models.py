from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, User, Comment, Follow


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем тестовые экземпляры моделей User,Group,Post."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_not_author = User.objects.create_user(username='noname')
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
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user_not_author,
            text='Новый комментарий'
        )
        cls.follow = Follow.objects.create(
            user=cls.user_not_author,
            author=cls.user
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        comment = PostModelTest.comment
        follow = PostModelTest.follow
        models = {
            post: post.text,
            group: group.title,
            comment: comment.text,
            follow:
                f'{follow.user.username} подписан на {follow.author.username}',
        }
        for field, expected_text in models.items():
            with self.subTest(field=field):
                self.assertEqual(
                    str(field), expected_text)

    def test_verbose_name_post(self):
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_verbose_name_group(self):
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        field_verboses = {
            'title': 'Название',
            'slug': 'Псевдоним',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_verbose_name_comment(self):
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        comment = PostModelTest.comment
        field_verboses = {
            'post': 'Пост',
            'author': 'Автор',
            'text': 'Текст комментария',
            'created': 'Дата публикации комментария',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_verbose_name_follow(self):
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        follow = PostModelTest.follow
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follow._meta.get_field(field).verbose_name, expected_value)

    def test_help_text_post(self):
        """Проверяем, что help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

    def test_help_text_comment(self):
        """Проверяем, что help_text в полях совпадает с ожидаемым."""
        comment = PostModelTest.comment
        help_text = comment._meta.get_field('text').help_text
        self.assertEqual(help_text, 'Текст комментария')

from django.test import TestCase, Client


class AboutURLTests(TestCase):
    """Тестируем URLs приложения about."""
    def setUp(self):
        """Создаем тестовый экземпляр неавторизованного пользователя."""
        self.guest_client = Client()

    def test_url_exists_at_desired_location(self):
        """Проверяем доступность адресов /about/author/ и /about/tech/."""
        urls = {
            '/about/author/': 200,
            '/about/tech/': 200,
        }
        for address, status_code in urls.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_about_url_uses_correct_template(self):
        """Проверяем, что URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

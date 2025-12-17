from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import NoReverseMatch, reverse

from notes.models import Note

User = get_user_model()


def reverse_any(names):
    last = None
    for name in names:
        try:
            return reverse(name)
        except NoReverseMatch as exc:
            last = exc
    raise last


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username="author", password="pass12345")
        cls.other = User.objects.create_user(username="other", password="pass12345")

        cls.note = Note.objects.create(
            title="My note", text="Text", slug="my-note", author=cls.author
        )

        cls.home_url = reverse("notes:home")
        cls.list_url = reverse("notes:list")
        cls.success_url = reverse("notes:success")
        cls.add_url = reverse("notes:add")
        cls.detail_url = reverse("notes:detail", args=(cls.note.slug,))
        cls.edit_url = reverse("notes:edit", args=(cls.note.slug,))
        cls.delete_url = reverse("notes:delete", args=(cls.note.slug,))

        # auth urls могут называться по-разному, пробуем популярные варианты
        cls.login_url = reverse_any(["users:login", "login", "accounts:login"])
        cls.logout_url = reverse_any(["users:logout", "logout", "accounts:logout"])
        cls.signup_url = reverse_any(["users:signup", "signup", "accounts:signup"])

    def test_home_available_for_anonymous(self):
        resp = self.client.get(self.home_url)
        self.assertEqual(resp.status_code, 200)

    def test_auth_user_pages_available(self):
        self.client.login(username="author", password="pass12345")

        self.assertEqual(self.client.get(self.list_url).status_code, 200)
        self.assertEqual(self.client.get(self.success_url).status_code, 200)
        self.assertEqual(self.client.get(self.add_url).status_code, 200)

    def test_note_pages_available_only_for_author(self):
        # автор
        self.client.login(username="author", password="pass12345")
        self.assertEqual(self.client.get(self.detail_url).status_code, 200)
        self.assertEqual(self.client.get(self.edit_url).status_code, 200)
        self.assertEqual(self.client.get(self.delete_url).status_code, 200)

        # другой пользователь -> 404 (из-за get_queryset в NoteBase)
        self.client.logout()
        self.client.login(username="other", password="pass12345")
        self.assertEqual(self.client.get(self.detail_url).status_code, 404)
        self.assertEqual(self.client.get(self.edit_url).status_code, 404)
        self.assertEqual(self.client.get(self.delete_url).status_code, 404)

    def test_anonymous_redirected_to_login_for_protected_pages(self):
        protected = [
            self.list_url,
            self.success_url,
            self.add_url,
            self.detail_url,
            self.edit_url,
            self.delete_url,
        ]
        for url in protected:
            with self.subTest(url=url):
                resp = self.client.get(url)
                self.assertRedirects(resp, f"{settings.LOGIN_URL}?next={url}")

    def test_signup_login_logout_available_for_all(self):
        self.assertEqual(self.client.get(self.signup_url).status_code, 200)
        self.assertEqual(self.client.get(self.login_url).status_code, 200)

        # logout часто бывает только POST; главное — доступен не только “особым” пользователям
        resp = self.client.post(self.logout_url)
        self.assertIn(resp.status_code, (200, 302))

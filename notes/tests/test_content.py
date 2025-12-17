from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username="author", password="pass12345")
        cls.other = User.objects.create_user(username="other", password="pass12345")

        cls.note_author = Note.objects.create(
            title="A1", text="t", slug="a1", author=cls.author
        )
        cls.note_other = Note.objects.create(
            title="B1", text="t", slug="b1", author=cls.other
        )

        cls.list_url = reverse("notes:list")
        cls.add_url = reverse("notes:add")
        cls.edit_url = reverse("notes:edit", args=(cls.note_author.slug,))

    def test_note_in_object_list_on_list_page(self):
        self.client.login(username="author", password="pass12345")
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, 200)

        object_list = resp.context["object_list"]
        self.assertIn(self.note_author, object_list)

    def test_other_users_notes_not_in_list(self):
        self.client.login(username="author", password="pass12345")
        resp = self.client.get(self.list_url)
        object_list = resp.context["object_list"]

        self.assertIn(self.note_author, object_list)
        self.assertNotIn(self.note_other, object_list)

    def test_forms_passed_to_add_and_edit_pages(self):
        self.client.login(username="author", password="pass12345")

        resp_add = self.client.get(self.add_url)
        self.assertIn("form", resp_add.context)

        resp_edit = self.client.get(self.edit_url)
        self.assertIn("form", resp_edit.context)

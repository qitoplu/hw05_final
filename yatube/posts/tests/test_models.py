from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import CONSTANT_SYMBOLS, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='В дверь постучали восемь раз. "Осьминог", - подумал Штирлиц',
        )

    def test_str(self):
        self.assertEqual(self.post.text[:CONSTANT_SYMBOLS], str(self.post))

    def test_models_have_correct_object_names(self):
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_models_have_correct_object_names_post(self):
        post = PostModelTest.post
        expected_object_name = post.text[:CONSTANT_SYMBOLS]
        self.assertEqual(expected_object_name, str(post))

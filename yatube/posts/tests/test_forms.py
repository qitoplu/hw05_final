import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user('test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            author=self.user,
            text='Текст нового поста',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        form_data = {
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user})
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=None,
                image='posts/small.gif',
            ).exists()
        )

    def test_post_edit_works_correctly(self):
        self.post = Post.objects.create(text='Тестовый текст',
                                        author=self.user,
                                        group=self.group)
        previous_text = self.post
        self.newgroup = Group.objects.create(
            title='Тестовая группа2',
            slug='test-group',
            description='Описание'
        )
        form_data = {
            'text': 'Новый текст формы',
            'group': self.newgroup.id
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': previous_text.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
            author=self.user,
            group=self.newgroup.id,
            pub_date=self.post.pub_date,
            id=previous_text.id
        ).exists()
        )
        self.assertNotEqual(previous_text.text, form_data['text'])
        self.assertNotEqual(previous_text.group, form_data['group'])

    def test_comments_work_correctly(self):
        comments_count = Comment.objects.count()
        user = User.objects.create(username='user')
        form = {
            'text': 'Текст комментария',
            'author': user
        }
        self.authorized_client.force_login(user)
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form,
            follow=True
        )
        self.assertRedirects(
            response, f'/posts/{self.post.id}/'
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(f'{self.post.comments.all()[0]}', form['text'])

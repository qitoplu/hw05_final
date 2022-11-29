from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='boba')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTest.user)

    def test_urls_status(self):
        pages = (
            '/',
            f'/posts/{self.post.id}/',
            f'/profile/{self.user}/',
            f'/group/{self.group.slug}/',
        )
        for page in pages:
            response = self.client.get(page)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_redirect_anonymous(self):
        response = self.client.get(f'/posts/{self.post.id}/edit/')
        self.assertRedirects(
            response, (f'/auth/login/?next=/posts/{self.post.id}/edit/'))

    def test_post_create_url_redirect_anonymous(self):
        response = self.client.get('/create/')
        self.assertRedirects(
            response, ('/auth/login/?next=/create/'))

    def unexisting_page(self):
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_edit_url(self):
        author = PostURLTest.user
        post = Post.objects.create(
            author=author,
            text='Текст поста',
            group=self.group
        )
        self.authorized_client.force_login(author)
        response = self.authorized_client.get(f'/posts/{post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        cache.clear()
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{PostURLTest.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostURLTest.user}/': 'posts/profile.html',
            f'/posts/{PostURLTest.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{PostURLTest.post.id}/edit/': 'posts/create_post.html',
            '/unexisting_page/': 'core/404.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_cache(self):
        new_post = Post.objects.create(
            text='test cache',
            author=PostURLTest.user,
            group=PostURLTest.group
        )
        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.context.get('page_obj').object_list
        new_post.delete()
        posts_new = response.context.get('page_obj').object_list
        self.assertEqual(len(posts), len(posts_new))

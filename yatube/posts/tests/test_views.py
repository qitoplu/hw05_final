from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from core.utils import POSTS_QUANTITY

from ..models import Follow, Group, Post

POSTS_OVERALL = 13
User = get_user_model()


class PostPagesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        self.post = Post.objects.create(
            text='Тестовый текст',
            group=self.group,
            author=self.user
        )

    def test_pages_uses_correct_template(self):
        cache.clear()
        templates_pages_names = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.user}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.pk}
            ): 'posts/create_post.html',
            reverse(
                'posts:post_create'
            ): 'posts/create_post.html'
        }
        for address, template in templates_pages_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def same_obj(self, post1, post2):
        self.assertEqual(post2.text, post1.text)
        self.assertEqual(post2.group, post1.group)
        self.assertEqual(post2.author, post1.author)
        self.assertEqual(post2.image, post1.image)

    def test_index_page_show_correct_context(self):
        cache.clear()
        response = self.authorized_client.get(reverse(
            'posts:index'
        ))
        post = response.context['page_obj'][0]
        self.same_obj(post, self.post)

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test-slug'}
        ))
        post = response.context['page_obj'][0]
        self.same_obj(post, self.post)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user}
        ))
        post = response.context['page_obj'][0]
        self.same_obj(post, self.post)

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}
        ))
        post = response.context.get('post')
        self.same_obj(post, self.post)

    def test_post_create_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_create'
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.pk}
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_added_correctly(self):
        cache.clear()
        response_index = self.authorized_client.get(
            reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}))
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user}))
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(self.post, index)
        self.assertIn(self.post, group)
        self.assertIn(self.post, profile)


class TestPaginator(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user('test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        posts_list = []
        for i in range(POSTS_OVERALL):
            posts_list.append(Post(
                author=self.user,
                text=f'Текстовый текст {i}',
                group=self.group,
                pk=i
            ))
        self.post = Post.objects.bulk_create(posts_list)

    def test_paginator_works_guest(self):
        cache.clear()
        pages = (reverse('posts:index'),
                 reverse('posts:profile', kwargs={'username': self.user}),
                 reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        for page in pages:
            response_first = self.guest_client.get(page)
            response_second = self.guest_client.get(page + '?page=2')
            count_posts_first = len(response_first.context['page_obj'])
            count_posts_second = len(response_second.context['page_obj'])
            self.assertEqual(
                count_posts_first,
                POSTS_QUANTITY
            )
            self.assertEqual(
                count_posts_second,
                POSTS_OVERALL - POSTS_QUANTITY
            )

    def test_paginator_works_authorized(self):
        cache.clear()
        pages = (reverse('posts:index'),
                 reverse('posts:profile', kwargs={'username': self.user}),
                 reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        for page in pages:
            response_first = self.authorized_client.get(page)
            response_second = self.authorized_client.get(page + '?page=2')
            count_posts_first = len(response_first.context['page_obj'])
            count_posts_second = len(response_second.context['page_obj'])
            self.assertEqual(
                count_posts_first,
                POSTS_QUANTITY
            )
            self.assertEqual(
                count_posts_second,
                POSTS_OVERALL - POSTS_QUANTITY
            )

    def test_cache_index(self):
        post = Post.objects.create(
            text='Текст',
            author=self.user)
        response1 = self.authorized_client.get(
            reverse('posts:index')).content
        post.delete()
        response2 = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertEqual(response1, response2)
        cache.clear()
        response3 = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(response2, response3)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.subscriberr = User.objects.create(username='Подписчик')
        cls.not_subscriber = User.objects.create(username='Не подписчик')
        cls.authorr = User.objects.create(username='Автор')
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.authorr,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.authorr)
        self.follower = Client()
        self.follower.force_login(self.subscriberr)
        self.nonfollower = Client()
        self.nonfollower.force_login(self.not_subscriber)
        cache.clear()

    def test_follow_index(self):
        Follow.objects.create(
            user=self.subscriberr,
            author=self.authorr
        )
        response1 = self.follower.get(reverse('posts:follow_index'))
        response2 = self.nonfollower.get(reverse('posts:follow_index'))
        follow = response1.context['page_obj']
        nonfollow = response2.context['page_obj']
        self.assertIn(self.post, follow)
        self.assertNotIn(self.post, nonfollow)

    def test_follow_on_user(self):
        count = Follow.objects.count()
        self.follower.post(
            reverse('posts:profile_follow',
                    kwargs={'username': self.authorr}))
        follow = Follow.objects.all().latest('id')
        self.assertEqual(Follow.objects.count(), count + 1)
        self.assertEqual(follow.author_id, self.authorr.id)
        self.assertEqual(follow.user_id, self.subscriberr.id)

    def test_unfollow_on_user(self):
        Follow.objects.create(user=self.subscriberr,
                              author=self.authorr)
        count = Follow.objects.count()
        self.follower.post(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.authorr}))
        self.assertEqual(Follow.objects.count(), count - 1)

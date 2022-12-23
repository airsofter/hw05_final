from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache


from ..models import User, Post, Group, Follow
from .utils import SetUpMixin


class PostsPagesTests(SetUpMixin, TestCase):
    def test_pages_uses_correct_template(self):
        """URL uses correct template."""
        cache.clear()
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            (
                reverse('posts:group_list',
                        kwargs={'slug': 'test-slug'})
            ): 'posts/group_list.html',
            (
                reverse('posts:profile',
                        kwargs={'username': self.post.author})
            ): 'posts/profile.html',
            (
                reverse('posts:post_detail',
                        kwargs={'post_id': self.post.id})
            ): 'posts/post_detail.html',
            (
                reverse('posts:post_edit',
                        kwargs={'post_id': self.post.id})
            ): 'posts/post_create.html',
            reverse('posts:post_create'): 'posts/post_create.html'
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_index_group_profile_page_show_correct_context(self):
        """Test correct context pages index, group, profile"""
        cache.clear()
        response_list = [
            self.author_client.get(reverse('posts:index')),
            self.author_client.get(reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            )),
            self.author_client.get(reverse(
                'posts:profile', kwargs={'username': self.user.username}
            ))
        ]
        for response in response_list:
            first_object = response.context['page_obj'][0]
            context_objects = {
                self.group: first_object.group,
                self.post.author: first_object.author,
                self.post.text: first_object.text,
                self.group.slug: first_object.group.slug,
                self.post.id: first_object.id,
                self.post.image: first_object.image
            }
            for reverse_name, response_name in context_objects.items():
                with self.subTest(reverse_name=reverse_name):
                    self.assertEqual(response_name, reverse_name)

    def test_post_post_detail(self):
        """Test context template post_detail"""
        post_object = Post.objects.get(pk=1)
        response = self.author_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': post_object.id}
        ))
        self.assertEqual(post_object.text, response.context['post'].text)
        self.assertEqual(post_object.image, response.context['post'].image)

    def test_post_post_create_post_edit(self):
        """Test context in post_create and post_edit"""

        post_object = Post.objects.get(pk=1)

        respose_is_edit = self.author_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': post_object.id})
        )
        self.assertEqual(
            True, respose_is_edit.context['is_edit']
        )
        self.assertEqual(
            post_object.id, respose_is_edit.context['post_id']
        )
        response_list_form = [
            self.author_client.get(reverse('posts:post_create')),
            respose_is_edit
        ]
        for response in response_list_form:
            for value, expected in self.form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_post_group_context(self):
        """Test post output with a group"""
        cache.clear()
        group_obj = Group.objects.get(title='Тестовая группа')
        post_obj = Post.objects.create(
            author=self.user,
            text='Новый пост',
            group=group_obj
        )
        test_urls = {
            'posts:index': None,
            'posts:group_list': {'slug': group_obj.slug},
            'posts:profile': {'username': self.user.username}
        }
        for name, kwargs in test_urls.items():
            response = self.client.get(reverse(name, kwargs=kwargs))
            self.assertEqual(response.context['page_obj'][0], post_obj)

    def test_correct_cache_working(self):
        """checking operation of the index page cache"""
        cache.clear()
        response = self.guest_client.get('/')
        cached_response_content = response.content
        Post.objects.create(text='Второй пост', author=self.user)
        response = self.guest_client.get('/')
        self.assertEqual(cached_response_content, response.content)
        cache.clear()
        response = self.client.get('/')
        self.assertNotEqual(cached_response_content, response.content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.posts = []
        for _ in range(13):
            cls.posts.append(Post(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group
            ))
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_paginator(self):
        """Test paginator on first and second pages"""
        paginated_test_urls = {
            'posts:index': None,
            'posts:group_list': {'slug': 'test-slug'},
            'posts:profile': {'username': PaginatorViewsTest.user.username}
        }
        for name, kwargs in paginated_test_urls.items():
            respone_page_obj_1 = self.author_client.get(
                reverse(name, kwargs=kwargs), {'page': 1}
            ).context['page_obj']
            respone_page_obj_2 = self.author_client.get(
                reverse(name, kwargs=kwargs), {'page': 2}
            ).context['page_obj']

            count_objs_page_1 = abs(respone_page_obj_1.start_index()
                                    - respone_page_obj_1.end_index() - 1)
            count_objs_page_2 = abs(respone_page_obj_2.start_index()
                                    - respone_page_obj_2.end_index() - 1)

            self.assertEqual(count_objs_page_1, 10)
            self.assertEqual(count_objs_page_2, 3)


class TestsFollow(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.author = User.objects.create_user(username='auth_2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_user_following(self):
        follow_count = Follow.objects.count()
        self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': self.author.username}
        ))
        follow_after = Follow.objects.count()
        self.assertEqual(follow_after, follow_count + 1)
        self.assertTrue(Follow.objects.filter(user=self.user,
                                              author=self.author).exists())

    def test_user_unfollowing(self):
        Follow.objects.create(user=self.user, author=self.author)
        follow_count_before = Follow.objects.count()
        self.authorized_client.get(reverse(
            'posts:profile_unfollow', kwargs={'username': self.author.username}
        ))
        follow_after = Follow.objects.count()
        self.assertEqual(follow_after, follow_count_before - 1)
        self.assertFalse(Follow.objects.filter(user=self.user,
                                               author=self.author).exists())

    def test_unfollowing_paginator(self):
        Post.objects.create(author=self.author,
                            text='текст')
        response = self.authorized_client.get(reverse('posts:follow_index'))
        page_obj = response.context['page_obj'].object_list
        self.assertEqual(len(page_obj), 0)

    def test_following_paginator(self):
        Post.objects.create(author=self.author,
                            text='текст')
        self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': self.author.username}
        ))
        response = self.authorized_client.get(reverse('posts:follow_index'))
        page_obj = response.context['page_obj'].object_list
        self.assertEqual(len(page_obj), 1)

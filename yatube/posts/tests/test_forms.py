import shutil
import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache

from ..models import Post, Group, Comment
from .utils import SetUpMixin


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTest(SetUpMixin, TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_post(self):
        """Valid form create post"""
        posts_count = Post.objects.count()
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user}
        ))
        self.assertTrue(Post.objects.filter(
            text=self.form_data.get('text'),
            group=Group.objects.get(id=self.group.id),
            image=response.context.get('page_obj')[0].image
        ).exists())
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """Valid form edit post"""
        posts_count = Post.objects.count()
        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=self.form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}
        ))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(Post.objects.get(
            id=self.post.id).text, self.form_data['text']
        )

    def test_comment_authorized_client(self):
        """test the possibility of commenting for authorized client"""
        cache.clear()
        comment_count = Comment.objects.count()
        response = self.author_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=self.form_data_comments,
            follow=True
        )
        self.assertTrue(Comment.objects.filter(
            text=self.form_data_comments.get('text')
        ).exists())
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}
        ))

    def test_comment_none_authorized_client(self):
        """test the possibility of commenting for non authorized client"""
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=self.form_data_comments,
            follow=True
        )
        self.assertFalse(Comment.objects.filter(
            text=self.form_data_comments.get('text')
        ).exists())
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=' + reverse(
                'posts:add_comment', kwargs={'post_id': self.post.id}
            ))

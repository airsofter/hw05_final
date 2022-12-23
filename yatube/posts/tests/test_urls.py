from django.test import TestCase
from django.core.cache import cache

from .utils import SetUpMixin


class PostsURLTests(SetUpMixin, TestCase):
    def test_urls_uses_correct_template(self):
        """URL uses correct template."""
        cache.clear()
        response_templates_dict = {
            self.author_client.get(
                f'/posts/{self.post.id}/edit/'
            ): 'posts/post_create.html',
            self.author_client.get(
                '/create/'
            ): 'posts/post_create.html',
            self.guest_client.get(
                '/'
            ): 'posts/index.html',
            self.guest_client.get(
                f'/group/{self.group.slug}/'
            ): 'posts/group_list.html',
            self.guest_client.get(
                f'/profile/{self.user.username}/'
            ): 'posts/profile.html',
            self.guest_client.get(
                f'/posts/{self.post.id}/'
            ): 'posts/post_detail.html',
            self.guest_client.get(
                'unknown_page'
            ): 'core/404.html'
        }
        for response, template in response_templates_dict.items():
            with self.subTest(response=response):
                self.assertTemplateUsed(response, template)

    def test_exist_at_desired_location(self):
        """Test exist at desired location"""
        for url, response_code in self.templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, response_code)

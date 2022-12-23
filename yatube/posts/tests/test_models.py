from django.test import TestCase

from .utils import SetUpMixin


class PostModelTest(SetUpMixin, TestCase):
    def test_model_have_correct_object_names(self):
        """Test model have correct object names"""
        expected_object_list = {
            self.group.title: self.group,
            self.post.text: self.post
        }
        for received, expect in expected_object_list.items():
            with self.subTest(received=received):
                self.assertEqual(received, str(expect))

    def test_verbose_name_post(self):
        """verbose_name in the fields matches the expected."""
        post = PostModelTest.post
        for value, expected in self.field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_help_text_post(self):
        """help_text in the fields matches the expected."""
        post = PostModelTest.post
        for value, expected in self.field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )

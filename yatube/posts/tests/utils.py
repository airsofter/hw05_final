from http import HTTPStatus

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django import forms

from ..models import User, Post, Group
from ..forms import PostForm


# некотрые данные пришлось вынести отсюда из за
# специфики работы setUpClass и его наследования
class SetUpMixin:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded_for_context = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded_for_context
        )
        cls.form = PostForm()

        # test_forms
        cls.field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата создания',
            'author': 'Автор',
            'group': 'Группа'
        }

        # test_models
        cls.field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост'
        }

        # test_urls
        cls.templates_url_names = {
            '/': HTTPStatus.OK,
            f'/group/{cls.group.slug}/': HTTPStatus.OK,
            f'/profile/{cls.user.username}/': HTTPStatus.OK,
            f'/posts/{cls.post.id}/': HTTPStatus.OK,
            f'/posts/{cls.post.id}/edit/': HTTPStatus.FOUND,
            '/create/': HTTPStatus.FOUND,
            '/unexisting_page/': HTTPStatus.NOT_FOUND
        }

        cls.form_fields = {
            'group': forms.ModelChoiceField,
            'text': forms.fields.CharField,
        }

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.post.author)

        # test_forms
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        self.form_data = {
            'text': 'Новый текст',
            'group': self.group.id,
            'image': self.uploaded
        }

        self.form_data_comments = {
            'text': 'текст коммента'
        }

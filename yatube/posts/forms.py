from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        fields = ('text', 'group', 'image')
        model = Post

    def clean_text(self):
        data = self.cleaned_data['text']
        if data is None:
            raise forms.ValidationError('Заполните поле текст')

        return data


class CommentForm(forms.ModelForm):
    class Meta:
        fields = ('text',)
        model = Comment

    def clean_text(self):
        data = self.cleaned_data['text']
        if data is None:
            raise forms.ValidationError('Заполните поле текст')

        return data

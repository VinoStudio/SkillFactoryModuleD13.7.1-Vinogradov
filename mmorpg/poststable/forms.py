from django.forms import ModelForm
from .models import Post, Response, Author
from django import forms
from allauth.account.forms import SignupForm, LoginForm
from django.contrib.auth.models import Group
from ckeditor.widgets import CKEditorWidget


class CreateForm(ModelForm):
    class Meta:
        model = Post
        fields = ['postCategory', 'title', 'description', 'preview_image', 'text']
        labels = {
            'postCategory': 'Выберете категорию',
            'title': 'Заголовок поста',
            'description': 'Краткое описание',
            'preview_image': 'Изображение для превью',
        }
        widgets = {
            'postCategory': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Выберете категорию',
                'style': 'background-color: #1E1E1E; color: white;'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите заголовок поста',
                'style': 'background-color: #1E1E1E; color: white;'
            }),
            'description': forms.Textarea(attrs={
                'class': 'md-textarea form-control mb-1 shadow-none',
                'placeholder': 'Краткое описание поста',
                'rows': '2',
                'style': 'background-color: #1E1E1E; color: white;'
            }),
            'preview_image': forms.FileInput(attrs={
                'class': 'd-flex justify-content-between',
                'style': ''
            }),
            'text': forms.Textarea(attrs={
                'class': 'ckeditor',
                'style': 'background-color: #1E1E1E; color: white;'
            })
        }
class CommentForm(ModelForm):
    class Meta:
        model = Response
        fields = ('text', 'comment_image',)
        labels = {
            'text': '',
            'comment_image': '',
        }
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'md-textarea form-control mb-1 shadow-none',
                'placeholder': 'Ваш комментарий',
                'rows': '2',
                'style': 'background-color: #1E1E1E; color: white;',
                'id': 'comment_text'
            }),
            'comment_image': forms.FileInput(attrs={
                'class': 'd-flex justify-content-between',
                'style': ''
            })
        }


class MySignupForm(SignupForm):

    def __init__(self, *args, **kwargs):
        super(MySignupForm, self).__init__(*args, **kwargs)

        #labes
        self.fields['username'].label = ''
        self.fields['email'].label = ''
        self.fields['password1'].label = ''
        self.fields['password2'].label = ''

        self.fields['username'].widget.attrs['placeholder'] = 'Никнейм'
        self.fields['email'].widget.attrs['placeholder'] = 'E-mail адрес'
        self.fields['password1'].widget.attrs['placeholder'] = 'Пароль'
        self.fields['password2'].widget.attrs['placeholder'] = 'Пароль (повторно)'

        #widgets
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'type': 'text',
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'type': 'email',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'type': 'password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'type': 'password',
        })

    def save(self, request):
        user = super(MySignupForm, self).save(request)
        # common_group = Group.objects.get_or_create(name='common')[0]
        # common_group.user_set.add(user)
        Author.objects.create(userAuthor=user)
        return user


class MyLoginForm(LoginForm):

    def __init__(self, *args, **kwargs):
        super(MyLoginForm, self).__init__(*args, **kwargs)

        #labes
        self.fields['remember'].label = 'Запомнить меня'
        self.fields['password'].label = ''
        self.fields['login'].label = ''

        self.fields['login'].widget.attrs['placeholder'] = 'E-mail адрес'
        self.fields['password'].widget.attrs['placeholder'] = 'Пароль'

        #widgets
        self.fields['login'].widget.attrs.update({
            'class': 'form-control',
            'type': 'email',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'type': 'password',
        })


class SearchForm(ModelForm):

    class Meta:
        model = Post
        fields = ['title']
        labels = {
            'title': ''
        }
        widgets = {
            'title': forms.Textarea(attrs={
                'class': 'row-12 rounded-pill shadow-none',
                'placeholder': 'Введите поисковой запрос',
                'style': 'background-color: #1E1E1E; color: white;',
                'id': 'search_menu'
            })
        }

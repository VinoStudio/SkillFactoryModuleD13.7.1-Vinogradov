import django_filters
from django_filters import FilterSet
from .models import Post, Author
from django.forms import ModelForm
from django import forms
from .forms import SearchForm
from django.forms.widgets import Input


class PostFilter(FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Post
        fields = ['title']

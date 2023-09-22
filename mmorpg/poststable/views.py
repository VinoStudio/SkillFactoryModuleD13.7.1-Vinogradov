import http

from django.http import HttpResponseForbidden
from django.shortcuts import render
from datetime import timedelta
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from .models import Post, Category, Author, Response
from django.contrib.auth.models import User
from django.views import View
from django.utils import timezone
from django.core.paginator import Paginator
from .forms import CreateForm, CommentForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth.models import Group
from decouple import config
from hitcount.views import HitCountDetailView
from django.conf import settings
from .filters import PostFilter


class PostView(ListView):
    model = Post
    template_name = 'base/default.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-id')
    ordering = ['-postDate']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # category = Category.objects.get(name=self.kwargs['name'])
        post_count = Response.objects.all().filter()
        context['subscriber'] = Category.objects.filter(subscribers=self.request.user.id).exists()
        context['liked'] = Post.objects.filter(likedUser=self.request.user.id).exists()
        context['comments'] = Response.objects.order_by('-commentDate')
        context['filter'] = PostFilter(self.request.GET)
        # context['category_name'] = category
        return context


    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     return


class SearchView(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'searched'
    queryset = Post.objects.order_by('-id')
    ordering = ['-postDate']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscriber'] = Category.objects.filter(subscribers=self.request.user.id).exists()
        context['liked'] = Post.objects.filter(likedUser=self.request.user.id).exists()
        context['comments'] = Response.objects.order_by('-commentDate')
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context

class CreatePost(CreateView):
    model = Post
    template_name = 'create.html'
    form_class = CreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Response.objects.order_by('-commentDate')
        context['form'] = self.form_class
        context['filter'] = PostFilter(self.request.GET)

        return context

    def post(self, request, *args, **kwargs):
        user = request.user

        if not Author.objects.filter(userAuthor_id=user.id).exists():
            Author.objects.create(userAuthor=user)

        form = self.form_class(request.POST, request.FILES)
        if form.is_valid:
            form.instance.author = Author.objects.get(userAuthor=self.request.user.id)

            form.save()

            return redirect('table:author_post')
        else:
            return redirect('table:popular')


class UpdatePost(UpdateView):
    template_name = 'create.html'
    form_class = CreateForm
    success_url = reverse_lazy('table:author_post')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Response.objects.order_by('-commentDate')
        context['filter'] = PostFilter(self.request.GET)

        return context

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class DeletePost(DeleteView):
    context_object_name = 'delete_post'
    template_name = 'delete_post.html'
    queryset = Post.objects.all()
    success_url = reverse_lazy('table:posts')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Response.objects.order_by('-commentDate')
        context['form'] = self.form_class
        context['filter'] = PostFilter(self.request.GET)

        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author.userAuthor == self.request.user:
            success_url = self.get_success_url()
            obj.delete()
            return HttpResponseRedirect(success_url)
        else:
            return HttpResponseForbidden("Нельзя удалить этот отклик")


class ResponsesList(ListView):
    model = Response
    template_name = 'responses.html'
    context_object_name = 'responses'
    queryset = Response.objects.order_by('-id')
    ordering = ['-commentDate']
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscriber'] = Category.objects.filter(subscribers=self.request.user.id).exists()
        context['comments'] = Response.objects.order_by('-commentDate')
        context['author_comments'] = Response.objects.filter(author=self.request.user.id)
        context['post_comments'] = Response.objects.filter(post_id__author=self.request.user.id).exclude(author=self.request.user.id)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context

class PopularList(ListView):
    model = Post
    template_name = 'popular.html'
    context_object_name = 'popular'
    queryset = Post.objects.order_by('-id')
    ordering = ['-postRating']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscriber'] = Category.objects.filter(subscribers=self.request.user.id).exists()
        context['liked'] = Post.objects.filter(likedUser=self.request.user.id).exists()
        context['comments'] = Response.objects.order_by('-commentDate')
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context


class CategoryList(ListView):
    model = Post
    template_name = 'category_view.html'
    context_object_name = 'categories'
    queryset = Post.objects.order_by('-id')
    ordering = ['-postDate']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.all().filter(postCategory__name=self.kwargs['name'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.get(name=self.kwargs['name'])
        context['subscriber'] = Category.objects.filter(subscribers=self.request.user.id).exists()
        context['comments'] = Response.objects.order_by('-commentDate')
        context['liked'] = Post.objects.filter(likedUser=self.request.user.id).exists()
        context['category_name'] = category
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context


class PostDetail(HitCountDetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'
    # slug_field = 'slug'
    count_hit = True

    form = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscriber'] = Category.objects.filter(subscribers=self.request.user.id).exists()
        context['liked'] = Post.objects.filter(likedUser=self.request.user.id).exists()
        context['comments'] = Response.objects.order_by('-commentDate')
        context['form'] = self.form
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context

    def post(self, request, *args, **kwargs):
        user = request.user

        if not Author.objects.filter(userAuthor_id=user.id).exists():
            Author.objects.create(userAuthor=user)

        form = self.form(request.POST, request.FILES)
        if form.is_valid():
            post = self.get_object()
            form.instance.author = Author.objects.get(userAuthor=request.user.id)
            form.instance.post_id = post
            form.save()

            post.comments.add(form.instance)

            return redirect(request.META.get('HTTP_REFERER', 'table:posts'))
        else:
           return redirect('table:popular')

    def get_object(self, *args, **kwargs):
        post = cache.get(f'post-{self.kwargs["pk"]}', None)

        if not post:
            post = obj = super().get_object(queryset=self.queryset)
            cache.set(f'post-{self.kwargs["pk"]}', obj)
        return post








# Function Views

def delete_response(request, pk):
    user = request.user
    comment = Response.objects.get(id=pk)
    if comment.author.userAuthor == user:
        comment.delete()

    return redirect(request.META.get('HTTP_REFERER', 'table:posts'))


def approve_comment(request, pk):
    comment = Response.objects.get(id=pk)
    if not comment.approved:
        comment.approve

        email = comment.author.userAuthor.email
        html = render_to_string(
            template_name='mail/approve_mail.html',
            context={
                'comment': comment
            }
        )

        message = EmailMultiAlternatives(
            subject='Автору поста понравился ваш комметарий!',
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email, ],
        )

        message.attach_alternative(html, 'text/html')

        try:
            message.send()
        except Exception as e:
            print(e)

        return redirect(request.META.get('HTTP_REFERER', 'table:posts'))
    else:
        return redirect('table:posts')


def comment_like(request, pk):
    user = request.user
    comment = Response.objects.get(id=pk)
    author = Author.objects.get(userAuthor_id=comment.author.userAuthor_id)
    if user.is_authenticated:
        if not comment.likedUser.filter(id=user.id).exists():
            comment.likedUser.add(user)
            comment.like

            author.update_rating()
        return redirect(request.META.get('HTTP_REFERER', 'table:posts'))
    else:
        return redirect('account_login')


# def comment_dislike(request, pk):
#     user = request.user
#     comment = Response.objects.get(id=pk)
#     author = Author.objects.get(userAuthor=comment.author.userAuthor_id)
#     if user.is_authenticated:
#         if comment.likedUser.filter(id=user.id).exists():
#             comment.likedUser.remove(user)
#             comment.dislike
#
#             author.update_rating()
#         return redirect(request.META.get('HTTP_REFERER', 'table:posts'))
#     else:
#         return redirect('account_login')



def like(request, pk):
    user = request.user
    post = Post.objects.get(id=pk)
    author = Author.objects.get(userAuthor=post.author.userAuthor_id)
    if user.is_authenticated:
        if not post.likedUser.filter(id=user.id).exists():
            post.likedUser.add(user)
            post.like

            author.update_rating()
        return redirect(request.META.get('HTTP_REFERER', 'table:posts'))
    else:
        return redirect('account_login')


def dislike(request, pk):
    user = request.user
    post = Post.objects.get(id=pk)
    author = Author.objects.get(userAuthor=post.author.userAuthor_id)
    if user.is_authenticated:
        if post.likedUser.filter(id=user.id).exists():
            post.likedUser.remove(user)
            post.dislike

            author.update_rating()
        return redirect(request.META.get('HTTP_REFERER', 'table:posts'))
    else:
        return redirect('account_login')


def user_comments(request):
    user_comments = Response.objects.filter(author=request.user.id).order_by('-commentDate')
    comments = Response.objects.order_by('-commentDate')
    filter = PostFilter(request.GET)
    context = {
        'user_comments': user_comments,
        'comments': comments,
        'filter': filter
    }
    return render(request, 'my_comments.html', context)


def post_comments(request):
    post_comments = Response.objects.filter(post_id__author=request.user.id).exclude(author=request.user.id).order_by('-commentDate')
    comments = Response.objects.order_by('-commentDate')
    filter = PostFilter(request.GET)
    context = {
        'post_comments': post_comments,
        'comments': comments,
        'filter': filter
    }
    return render(request, 'my_responses.html', context)


def author_posts(request):
    author_post = Post.objects.filter(author__userAuthor=request.user.id).order_by('-postDate')
    comments = Response.objects.order_by('-commentDate')
    filter = PostFilter(request.GET)
    context = {
        'author_post': author_post,
        'comments': comments,
        'filter': filter
    }
    return render(request, 'author_posts.html', context)


def user_subs(request):
    user_posts = Post.objects.filter(postCategory__subscribers=request.user.id ).order_by('-postDate')
    comments = Response.objects.order_by('-commentDate')
    liked = Post.objects.filter(likedUser=request.user.id).exists()
    subscriber = Category.objects.filter(subscribers=request.user.id).exists()
    filter = PostFilter(request.GET)
    context = {
        'user_subs': user_posts,
        'comments': comments,
        'liked': liked,
        'subscriber': subscriber,
        'filter': filter,
    }
    return render(request, 'user_subs.html', context)


def subscribe(request, name):
    category = Category.objects.get(name=name)
    user = request.user

    if not category.subscribers.filter(id=user.id).exists():
        category.subscribers.add(user)
        email = user.email
        html = render_to_string(
            template_name='mail/subscribtion.html',
            context={
                'category': category,
                'user': user,
            }
        )
        message = EmailMultiAlternatives(
            subject='Уведомление о подписке',
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email, ],
        )

        message.attach_alternative(html, 'text/html')
        try:
            message.send()
        except Exception as e:
            print(e)

    return redirect(request.META.get('HTTP_REFERER', 'table:posts'))


def unsubscribe(request, name):
    category = Category.objects.get(name=name)
    user = request.user
    if category.subscribers.filter(id=user.id).exists():
        category.subscribers.remove(user)
        email = user.email
        html = render_to_string(
            template_name='mail/unsubscribtion.html',
            context={
                'category': category,
                'user': user,
            }
        )
        message = EmailMultiAlternatives(
            subject='Уведомление об отписке',
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email, ],
        )

        message.attach_alternative(html, 'text/html')
        try:
            message.send()
        except Exception as e:
            print(e)
    return redirect(request.META.get('HTTP_REFERER', 'table:posts'))

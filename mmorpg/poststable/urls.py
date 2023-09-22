from django.urls import path
from .views import (PostView, PopularList, subscribe, unsubscribe, CategoryList, PostDetail,
                    like, dislike, ResponsesList, user_comments, post_comments, author_posts, user_subs, CreatePost,
                    approve_comment, UpdatePost, DeletePost, SearchView, delete_response, comment_like,)

app_name = 'table'

urlpatterns = [
    path('', PostView.as_view(), name='posts'),
    path('<int:pk>', PostDetail.as_view(), name='post'),
    path('popular/', PopularList.as_view(), name='popular'),
    path('subscription/', user_subs, name='subscription'),
    path('create/', CreatePost.as_view(), name='create'),
    path('search/', SearchView.as_view(), name='search'),
    path('<int:pk>/edit', UpdatePost.as_view(), name='update'),
    path('<int:pk>/delete', DeletePost.as_view(), name='delete'),
    path('responses/', post_comments, name='responses'),
    path('comments/', user_comments, name='user_comments'),
    path('my_posts/', author_posts, name='author_post'),
    path('subscribe/<str:name>', subscribe, name='subscribe'),
    path('unsubscribe/<str:name>', unsubscribe, name='unsubscribe'),
    path('categories/<str:name>', CategoryList.as_view(), name='categories'),
    path('like/<int:pk>', like, name='like'),
    path('dislike/<int:pk>', dislike, name='dislike'),
    path('comment_like/<int:pk>', comment_like, name='comment_like'),
    path('approve/<int:pk>', approve_comment, name='approve'),
    path('delete/<int:pk>', delete_response, name='delete_response'),
]
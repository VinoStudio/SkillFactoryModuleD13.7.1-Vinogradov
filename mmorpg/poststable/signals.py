from django.core.mail import mail_managers, EmailMultiAlternatives
from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.shortcuts import redirect
from .models import Post, Category, Author, Response
from django.conf import settings


def get_subscribers(category):
    user_email = []
    for user in category.subscribers.all():
        user_email.append(user.email)
    return user_email


@receiver(post_save, sender=Post)
def notify_subscriber(sender, instance, created, **kwargs):
    if created:

        subscribers = get_subscribers(instance.postCategory)
        author_email = instance.author.userAuthor.email
        if author_email in subscribers:
            subscribers.remove(author_email)


        html = render_to_string(
            template_name='mail/new_post.html',
            context={
                'category': instance.postCategory,
                'author': instance.author.userAuthor.username,
                'title': instance.title,
                'url': instance.id,
            }
        )
        message = EmailMultiAlternatives(
            subject=f'Новое объявление в категории {instance.postCategory.name}',
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=subscribers
        )
        message.attach_alternative(html, 'text/html')
        message.send()


@receiver(post_save, sender=Response)
def notify_author(sender, instance, created, **kwargs):
    if created:
        author_email = instance.post_id.author.userAuthor.email

        html = render_to_string(
            template_name='mail/new_comment.html',
            context={
                'author': instance.author.userAuthor.username,
                'post_title': instance.post_id.title,
                'text': instance.text,
                'url': instance.post_id.id,
            }
        )
        message = EmailMultiAlternatives(
            subject=f'Новый комментарий к посту {instance.post_id.title}',
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[author_email, ]
        )
        message.attach_alternative(html, 'text/html')
        message.send()
from autoslug import AutoSlugField
from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from hitcount.models import HitCountMixin, HitCount
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericRelation
from django.core.cache import cache

class Author(models.Model):
    userAuthor = models.OneToOneField(User, on_delete=models.CASCADE)
    userRating = models.SmallIntegerField(default=0)

    def update_rating(self):
        posts = self.post_set.all()
        comments = self.response_set.all()
        postRating = 0
        commentRating = 0

        if posts.exists():
            postValue = posts.aggregate(summ = Sum('postRating'))
            postRating += postValue.get('summ')

        if comments.exists():
            commentValue = comments.aggregate(summ=Sum('responseRating'))
            commentRating += commentValue.get('summ')

        self.userRating = postRating * 3 + commentRating
        self.save()

    def __str__(self):
        return f'User: {self.userAuthor}, {self.pk}'


class Category(models.Model):
    TANKS = 'Tanks'
    HEALERS = 'Healers'
    DD = 'DamageDealers'
    MERCHANTS = 'Merchants'
    GUILD_MASTERS = 'GuildMasters'
    QUEST_GIVERS = 'QuestGivers'
    BLACKSMITHS = 'BlackSmiths'
    TANNERS = 'Tanners'
    POTION_MAKERS = 'PotionMakers'
    SPELL_MASTERS = 'SpellMasters'
    CATEGORY_NAME_CHOICES = [
        (TANKS, 'Танки'),
        (HEALERS, 'Хилы'),
        (DD, 'ДД'),
        (MERCHANTS, 'Торговцы'),
        (GUILD_MASTERS, 'Гилдмастеры'),
        (QUEST_GIVERS, 'Квестгиверы'),
        (BLACKSMITHS, 'Кузнецы'),
        (TANNERS, 'Кожевники'),
        (POTION_MAKERS, 'Зельевары'),
        (SPELL_MASTERS, 'Мастера заклинаний'),
    ]
    name = models.CharField(max_length=15, choices=CATEGORY_NAME_CHOICES)
    subscribers = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return f'Категория: {self.name}'


class Response(models.Model):
    post_id = models.ForeignKey('Post', null=True, default=None, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    commentDate = models.DateTimeField(auto_now_add=True)
    comment_image = models.ImageField(upload_to='comment_images/%Y/%m/%d', null=True, default=None, blank=True)  #important!!
    approved = models.BooleanField(null=True, default=False)
    likedUser = models.ManyToManyField(User, blank=True)
    responseRating = models.SmallIntegerField(default=0, blank=True)


    @property
    def approve(self):
        self.approved = True
        self.save()

    def __str__(self):
        return f"{self.author.userAuthor.username}"

    @property
    def like(self):
        self.responseRating += 1
        self.save()
    @property
    def dislike(self):
        self.responseRating -= 1
        self.save()

    def get_absolute_url(self):
        return f'{self.id}'



class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    postDate = models.DateTimeField(auto_now_add=True)
    postUpdate = models.DateTimeField(auto_now=True)
    postCategory = models.ForeignKey(Category, blank=False, on_delete=models.CASCADE)
    title = models.CharField(blank=False, max_length=128)
    description = models.CharField(blank=True, max_length=300)
    preview_image = models.ImageField(upload_to='post_preview/%Y/%m/%d')
    text = RichTextUploadingField()
    postRating = models.SmallIntegerField(default=0)
    comments = models.ManyToManyField(Response, blank=True)
    likedUser = models.ManyToManyField(User, blank=True)
    slug = AutoSlugField(populate_from='title', default=None, null=True)
    hit_count_generic = GenericRelation(HitCount, object_id_field='object_p',
                                        related_query_name='hit_count_generic_relation')

    @property
    def like(self):
        self.postRating += 1
        self.save()
    @property
    def dislike(self):
        self.postRating -= 1
        self.save()

    def get_absolute_url(self):
        return f'/{self.id}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'post-{self.pk}')

    def __str__(self):
        return f"{self.author.userAuthor}, {self.title}"





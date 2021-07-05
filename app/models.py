from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.db.models import Prefetch


class AuthorManager(models.Manager):
    def get_top(self, number):
        return self.all().annotate(number_answers=models.Count('answer_author'))\
                .order_by('-number_answers').prefetch_related(
             Prefetch('profile', queryset=User.objects.all().only('pk', 'first_name')))[0:number]

    def contain(self, pk):
        return self.filter(pk=pk).exists()


class Author(models.Model):
    image = models.ImageField('Аватарка', upload_to='users/')
    profile = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='пользователь', related_name='author_users')

    objects = AuthorManager()

    def __str__(self):
        return self.profile.first_name

    def get_url(self):
        return

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'


class TagManager(models.Manager):
    def get_top(self, number):
        return self.annotate(number_question=models.Count('question_tags'))\
                    .order_by('-number_question')[0:number]

    def contain(self, name):
        return self.filter(name=name).exists()


class Tag(models.Model):
    name = models.CharField('Имя', max_length=255)

    objects = TagManager()

    def __str__(self):
        return self.name

    @classmethod
    def get_or_create(cls, value):
        if cls.objects.filter(name=value).exists():
            return cls.objects.get(name=value)
        else:
            return cls.objects.create(name=value)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class QuestionManager(models.Manager):
    def get_top(self, number):
        return self.base_list_question().order_by('-rating').exclude(rating=None)[0:number].prefetch_related()

    def get_by_tag(self, tag):
        return self.base_list_question().filter(tags__name__exact=tag).prefetch_related()

    def get_by_id(self, pk):
        return self.filter(pk=pk).prefetch_related(
            Prefetch('author', queryset=Author.objects.all().prefetch_related(
                Prefetch('profile', queryset=User.objects.all().only('first_name'))
                ).only('image', 'profile__username')),

            Prefetch('tags', queryset=Tag.objects.all().only('name'))
        ).only('author_id', 'tags', 'author__profile__first_name', 'text', 'title', 'pk', 'author__image', 'author', 'rating')

    def base_list_question(self):
        return self.annotate(num_answer=models.Count('answer_question', distinct=True))\
            .prefetch_related(
            Prefetch('author', queryset=Author.objects.all().only('image', 'pk')),
            Prefetch('tags', queryset=Tag.objects.all())
        ).only('author_id', 'tags', 'text', 'title', 'pk', 'author__image', 'rating')

    def contain(self, pk):
        return self.filter(pk=pk).exists()

    def get_list_by_id_author(self, author):
        return self.base_list_question().filter(author__id__exact=author).prefetch_related()


class Question(models.Model):
    title = models.CharField('Заголовок', max_length=500)
    text = models.TextField('Текст')
    date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='автор', related_name='question_author')
    tags = models.ManyToManyField(Tag, verbose_name='тэги', related_name='question_tags')

    rating = models.IntegerField('Рейтинг', default=0)

    objects = QuestionManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['date']


class QuestionLike(models.Model):
    number = models.IntegerField('Число', choices=(('like', 1), ('dislike', -1)))
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='автор', related_name='question_like_author')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='вопрос',
                                 related_name='question_likes')

    def __str__(self):
        return str(self.number)

    class Meta:
        verbose_name = 'ЛайкНаВопрос'
        verbose_name_plural = 'ЛайкиВопросов'
        unique_together = ('author', 'question')


class AnswerManager(models.Manager):
    def base_list_answer(self, question_id):
        return self.filter(question_id=question_id).prefetch_related(
            Prefetch('author', queryset=Author.objects.all().prefetch_related(
                Prefetch('profile', queryset=User.objects.all().only('username'))).only('pk', 'image', 'profile__username'))
        ).only('author_id', 'author__profile__username', 'text', 'pk', 'author__image', 'date', 'rating')


class Answer(models.Model):
    is_right = models.BooleanField('Верный ли ответ', default=False)
    text = models.TextField('Текст')
    date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='автор', related_name='answer_author')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='вопрос', related_name='answer_question')

    rating = models.IntegerField('Рейтинг', default=0)

    objects = AnswerManager()

    def __str__(self):
        return self.author.profile.username

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering = ['date']


class AnswerLike(models.Model):
    number = models.IntegerField('Число', choices=(('like', 1), ('not_active', 0), ('dislike', -1)))
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='автор', related_name='answer_like_author')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, verbose_name='отвт', related_name='answer_likes')

    def __str__(self):
        return str(self.number)

    class Meta:
        verbose_name = 'ЛайкНаОтвет'
        verbose_name_plural = 'ЛайкиОтветов'

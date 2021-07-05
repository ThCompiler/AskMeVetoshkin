import json

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from numpy import unicode

from app.models import Author, Question, Tag, AnswerLike, Answer, QuestionLike, User
from app.forms import LoginForm, RegisterForm, AskForm, AnswerForm, SettingsFormUser, SettingsFormAuthor
from django.contrib import auth

from django.shortcuts import render
import random

tags = [
    'C++',
    'Python',
    'Кольца',
    'Магазин',
    'Король',
    'Кошка',
    'Нога',
    'Хабр'
]

authors = [
    'Док',
    'Дон',
    'Марк',
    'Рун',
    'Шон',
    'Доc',
    'Рон'
]


def generate_tag():
    tmp = []
    for idx2 in range(random.randint(0, 3)):
        current = random.choice(tags)
        if current not in tmp:
            tmp.append(current)
            idx2 -= 1

    ans = {'list': tmp, 'last': ""}
    ans['last'] = ans['list'][-1] if len(ans['list']) != 0 else ""
    return ans


questions = [
    {
        'id': idx,
        'title': f'Title number {idx}',
        'text': f'Some text for question #{idx}',
        'tags': generate_tag(),
        'author': random.choice(authors),
        'answers': [
            {
                'author': random.choice(authors),
                'text': f'{idx2} answer for question #{idx}'
            } for idx2 in range(random.randint(0, 20))
        ]
    } for idx in range(10)
]


def convert_question(date):
    questions = []
    for question in date:
        questions.append(
            {
                'id': question.pk,
                'title': question.title,
                'text': question.text,
                'tags': {
                    'list': question.tags,
                    'last': question.tags.all()[len(question.tags.all()) - 1]
                },
                'author': question.author,
                'answers': [
                    {
                        'author': random.choice(authors),
                        'text': f'{idx2} answer for question'
                    } for idx2 in range(random.randint(0, 20))]
            }
        )
    return questions


def paginate(obj_list, page_number, per_page=10):
    paginator = Paginator(obj_list, per_page)
    return paginator.get_page(page_number)


def index(request):
    # print(Question.objects.base_list_question().all()[1].reting)
    return render(request, 'index.html',
                  {'page_obj': paginate(Question.objects.base_list_question().all(), request.GET.get('page')),
                   'tags': Tag.objects.get_top(10).all(), 'authors': Author.objects.get_top(12).all()})


def tag_questions(request, current_tag):
    if not Tag.objects.contain(current_tag):
        return render(request, 'error_page.html',
                      {'tags': Tag.objects.get_top(10).all(), 'authors': Author.objects.get_top(12).all()})

    return render(request, 'tag.html',
                  {'page_obj': paginate(Question.objects.get_by_tag(current_tag), request.GET.get('page')),
                   'tags': Tag.objects.get_top(10).all(), 'authors': Author.objects.get_top(12).all(),
                   'current_tag': current_tag})


def author_questions(request, current_author):
    if not Author.objects.contain(current_author):
        return render(request, 'error_page.html',
                      {'tags': Tag.objects.get_top(10).all(), 'authors': Author.objects.get_top(12).all()})

    return render(request, 'author-question.html', {
        'page_obj': paginate(Question.objects.get_list_by_id_author(current_author), request.GET.get('page')),
        'tags': Tag.objects.get_top(10).all(), 'authors': Author.objects.get_top(12).all(),
        'current_author': Author.objects.get(id=current_author)})


def hot_questions(request):
    return render(request, 'hot-question.html',
                  {'page_obj': paginate(Question.objects.get_top(300).all(), request.GET.get('page')),
                   'authors': Author.objects.get_top(12).all(), 'tags': Tag.objects.get_top(10).all()})


def tag_autocomplete(request):
    """ url: /tag_autocomplete/"""

    value = request.GET['term']

    available_tags = Tag.objects.filter(name__startswith=value)

    response = HttpResponse(json.dumps([unicode(tag) for tag in available_tags]), content_type="application/json")
    return response


@login_required
def new_questions(request):
    form = AskForm()
    if request.method == 'POST':
        form = AskForm(request.POST)

        if form.is_valid():
            date = form.cleaned_data
            if date is not None:
                question = Question(title=date['title'], text=date['text'],
                                    author_id=auth.get_user(request).author_users.id)
                question.save()
                for tag in date['tags']:
                    c_tag = Tag.get_or_create(tag)
                    question.tags.add(c_tag)
                question.save()
                return redirect(reverse('current_question', args=[question.id]))
    return render(request, 'ask.html',
                  {'form': form, 'tags': Tag.objects.get_top(10).all(), 'authors': Author.objects.get_top(12).all()})


def log_in(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(request, **form.cleaned_data)
            if user is not None:
                auth.login(request, user)
                return redirect(request.GET.get('next', '/'))
    return render(request, 'login.html',
                  { 'form': form, 'tags': Tag.objects.get_top(10).all(), 'authors': Author.objects.get_top(12).all()})


def sign_up(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            date = form.cleaned_data
            path = request.FILES.get('image')

            if date is not None and path is not None:
                us = User(first_name=date['username'], username=date['login'],
                          email=date['email'], password=date['password'])
                us.save()
                auth.login(request, us)
                a = Author(image=path, profile=us)
                a.save()
                return redirect(reverse('root'))
    return render(request, 'signup.html',
                  {'form': form, 'tags': Tag.objects.get_top(10).all(), 'authors': Author.objects.get_top(12).all()})


def current_question(request, pk):
    if not Question.objects.contain(pk):
        return render(request, 'error_page.html',
                      {'tags': Tag.objects.get_top(10).all(), 'authors': Author.objects.get_top(12).all()})
    form = AnswerForm()
    object = Question.objects.base_list_question().get(pk=pk)
    if request.method == 'POST':
        form = AnswerForm(request.POST)

        if form.is_valid():
            date = form.cleaned_data
            if date is not None:
                answer = Answer(text=date['text'], question_id=pk, author_id=auth.get_user(request).author_users.id)
                answer.save()

                return redirect(reverse('current_question', args=[pk]) + '?page=' + str(paginate(Answer.objects.base_list_answer(pk).all(),
                                                                              request.GET.get('page'), 5).end_index()))

    return render(request, 'question.html', {'form': form,
                                             'object': object,
                                             'page_obj': paginate(Answer.objects.base_list_answer(pk).all(),
                                                                  request.GET.get('page'), 5),
                                             'tags': Tag.objects.get_top(10).all(),
                                             'authors': Author.objects.get_top(12).all()})


@login_required
def settings(request):
    user = auth.get_user(request)
    form_user = SettingsFormUser(instance=user)
    form_author = SettingsFormAuthor(instance=user.author_users)

    if request.method == 'POST':
        form_user = SettingsFormUser(request.POST, request.FILES, instance=user)
        form_author = SettingsFormAuthor(request.POST, request.FILES, instance=user.author_users)
        if form_author.is_valid() and form_author.is_valid():
            form_author.save()
            form_user.save()
    return render(request, 'settings.html',
                  {'form_user': form_user, 'form_author' : form_author,
                   'tags': Tag.objects.get_top(10).all(), 'authors': Author.objects.get_top(12).all()})


def log_out(request):
    auth.logout(request)
    return redirect(request.GET.get('next', '/'))
# Create your views here.

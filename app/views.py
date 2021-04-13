from django.core.paginator import Paginator
from django.shortcuts import render

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
            } for idx2 in range(random.randint(0, 3))
        ]
    } for idx in range(10)
]


def paginate(obj_list, page_number, per_page=5):
    paginator = Paginator(obj_list, per_page)
    return paginator.get_page(page_number)


def index(request):
    return render(request, 'index.html', {'page_obj': paginate(questions, request.GET.get('page')), 'tags': tags, 'authors': authors})


def tag_questions(request, current_tag):
    select = []
    for question in questions:
        if current_tag in question['tags']['list']:
            select.append(question)
    return render(request, 'tag.html', {'page_obj': paginate(select, request.GET.get('page')), 'tags': tags, 'authors': authors, 'current_tag': current_tag})


def author_questions(request, current_author):
    select = []
    for question in questions:
        if current_author == question['author']:
            select.append(question)
    return render(request, 'author-question.html', {'page_obj': paginate(select, request.GET.get('page')), 'tags': tags, 'authors': authors, 'current_author': current_author})


def hot_questions(request):
    return render(request, 'hot-question.html', {'page_obj': paginate(questions, request.GET.get('page')), 'authors': authors, 'tags': tags})


def new_questions(request):
    return render(request, 'ask.html', {'tags': tags, 'authors': authors})


def log_in(request):
    return render(request, 'login.html', {'tags': tags, 'authors': authors})


def sign_up(request):
    return render(request, 'signup.html', {'tags': tags, 'authors': authors})


def current_question(request, pk):
    return render(request, 'question.html', {'question': questions[pk], 'tags': tags, 'authors': authors})


def settings(request):
    return render(request, 'settings.html', {'tags': tags, 'authors': authors})

# Create your views here.

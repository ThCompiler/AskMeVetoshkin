from django.core.paginator import Paginator
from django.shortcuts import render
from app.models import Author, Question, Tag, AnswerLike, Answer, QuestionLike

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
                    'last': question.tags.all()[len(question.tags.all())-1]
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
    #print(Question.objects.base_list_question().all()[1].reting)
    return render(request, 'index.html', {'page_obj': paginate(Question.objects.base_list_question().all(), request.GET.get('page')),
                                          'tags': Tag.objects.get_top(10).all(), 'authors': Author.objects.get_top(12).all()})


def tag_questions(request, current_tag):
    if not Tag.objects.contain(current_tag):
        return render(request, 'error_page.html', {'tags': Tag.objects.get_top(10).all(), 'authors': Author.objects.get_top(12).all()})

    return render(request, 'tag.html', {'page_obj': paginate(Question.objects.get_by_tag(current_tag), request.GET.get('page')),
                                        'tags': Tag.objects.get_top(10).all(), 'authors': Author.objects.get_top(12).all(), 'current_tag': current_tag})


def author_questions(request, current_author):
    if not Author.objects.contain(current_author):
        return render(request, 'error_page.html', {'tags': Tag.objects.get_top(10).all(), 'authors': Author.objects.get_top(12).all()})

    return render(request, 'author-question.html', {'page_obj': paginate(Question.objects.get_list_by_id_author(current_author), request.GET.get('page')),
                    'tags': Tag.objects.get_top(10).all(), 'authors': Author.objects.get_top(12).all(),
                                                    'current_author': Author.objects.get(id=current_author)})


def hot_questions(request):
    return render(request, 'hot-question.html', {'page_obj': paginate(Question.objects.get_top(300).all(), request.GET.get('page')),
                                                 'authors':  Author.objects.get_top(12).all(), 'tags': Tag.objects.get_top(10).all()})


def new_questions(request):
    return render(request, 'ask.html', {'tags': Tag.objects.get_top(10).all(), 'authors':  Author.objects.get_top(12).all()})


def log_in(request):
    return render(request, 'login.html', {'tags': Tag.objects.get_top(10).all(), 'authors': Author.objects.get_top(12).all()})


def sign_up(request):
    return render(request, 'signup.html', {'tags': Tag.objects.get_top(10).all(), 'authors': Author.objects.get_top(12).all()})


def current_question(request, pk):
    if not Question.objects.contain(pk):
        return render(request, 'error_page.html', {'tags': Tag.objects.get_top(10).all(), 'authors': Author.objects.get_top(12).all()})

    object = Question.objects.base_list_question().get(pk=pk)
    return render(request, 'question.html', {'object': object,
                                             'page_obj': paginate(Answer.objects.base_list_answer(pk).all(), request.GET.get('page'), 5),
                                             'tags': Tag.objects.get_top(10).all(), 'authors':  Author.objects.get_top(12).all()})


def settings(request):
    return render(request, 'settings.html', {'tags': Tag.objects.get_top(10).all(), 'authors': Author.objects.get_top(12).all()})

# Create your views here.

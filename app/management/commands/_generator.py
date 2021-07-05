from random import randint
import random
import os
import django
import faker
from bs4 import BeautifulSoup
import pytz
from django.conf import settings
import urllib.request
from django.db import models

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AskMeVetoshkin.settings')
django.setup()
from app.models import Question, Author, Tag, QuestionLike, User, AnswerLike, Answer


def get_question(pid):
    try:
        soup = BeautifulSoup(
            urllib.request.urlopen('https://ru.stackoverflow.com/questions?pagesize=50&page=' + str(pid)).read(),
            'lxml')
    except urllib.request.HTTPError:
        return None
    published = soup.find("div", {"id": "questions"})
    ans = []
    for header in published.findAll("div", {"class": "question-summary"}):
        tmp = {'head': header.find("div", {'class': 'summary'}).find('h3').find('a').string,
               'ans': header.find("div", {'class': 'summary'}).find('div', {"class": 'excerpt'}).string}
        ans.append(tmp['head'])
    return ans


def save_question():
    out = open('./app/text/question.txt', "a")
    questions = []

    length = randint(100000, 110000)
    j = 68454
    i = 6577
    while j < length:
        ans = get_question(i)
        if ans is not None:
            questions = questions + ans
            out.write("\n".join(ans))
            j += len(ans)
        i -= 1
    out.close()


def get_tag(filename):
    tags = []
    text = open(filename, "r").read().split('\n')  # прочитали текст из файла и избавились от пробелов
    for line in text:
        tags.append(line.split(' ')[1])
    return tags


rus = faker.Faker('ru_RU')
eng = faker.Faker()

path_to_img = "./media/users/"


def generate_img():
    files = os.listdir(path_to_img)
    image = list(filter(lambda x: x.endswith('.jpg'), files))
    return image[randint(0, len(image) - 1)]


def random_name(generator):
    i = 0
    ans = ""
    tmp = generator()
    while i < len(tmp):
        ans += tmp[i]
        i = i + 1
    return ans


def generate_user(number):
    uses_nik = []
    for i in range(1, randint(number, number + number * 0.3)):
        nik = random_name(lambda: eng.simple_profile()['username'])
        while nik in uses_nik:
            nik = random_name(lambda: eng.simple_profile()['username'])
        uses_nik.append(nik)

        us = User(first_name=rus.first_name(), last_name=rus.last_name(), username=nik,
                  email=rus.simple_profile()['mail'])
        us.set_password(rus.password())
        us.save()
        a = Author(image=(path_to_img + generate_img()), profile=us)
        a.save()


def generate_tag(number):
    tags = get_tag('./app/text/tags.txt')
    uses_tag = []
    for i in range(1, randint(number, number + number * 0.3)):
        tag = tags[randint(0, len(tags) - 1)]
        while tag in uses_tag:
            tag = tags[randint(0, len(tags) - 1)]
        uses_tag.append(tag)
        a = Tag(name=tag)
        a.save()


def generate_question(number):
    used_title = []
    out = open('./app/text/question.txt', "r")
    titles = out.read().replace('[закрыт]', '').replace('[дубликат]', '').split('\n')

    authors = Author.objects.all()
    tags = Tag.objects.all()
    j = 1
    for i in titles:
        if j > number:
            break
        if i not in used_title:
            lauthor = authors[randint(0, len(authors) - 1)]
            question = Question(author=lauthor, title=i, text=rus.unique.paragraph(nb_sentences=randint(10, 60)),
                                date=rus.unique.date_time().replace(tzinfo=pytz.timezone(settings.TIME_ZONE)),
                                rating=0)
            question.save()
            used_tag = []
            for j in range(0, randint(2, 7)):
                tmp = randint(0, len(tags) - 1)
                while tmp in used_tag:
                    tmp = randint(0, len(tags) - 1)
                used_tag.append(tmp)
                question.tags.add(tags[tmp])
            question.save()
            used_title.append(i)


def generate_quest_like(number):
    authors = len(Author.objects.all())
    questions = len(Question.objects.all())

    used_pair = []

    for i in range(0, randint(number, number + number * 0.1)):
        author = randint(1, authors)
        question = randint(1, questions)

        while QuestionLike.objects.filter(question_id=question, author_id=author).exists():
            author = randint(1, authors)
            question = randint(1, questions)

        #used_pair.append((question, author))

        like = QuestionLike(number=random.choice([-1, 1]), author_id=author, question_id=question)
        like.save()


def generate_answer(number):
    authors = Author.objects.all()
    questions = Question.objects.all()

    for i in range(0, randint(number, number + number * 0.2)):
        answer = Answer(is_right=randint(0, 1), text=rus.unique.paragraph(nb_sentences=randint(5, 30)),
                        question=questions[randint(0, len(questions) - 1)], author=authors[randint(0, len(authors) - 1)],
                        date=rus.unique.date_time().replace(tzinfo=pytz.timezone(settings.TIME_ZONE)),
                        rating=0)
        answer.save()


def generate_ans_like(number):
    authors = len(Author.objects.all())
    start_answer = Answer.objects.all()[0].pk
    answers = Answer.objects.all()[len(Answer.objects.all())-1].pk

    used_pair = []

    for i in range(0, randint(number, number + number * 0.1)):
        author = randint(1, authors)
        answer = randint(start_answer, answers)

        while AnswerLike.objects.filter(answer_id=answer, author_id=author).exists():
            author = randint(1, authors)
            answer = randint(start_answer, answers)

        used_pair.append((answer, author))

        like = AnswerLike(number=random.choice([-1, 1]), author_id=author, answer_id=answer)
        like.save()


def update_question_rating():
    for question in Question.objects.all():
        question.rating = QuestionLike.objects.filter(question_id=question.pk).aggregate(models.Sum('number'))['number__sum']
        if question.rating is None:
            question.rating = 0
        if question.pk % 100 == 0:
            print(question.pk)
        question.save()


#update_question_rating()
def update_answer_rating():
    for answer in Answer.objects.all():
        answer.rating = AnswerLike.objects.filter(answer_id=answer.pk).aggregate(models.Sum('number'))['number__sum']
        if answer.rating is None:
            answer.rating = 0
        if answer.pk % 100 == 0:
            print(answer.pk)
        answer.save()

#update_answer_rating()
# Question.objects.all().delete()
# Tag.objects.all().delete()
# Author.objects.all().delete()
# User.objects.all().delete()

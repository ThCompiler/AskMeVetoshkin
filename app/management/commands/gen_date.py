from django.core.management.base import BaseCommand
from app.management.commands import _generator as gen


class Command(BaseCommand):
    def handle(self, *args, **options):
        if options['delete']:
            if options['type'] == 'quest_likes':
                gen.QuestionLike.objects.all().delete()
            elif options['type'] == 'questions':
                gen.Question.objects.all().delete()
            elif options['type'] == 'answers':
                gen.Answer.objects.all().delete()
            elif options['type'] == 'tags':
                gen.Tag.objects.all().delete()
            elif options['type'] == 'authors':
                gen.Author.objects.all().delete()
            elif options['type'] == 'ans_likes':
                gen.AnswerLike.objects.all().delete()
        else:
            if options['type'] == 'quest_likes':
                gen.generate_quest_like(options['number'])
            elif options['type'] == 'questions':
                gen.generate_question(options['number'])
            elif options['type'] == 'answers':
                gen.generate_answer(options['number'])
            elif options['type'] == 'tags':
                gen.generate_tag(options['number'])
            elif options['type'] == 'authors':
                gen.generate_user(options['number'])
            elif options['type'] == 'ans_likes':
                gen.generate_ans_like(options['number'])
        print("Done!")

    def add_arguments(self, parser):
        parser.add_argument(
        '-t',
        '--type',
        action='store',
        choices=('questions', 'answers', 'tags', 'authors', 'ans_likes', 'quest_likes'),
        required=True
        )

        parser.add_argument(
            '-n',
            '--number',
            action='store',
            default=300,
            type=int
        )

        parser.add_argument(
            '-d',
            '--delete',
            action='store_true',
            default=False
        )

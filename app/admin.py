from django.contrib import admin
from .models import Question, Author, Tag, QuestionLike, Answer, AnswerLike

admin.site.register(Question)
admin.site.register(Author)
admin.site.register(Tag)
admin.site.register(Answer)
admin.site.register(QuestionLike)
admin.site.register(AnswerLike)
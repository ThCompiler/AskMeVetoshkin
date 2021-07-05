from django import forms
from django.core.exceptions import ValidationError
from numpy import unicode

from AskMeVetoshkin import settings
from app.models import Question, Tag, Author, User


class TagitWidget(forms.HiddenInput):
    """ Widget on the basis of Tag-It! http://aehlke.github.com/tag-it/"""

    class Media:
        js = (settings.STATIC_URL + 'js/tag-it.js',
              settings.STATIC_URL + 'js/tagit_widget.js',)
        css = {"all": (settings.STATIC_URL + 'css/jquery.tagit.css',)}


class TagitField(forms.Field):
    """ Tag field """

    widget = TagitWidget

    def __init__(self, tag_model, *args, **kwargs):
        self.tag_model = tag_model
        super(TagitField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        tag_strings = value.split(',')
        return [self.tag_model.get_or_create(tag_string) for tag_string in tag_strings if len(tag_string) > 0]

    def validate(self, value):
        if len(value) == 0 and self.required:
            raise ValidationError(self.error_messages['required'])

    def prepare_value(self, value):
        if value is not None and hasattr(value, '__iter__'):
            return ','.join((unicode(tag) for tag in value))
        return value

    def widget_attrs(self, widget):
        res = super(TagitField, self).widget_attrs(widget) or {}
        res["class"] = "tagit"
        return res


class LoginForm(forms.Form):
    username = forms.CharField(label="Логин")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput())


class AskForm(forms.Form):
    title = forms.CharField(label="Заголовок вопроса")
    text = forms.CharField(label="Вопрос", widget=forms.Textarea())
    tags = TagitField(Tag, label='Tags', required=True)


class AnswerForm(forms.Form):
    text = forms.CharField(label="", widget=forms.Textarea())


class SettingsForm(forms.Form):
    login = forms.CharField(label="Логин")
    email = forms.EmailField(label="Email")
    username = forms.CharField(label="Ник")
    image = forms.ImageField()


class SettingsFormUser(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'email', 'username']
        widgets = {
            'email': forms.EmailInput()
        }
        labels = {
            'first_name': "Ник",
            'username': "Логин",
            'email': "Email"
        }


class SettingsFormAuthor(forms.ModelForm):

    class Meta:
        model = Author
        fields = ['image']

        widgets = {
            'image': forms.FileInput()
        }


class RegisterForm(forms.Form):
    login = forms.CharField(label="Логин")
    email = forms.EmailField(label="Email")
    username = forms.CharField(label="Ник")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput())
    rep_password = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput())
    image = forms.ImageField()

    def clean(self):
        cleanDate = super().clean()
        password_one = cleanDate['password']
        password_two = cleanDate['rep_password']
        username = cleanDate['username']
        login = cleanDate['login']

        if password_one != password_two:
            self.add_error(None, "Пароли не совпадают")

        if User.objects.filter(first_name=username).all().count() != 0:
            cleanDate['username'] = ""
            self.add_error(None, "Пользователь с таким именем уже существует")

        if User.objects.filter(first_name=login).all().count() != 0:
            cleanDate['login'] = ""
            self.add_error(None, "Пользователь с таким логином уже существует")

        return cleanDate

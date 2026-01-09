from django import forms
from .models import Post, Comment, User
from django.core.mail import send_mail
from datetime import datetime
from django.core.exceptions import ValidationError
import pytz


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'image', 'pub_date', 'location', 'category')
        widgets = {'pub_date': forms.DateTimeInput(
                   attrs={'type': 'datetime-local'}),
                   'text': forms.Textarea(attrs={'cols': 10, 'rows': 10})}

    def clean(self):
        super().clean()
        if self.is_valid():
            pub_date = self.cleaned_data['pub_date']
            title = self.cleaned_data['title']
            print(pub_date)
            if pub_date < datetime(1969, 10, 29, 0, 0, 0, tzinfo=pytz.utc):
                send_mail(
                    subject='Неправильная дата',
                    message=f'в посте {title} неправильно введена дата',
                    from_email='post_from@sprint4.com',
                    recipient_list=['to_admin@sprint4.com'],
                    fail_silently=True,
                )
                raise ValidationError(
                    'До 29 октября 1969 года интернета не было')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {'text': forms.Textarea(attrs={'cols': 10, 'rows': 10})}


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email',)

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

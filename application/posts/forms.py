from django import forms
from .models import Post, CommentForPost


def warning_form(self, form):
    field = dict(self.fields.items()).get(form)
    field.widget.attrs['class'] += ' is-warning'


def invalid_form(self, form):
    field = dict(self.fields.items()).get(form)
    field.widget.attrs['class'] += ' is-invalid'


class NewPostPage(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'file']

    content = forms.CharField(
        label='Додати підпис',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
        required=False)

    file = forms.FileField(
        label='Завантажити фото',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        required=False)

    def clean(self):
        uploaded_file = self.cleaned_data.get('file')
        content = self.cleaned_data.get('content')

        if uploaded_file:
            allowed_mime_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif', 'video/mp4', 'video/quicktime']

            if uploaded_file.content_type not in allowed_mime_types:
                invalid_form(self, 'file')
                self.add_error('file', 'Цей тип файлу не підтримується.')

        if not uploaded_file and not content:
            warning_form(self, 'file')
            warning_form(self, 'content')
            self.add_error('content', 'Додайте підпис або зображення!')


class CommentForPostPage(forms.ModelForm):
    class Meta:
        model = CommentForPost
        fields = ['content']

    content = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '5',
            'placeholder': 'Відповідь',
            'style': 'border: 0; resize: none; box-shadow: 0 0 0 0; border-color: var(--bs-border-color); mb-3;'
        })
    )

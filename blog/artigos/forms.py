from django import forms
from django.utils.text import slugify
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['titulo', 'resumo', 'conteudo', 'categoria', 'tags', 'situacao']
        widgets = {'conteudo': forms.Textarea(attrs={'rows': 12})}

    def clean_titulo(self):
        titulo = self.cleaned_data['titulo'].strip()
        if len(titulo) < 10:
            raise forms.ValidationError('O título precisa ter no mínimo 10 caracteres.')
        return titulo

    def clean(self):
        dados = super().clean()
        if dados.get('situacao') == Post.Situacao.PUBLICADO and not dados.get('resumo'):
            raise forms.ValidationError('Um post publicado precisa ter resumo.')
        return dados

    def save(self, commit=True):
        post = super().save(commit=False)
        # Na edição, preservamos a URL já divulgada.
        if not post.slug:
            base = slugify(post.titulo)[:190] or 'post'
            slug = base
            numero = 2
            while Post.objects.exclude(pk=post.pk).filter(slug=slug).exists():
                slug = f'{base}-{numero}'
                numero += 1
            post.slug = slug
        if commit:
            post.save()
            self.save_m2m()
        return post


class BuscaForm(forms.Form):
    q = forms.CharField(label='Buscar', max_length=100, required=False)

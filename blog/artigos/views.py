from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from .forms import BuscaForm, PostForm
from .models import Categoria, Post


def lista(request):
    posts = Post.objects.filter(situacao=Post.Situacao.PUBLICADO).select_related('categoria')
    return render(request, 'artigos/lista.html', {'posts': posts})


def por_categoria(request, slug):
    categoria = get_object_or_404(Categoria, slug=slug)
    posts = categoria.posts.filter(situacao=Post.Situacao.PUBLICADO)
    return render(request, 'artigos/lista.html', {'posts': posts, 'categoria': categoria})


def detalhe(request, slug):
    visiveis = Q(situacao=Post.Situacao.PUBLICADO)
    if request.user.is_authenticated:
        visiveis |= Q(autor=request.user)
    post = get_object_or_404(Post.objects.filter(visiveis).select_related('autor', 'categoria').prefetch_related('tags'), slug=slug)
    return render(request, 'artigos/detalhe.html', {'post': post})


@login_required
@permission_required('artigos.add_post', raise_exception=True)
def novo(request):
    form = PostForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.autor = request.user
        post.save()
        form.save_m2m()
        messages.success(request, 'Post criado com sucesso.')
        return redirect(post)
    return render(request, 'artigos/post_form.html', {'form': form})


class EditarPost(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'artigos.change_post'
    model = Post
    form_class = PostForm
    template_name = 'artigos/post_form.html'

    def get_queryset(self):
        return Post.objects.filter(autor=self.request.user)

    def form_valid(self, form):
        resposta = super().form_valid(form)
        messages.success(self.request, 'Post atualizado com sucesso.')
        return resposta


@login_required
@permission_required('artigos.delete_post', raise_exception=True)
def excluir(request, slug):
    post = get_object_or_404(Post, slug=slug, autor=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post excluído com sucesso.')
        return redirect('artigos:lista')
    return render(request, 'artigos/post_confirm_delete.html', {'post': post})


def busca(request):
    form = BuscaForm(request.GET)
    posts = Post.objects.none()
    if form.is_valid() and form.cleaned_data['q']:
        termo = form.cleaned_data['q']
        posts = Post.objects.filter(situacao=Post.Situacao.PUBLICADO).filter(Q(titulo__icontains=termo) | Q(conteudo__icontains=termo))
    return render(request, 'artigos/busca.html', {'form': form, 'posts': posts})


@login_required
def meus_posts(request):
    posts = request.user.posts.select_related('categoria')
    return render(request, 'artigos/lista.html', {'posts': posts, 'meus_posts': True})


def cadastro(request):
    form = UserCreationForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        usuario = form.save()
        login(request, usuario)
        messages.success(request, 'Conta criada com sucesso. Aguarde a atribuição de um grupo para escrever.')
        return redirect('artigos:meus_posts')
    return render(request, 'registration/cadastro.html', {'form': form})

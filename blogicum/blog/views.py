from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Category, Comment
from datetime import datetime
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .forms import CommentForm, PostForm, UserForm
from django.views.generic import UpdateView, DeleteView
from django.urls import reverse_lazy
from users.forms import User


# Добавить пост
@login_required
def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None,)
    template = 'blog/create.html'
    context = {'form': form}
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, template, context)


# Редактировать пост
def post_update(request, pk):
    instance = get_object_or_404(Post, pk=pk)
    template = 'blog/create.html'
    form = PostForm(request.POST or None, instance=instance)
    context = {'form': form,
               'comment': instance}

    if form.is_valid():
        if instance.author == request.user:
            form.save()
        return redirect("blog:post_detail", pk=pk)
    elif not request.user.is_authenticated:
        return redirect("blog:post_detail", pk=pk)

    return render(request, template, context)


# Удаление поста
def post_delete(request, pk):
    instance = get_object_or_404(Post, pk=pk)
    template = 'blog/create.html'
    context = {'comment': instance}

    if request.method == 'POST' and instance.author == request.user:
        instance.delete()
        return redirect('blog:index')

    return render(request, template, context)


# Главная страница
def index(request):
    template = 'blog/index.html'
    posts = Post.objects.select_related('category').filter(
        is_published=True, category__is_published=True,
        pub_date__lte=datetime.now()).select_related(
        'category').order_by('-pub_date')
    for post in posts:
        post.comment_count = Comment.objects.filter(post=post.id).count()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, template, context)


# Просмотр поста
def post_detail(request, pk):
    template = 'blog/detail.html'
    if request.user == get_object_or_404(Post.objects.select_related(
            'author').filter(id=pk)).author:
        post = get_object_or_404(Post.objects.select_related(
            'category').select_related('location').select_related(
            'author').filter(id=pk))
    else:
        post = get_object_or_404(Post.objects.select_related(
            'category').select_related('location').select_related(
            'author').filter(is_published=True, category__is_published=True,
                             id=pk, pub_date__lte=datetime.now()))

    comments = Comment.objects.select_related('author').select_related(
        'post').filter(post__id=pk)
    context = {"post": post,
               "comments": comments,
               "form": CommentForm(request.POST), }

    return render(request, template, context)


# Просмотр по категории
def category_posts(request, category_slug):
    template = "blog/category.html"

    the_category = get_object_or_404(Category.objects.values(
        'id', 'title', 'description'
    ).filter(
        is_published=True, slug=category_slug))

    category_posts = Post.objects.select_related('category').filter(
        is_published=True, category__is_published=True,
        category__pk=the_category['id'],
        pub_date__lte=datetime.now()).order_by('-pub_date')

    for post in category_posts:
        post.comment_count = Comment.objects.filter(post=post.id).count()

    paginator = Paginator(category_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'category': the_category,
               'page_obj': page_obj}
    return render(request, template, context)


# Просмотр профиля
def profile(request, username):
    template = "blog/profile.html"
    profile = get_object_or_404(User, username=username)

    author_posts = Post.objects.select_related('author').filter(
        author__username=username,).order_by('-pub_date')

    for post in author_posts:
        post.comment_count = Comment.objects.filter(post=post.id).count()

    paginator = Paginator(author_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj,
               'profile': profile, }

    return render(request, template, context)


# Добавление комментария
@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


# Редактирование профиля
def edit_profile(request):
    template = "blog/user.html"
    instance = get_object_or_404(User, username=request.user.username)
    form = UserForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
    return render(request, template, context)


# Удаление комментария
def comment_delete(request, post_id, comment_id):
    template = 'blog/comment.html'
    instance = get_object_or_404(Comment, pk=comment_id)
    context = {'comment': instance}
    if request.method == 'POST' and instance.author == request.user:
        instance.delete()
        return redirect('blog:index')
    return render(request, template, context)


# Редактирование комментария
def comment_update(request, post_id, comment_id):

    instance = get_object_or_404(Comment, pk=comment_id)
    template = 'blog/comment.html'
    form = CommentForm(request.POST or None, instance=instance)
    context = {'form': form,
               'comment': instance}
    if form.is_valid() and instance.author == request.user:
        form.save()
    return render(request, template, context)

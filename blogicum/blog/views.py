from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Category, Comment
from datetime import datetime
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .forms import CommentForm, PostForm, UserForm
from users.forms import User
from django.db.models import Count
from datetime import datetime, timezone, timedelta


# Вычисление одной страницы пагинатора
def get_page_obj(the_set, request):
    paginator = Paginator(the_set, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


# Фильтрация записей по опубликованности
def date_sort(the_set):
    return the_set.order_by('-pub_date')


# Добавить пост
@login_required
def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None,)
    template = 'blog/create.html'
    context = {'form': form}
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.pub_date = post.pub_date.replace(tzinfo=timezone(
            timedelta(hours=0, minutes=0)))
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, template, context)


# Редактировать пост
def post_update(request, post_id):
    instance = get_object_or_404(Post, pk=post_id)
    if instance.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    template = 'blog/create.html'
    form = PostForm(request.POST or None, instance=instance)
    context = {'form': form,
               'comment': instance}

    if form.is_valid():
        if instance.author == request.user:
            form.save()
        return redirect('blog:post_detail', post_id=post_id)
    elif not request.user.is_authenticated:
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, template, context)


# Удаление поста
def post_delete(request, post_id):
    instance = get_object_or_404(Post, pk=post_id)
    if instance.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

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
        'category').annotate(comment_count=Count('comments'))
    page_obj = get_page_obj(date_sort(posts), request)
    context = {'page_obj': page_obj}
    return render(request, template, context)


# Просмотр поста
def post_detail(request, post_id):
    template = 'blog/detail.html'
    if request.user == get_object_or_404(Post.objects.select_related(
            'author').filter(id=post_id)).author:
        post = get_object_or_404(Post.objects.select_related(
            'category').select_related('location').select_related(
            'author').filter(id=post_id))
    else:
        post = get_object_or_404(Post.objects.select_related(
            'category').select_related('location').select_related(
            'author').filter(is_published=True, category__is_published=True,
                             id=post_id, pub_date__lte=datetime.now()))

    comments = Comment.objects.select_related('author').select_related(
        'post').filter(post__id=post_id)
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
        pub_date__lte=datetime.now())

    for post in category_posts:
        post.comment_count = Comment.objects.filter(post=post.id).count()

    page_obj = get_page_obj(date_sort(category_posts), request)

    context = {'category': the_category,
               'page_obj': page_obj}
    return render(request, template, context)


# Просмотр профиля
def profile(request, username):
    template = "blog/profile.html"
    profile = get_object_or_404(User, username=username)

    if request.user == get_object_or_404(User.objects.
                                         filter(username=username)):
        author_posts = Post.objects.select_related('author').filter(
            author__username=username,).annotate(
            comment_count=Count('comments'))
    else:
        author_posts = Post.objects.select_related('author').filter(
            author__username=username, is_published=True).annotate(
            comment_count=Count('comments'))

    page_obj = get_page_obj(date_sort(author_posts), request)

    context = {'page_obj': page_obj,
               'profile': profile, }

    return render(request, template, context)


# Добавление комментария
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


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
@login_required
def comment_delete(request, post_id, comment_id):
    template = 'blog/comment.html'
    instance = get_object_or_404(Comment, pk=comment_id)
    if instance.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    context = {'comment': instance}
    if request.method == 'POST' and instance.author == request.user:
        instance.delete()
        return redirect('blog:index')
    return render(request, template, context)


# Редактирование комментария
@login_required
def comment_update(request, post_id, comment_id):

    instance = get_object_or_404(Comment, pk=comment_id)
    if instance.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    template = 'blog/comment.html'
    form = CommentForm(request.POST or None, instance=instance)
    context = {'form': form,
               'comment': instance}
    if form.is_valid() and instance.author == request.user:
        form.save()
    return render(request, template, context)

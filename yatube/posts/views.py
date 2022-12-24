from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.http import HttpRequest

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from .utils import get_page_object


@cache_page(20, key_prefix='index_page')
def index(request: HttpRequest):
    template = 'posts/index.html'
    post_list = Post.objects.all().order_by('-pub_date')
    page_obj = get_page_object(post_list, request)
    context = {
        'page_obj': page_obj
    }

    return render(request, template, context)


def group_posts(request: HttpRequest, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all().order_by('-pub_date')
    page_obj = get_page_object(post_list, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }

    return render(request, template, context)


def profile(request: HttpRequest, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts_list = author.posts.all().order_by('-pub_date')
    page_obj = get_page_object(posts_list, request)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user,
                                          author=author).exists()
        context['following'] = following

    return render(request, template, context)


def post_detail(request: HttpRequest, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }

    return render(request, template, context)


@login_required
def add_comment(request: HttpRequest, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', post_id=post_id)


@login_required
def post_create(request: HttpRequest):
    template = 'posts/post_create.html'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:profile', request.user)

    return render(request, template, {'form': form})


@login_required
def post_edit(request: HttpRequest, post_id):
    template = 'posts/post_create.html'
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post.pk)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.pk)
    context = {
        'form': form,
        'post_id': post_id,
        'is_edit': True
    }

    return render(request, template, context)


@login_required
def follow_index(request: HttpRequest):
    posts_list = Post.objects.filter(author__following__user=request.user)
    page_obj = get_page_object(posts_list, request)
    context = {
        'page_obj': page_obj
    }

    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request: HttpRequest, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(author=author, user=request.user)

    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request: HttpRequest, username):
    subscription = get_object_or_404(User, username=username)
    following = Follow.objects.filter(author=subscription, user=request.user)
    following.delete()

    return redirect('posts:follow_index')

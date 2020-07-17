from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Post, Group, User
from . forms import PostForm
from django.contrib.auth.decorators import login_required


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    groups = get_object_or_404(Group, slug=slug)
    posts = groups.group_posts.all()
    page_number = request.GET.get('page')
    paginator = Paginator(posts, 10)
    page = paginator.get_page(page_number)
    return render(
        request,
        "group.html",
        {"group": groups, 'page': page, 'paginator': paginator}
    )


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        return render(request, 'new_post.html', {'form': form})
    form = PostForm()
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)
    paginator = Paginator(posts, 10)
    page_num = request.GET.get('page')
    page = paginator.get_page(page_num)
    return render(
        request,
        'profile.html',
        {
            'page': page,
            'paginator': paginator,
            'author': author,
            'post_sum': posts.count()
        }
    )


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    # post = Post.objects.filter(pk=post_id)
    post = get_object_or_404(Post, pk=post_id)
    return render(
        request,
        'post.html',
        {
            'author': author,
            'post': post
        }
    )


def post_edit(request, username, post_id):
    # тут тело функции. Не забудьте проверить,
    # что текущий пользователь — это автор записи.
    # В качестве шаблона страницы редактирования укажите шаблон создания новой записи
    # который вы создали раньше (вы могли назвать шаблон иначе)
    return render(request, 'post_new.html', {})



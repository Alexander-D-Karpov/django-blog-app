import secrets
import string

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import F, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.text import slugify

from .models import Post, UserRate, Comment, CommentRate
from .models import PostFile


def post_list(request):
    user_from = request.GET.get("user")
    search_post = request.GET.get("search")
    if search_post:
        posts = Post.objects.filter(
            Q(title__icontains=search_post) | Q(body__icontains=search_post)
        )
    else:
        posts = sorted(Post.objects.all(), key=lambda x: x.date_pub, reverse=True)
    if user_from:
        posts = [x for x in posts if x.creator.username == user_from]
    else:
        posts = [x for x in posts if x.creator.is_superuser]
    return render(request, "blog/index.html", context={"posts": posts})


def top_post_list(request):
    search_post = request.GET.get("search")
    if search_post:
        posts = Post.objects.filter(
            Q(title__icontains=search_post) | Q(body__icontains=search_post)
        )
    else:
        posts = sorted(Post.objects.all(), key=lambda x: x.post_views, reverse=True)
    return render(
        request,
        "blog/index.html",
        context={"posts": posts, "message": "Most rated posts:"},
    )


def rate_post(request, slug):
    if request.method == "POST" and request.user.is_authenticated:
        rate = round(int(request.POST["rating"]))
        post = Post.objects.get(slug=slug)
        if 0 <= rate <= 5:
            if not UserRate.objects.filter(
                user=request.user, post__slug=post.slug
            ).exists():
                UserRate.objects.create(user=request.user, post_id=post.id, rating=rate)
                post.count_rating(rate)
            else:
                old_rate = UserRate.objects.get(
                    user=request.user, post__slug=post.slug
                ).rating
                new_rate = rate
                Post.objects.get(slug=slug).update_rating(old_rate, new_rate)
                UserRate.objects.filter(user=request.user, post__slug=post.slug).update(
                    rating=new_rate
                )
    return redirect("post_view_url", slug=slug)


def top_comment_post_list(request):
    search_post = request.GET.get("search")
    if search_post:
        posts = Post.objects.filter(
            Q(title__icontains=search_post) | Q(body__icontains=search_post)
        )
    else:
        posts = sorted(
            Post.objects.all(),
            key=lambda x: len(x.comments.filter(active=True)),
            reverse=True,
        )
    return render(
        request,
        "blog/index.html",
        context={"posts": posts, "message": "Posts with the most comments:"},
    )


def menadus(request):
    return render(request, "menad.html")


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post_views = post.post_views + 1

    rate = None
    files = [x.file for x in PostFile.objects.filter(post__slug=slug)]
    range = [5, 4, 3, 2, 1]
    new_comment = None
    if UserRate.objects.filter(
        user__username=request.user.username, post__slug=post.slug
    ).exists():
        rate = UserRate.objects.get(
            user_id=request.user.id, post__slug=post.slug
        ).rating
    # Comment posted
    if request.method == "POST" and not Comment.objects.filter(body=request.POST["body"], post=post).exists():
        if request.user.is_authenticated:
            Comment.objects.create(
                name=request.user.username,
                body=request.POST["body"],
                post=post,
                active=True,
                from_user=True,
            )
        else:
            Comment.objects.create(
                name=request.POST["username"], body=request.POST["body"], post=post
            )
            new_comment = True

    comments = post.comments.filter(active=True).order_by("sum_rate").reverse()
    comments_peg = Paginator(comments, 10)
    com_number = request.GET.get("comment")
    try:
        comments = comments_peg.get_page(com_number)
    except PageNotAnInteger:
        comments = comments_peg.page(1)
    except EmptyPage:
        comments = comments_peg.page(comments_peg.num_pages)

    comment_rates_up = None
    comment_rates_down = None
    if request.user.is_authenticated:
        comment_rates_up = [x.comment for x in CommentRate.objects.filter(comment__in=comments, user=request.user, rate=True)]
        comment_rates_down = [x.comment for x in CommentRate.objects.filter(comment__in=comments, user=request.user, rate=False)]

    post.post_views = F("post_views") + 1
    post.save(update_fields=["post_views"])
    return render(
        request,
        "blog/post_view.html",
        {
            "post": post,
            "post_views": post_views,
            "comments": comments,
            "new_comment": new_comment,
            "comment_rates_up": comment_rates_up,
            "comment_rates_down": comment_rates_down,
            "user_rate": rate,
            "range": range,
            "files": files,
            "p": comments_peg,
        },
    )


def post_create(request):
    if request.method == "GET":
        return render(request, "blog/create.html")
    elif request.method == "POST":
        if request.user.is_authenticated:
            heading = request.POST["heading"][:150]
            text = request.POST["text"]
            image = None
            if request.FILES:
                image = request.FILES["image"]
            post = Post.objects.create(
                title=heading,
                image=image,
                slug=str(
                    slugify(heading[:30])
                    + "".join(secrets.choice(string.ascii_letters) for i in range(5))
                ),
                body=text,
                isMD=True,
                creator=request.user,
            )
            return redirect("post_view_url", slug=post.slug)


def rate_comment(request, slug):
    if request.method == "POST" and request.user.is_authenticated:
        if "comment_up" in request.POST:
            comment = Comment.objects.get(id=request.POST["comment_up"])
            if com_rate := CommentRate.objects.filter(
                user=request.user, post__slug=slug, comment=comment
            ):
                rate = com_rate[0].rate
                if not rate:
                    com_rate[0].rate = True
                    com_rate[0].save()

                    comment.sum_rate += 2
                    comment.save()
                else:
                    com_rate[0].delete()

                    comment.sum_rate -= 1
                    comment.save()
            else:
                CommentRate.objects.create(
                    user=request.user,
                    post=Post.objects.get(slug=slug),
                    comment=comment,
                    rate=True,
                )

                comment.sum_rate += 1
                comment.save()
        elif "comment_down" in request.POST:
            comment = Comment.objects.get(id=request.POST["comment_down"])
            if com_rate := CommentRate.objects.filter(
                user=request.user, post__slug=slug, comment=comment
            ):
                rate = com_rate[0].rate
                if rate:
                    com_rate[0].rate = False
                    com_rate[0].save()

                    comment.sum_rate -= 2
                    comment.save()
                else:
                    com_rate[0].delete()

                    comment.sum_rate += 1
                    comment.save()
            else:
                CommentRate.objects.create(
                    user=request.user,
                    post=Post.objects.get(slug=slug),
                    comment=comment,
                    rate=False,
                )

                comment.sum_rate -= 1
                comment.save()

    return redirect("post_view_url", slug=slug)

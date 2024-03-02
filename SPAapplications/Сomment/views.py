import random
from io import BytesIO
from tkinter import Image
from xml import etree
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from bleach import clean
from captcha.image import ImageCaptcha
from django.conf import settings
from rest_framework import pagination
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse, HttpResponseBadRequest
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import View

from .serializers import *


# Create your views here.
class PostListView(View):
    def get(self, request):
        post = Post.objects.order_by('-pub_date')[:7]
        return render(request, 'Comment/index.html', {'post': post})


def get_comments_tree(comments):
    comments_dict = {}
    parent_comments = []

    for comment in comments:
        if comment.parent_comment:
            comments_dict.setdefault(comment.parent_comment_id, []).append(comment)
        else:
            parent_comments.append(comment)

    for parent_comment in parent_comments:
        parent_comment.children_comments = comments_dict.get(parent_comment.id, [])

    return parent_comments


class PostDetailView(View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        comments = Comment.objects.filter(post=post).order_by('-created_at')
        parent_comments = get_comments_tree(comments)

        paginator = Paginator(parent_comments, 25)  # 25 коментарів на сторінку
        page_number = request.GET.get('page')
        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        return render(request, 'Comment/detail.html', {
            'post': post,
            'parent_comments': page,
            'page': page,
            'total_pages': paginator.num_pages,
        })


def get_captcha(request):
    if request.method == 'GET':
        captcha_text = ''.join(random.choices('0123456789', k=4))  # Створення випадкового рядка з цифр

        image = ImageCaptcha()
        image_bytes = image.generate(captcha_text)

        # Створення  зображенням CAPTCHA
        response = HttpResponse(image_bytes, content_type='image/png')
        response['Content-Disposition'] = 'inline; filename="captcha.png"'

        # Зберігання очікуваного тексту CAPTCHA у сесії
        request.session['expected_captcha'] = captcha_text

        return response


def validate_xhtml(text):
    try:
        etree.fromstring("<root>" + text + "</root>")
        return True
    except etree.XMLSyntaxError:
        return False


BLEACH_ALLOWED_TAGS = settings.BLEACH_ALLOWED_TAGS
BLEACH_ALLOWED_ATTRIBUTES = settings.BLEACH_ALLOWED_ATTRIBUTES


def leave_comment(request, post_id):
    if request.method == 'POST':
        # Перевірка CAPTCHA
        if request.POST.get('captcha') != request.session.get('expected_captcha', ''):
            return HttpResponseBadRequest("Вкажіть правильну CAPTCHA")

        # Отримання даних з POST-запиту
        user_name = request.POST.get('user_name')
        email = request.POST.get('email')
        text = request.POST.get('text')
        photo = request.FILES.get('photo')
        file = request.FILES.get('file')
        parent_id = request.POST.get('parent_comment')

        # Отримання або створення поста
        post = get_object_or_404(Post, id=post_id)

        # Отримання або створення батьківського коментаря
        parent_comment = get_object_or_404(Comment, id=parent_id) if parent_id else None
        # Обробка фото, якщо воно було завантажено
        if photo:
            # Валідація формату фото
            formats_valid = ['image/jpeg', 'image/png', 'image/gif']
            if photo.content_type not in formats_valid:
                return JsonResponse({'success': False, 'message': 'Недоступний формат зображення'}, status=400)

            # Обробка фото для зменшення розміру
            img = Image.open(photo)
            width, height = img.size
            max_size = (320, 240)
            if width > max_size[0] or height > max_size[1]:
                img = img.resize(max_size)
                output_buffer = BytesIO()
                img.save(output_buffer, format=photo.content_type.split('/')[-1].upper())
                photo = output_buffer

        # Обробка текстового файлу, якщо він був завантажений
        if file:
            # Валідація формату файлу
            if not file.name.endswith('.txt'):
                return JsonResponse(
                    {'success': False, 'message': 'Недопустимий формат файлу. Дозволені лише .txt файли.'},
                    status=400)
            # Валідація розміру файлу
            if file.size > 102400:
                return JsonResponse({'success': False, 'message': 'Файл занадто великий'}, status=400)

        # Створення об'єкта клієнтської інформації
        client_info = ClientInfo.objects.create(ip_address=request.META.get('REMOTE_ADDR'), user_name=user_name,
                                                user_agent=request.META.get('HTTP_USER_AGENT', ''))

        # Створення коментаря для поста
        post.comment_set.create(user_name=user_name, email=email, text=text, text_file=file, image=photo,
                                post=post, parent_comment=parent_comment, client_info=client_info)

        # Перенаправлення на сторінку деталей поста
        return HttpResponseRedirect(reverse('Comments:post_detail', args=(post.id,)))
    else:
        # Якщо метод запиту не є POST
        return HttpResponseBadRequest("Неприпустимий метод запиту")

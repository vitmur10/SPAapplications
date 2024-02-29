import random
from io import BytesIO
from tkinter import Image
from xml import etree

from bleach import clean
from captcha.image import ImageCaptcha
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from .serializers import *


# Create your views here.
class PostListView(View):
    def get(self, request):
        post = Post.objects.order_by('-pub_date')[:7]
        return render(request, 'Comment/index.html', {'post': post})


class PostDetailView(View):
    def get(self, request, post_id):
        post = Post.objects.get(id=post_id)
        latest_comment_list = post.comment_set.order_by('-id')[:25]
        return render(request, 'Comment/detail.html', {
            'post': post,
            'latest_comment_list': latest_comment_list
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
    if request.POST.get('captcha') != request.session.get('expected_captcha', ''):
        return HttpResponse("Вкажіть правильну капчу", status=400)
    try:
        post = Post.objects.get(id=post_id)
    except:
        raise Http404('Статья не знайдена')
    user_name = request.POST.get('user_name')
    email = request.POST.get('email')
    text = request.POST.get('text')

    id_parent = request.POST.get('parent_comment')
    parent_comment = Comment.objects.get(id=id_parent) if id_parent else None
    try:
        file_image = request.POST.get('photo')
        if file_image:
            formats_valid = ['image/jpeg', 'image/png', 'image/gif']
            if file_image.content_type not in formats_valid:
                return JsonResponse({'success': False, 'message': 'Недоступний формат заображення'}, status=400)

            img = Image.open(file_image)
            width, height = img.size
            max_size = (320, 240)
            if width > max_size[0] or height > max_size[1]:
                img = img.resize(max_size)
                output_buffer = BytesIO()
                img.save(output_buffer, format=file_image.content_type.split('/')[-1].upper())

                file_image = InMemoryUploadedFile(output_buffer,
                                                  'ImageField', f"{file_image.name}",
                                                  file_image.content_type, output_buffer.tell, None)
            comment.text = file_image
    except Exception as e:
        print(e)
    # Обработка текстового файла
    try:
        file_tmp_file = request.POST.get('file')
        if file_tmp_file:
            if not file_tmp_file.name.endswith('.txt'):
                return JsonResponse(
                    {'success': False, 'message': 'Недопустимый формат файла. Разрешены только .txt файлы.'},
                    status=400)
            if file_tmp_file.size > 102400:
                return JsonResponse({'success': False, 'message': 'Файл слишком большой'}, status=400)

            comment.text_file = file_tmp_file
            new_name = comment.text_file.name.split('/')[-1]
            comment.text_file.name = new_name
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")

    post.comment_set.create(user_name=user_name, email=email, text=text, file=file, photo=photo,
                            post=post, parent_comment=parent_comment)
    return HttpResponseRedirect(reverse('Comments:post_detail', args=(post.id,)))


class CommentAddView(View):
    serializer = ClientInfoSerializer(data={
        'id_address': request.META.get('REMOTE_ADDR'),
        'username': comment.user.username,
        'user_agent': str(comment.user.user_agent)
    })

    if serializer.is_valid():
        comment.client_info = serializer.save()

    comment.text = clean(comment.text, tafs=BLEACH_ALLOWED_TAGS, attributes=BLEACH_ALLOWED_ATTRIBUTES)

    if not validate_xhtml(comment.text):
        return HttpResponse("Вкажіть правильну капчу", status=400)

else:
return HttpResponse(
    "Помилка введених даних. Будь ласка, перевірте правильність введених даних і спробуйте ще раз.",
    status=400)

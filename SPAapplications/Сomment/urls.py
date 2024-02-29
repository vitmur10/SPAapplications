from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from . import views

app_name = 'Comments'

urlpatterns = [
                  path('', views.PostListView.as_view(), name='post'),
                  path('<int:post_id>/', views.PostDetailView.as_view(), name='post_detail'),
                  path('captcha/', include('captcha.urls')),
                  path('get_captcha/', views.get_captcha, name='get_captcha'),
                  path('<int:post_id>/leave_comment/', views.leave_comment, name='leave_comment'),
                  path('<int:post_id>/', views.CommentAddView.post, name='comm ent-list'),
                  path('<int:post_id>/create/', views.CommentAddView.post, name='create-comment'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL,
                                                                                           document_root=settings.MEDIA_ROOT)

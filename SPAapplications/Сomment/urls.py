from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import PostDetailView, get_captcha, leave_comment, PostListView

app_name = 'Comments'

urlpatterns = [
                  path('', PostListView.as_view(), name='index'),
                  path('<int:post_id>/', PostDetailView.as_view(), name='post_detail'),
                  path('captcha/', get_captcha, name='get_captcha'),
                  path('leave_comment/<int:post_id>/', leave_comment, name='leave_comment'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL,
                                                                                           document_root=settings.MEDIA_ROOT)

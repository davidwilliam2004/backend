from django.urls import path
from .views import signup, login, chat_with_ai
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("signup/", signup),
    path("login/", login),
    path("chat_ai/", chat_with_ai),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
 

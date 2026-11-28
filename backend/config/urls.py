"""
URL configuration for Signa Link ISL Chat Application
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/contacts/', include('contacts.urls')),
    path('api/conversations/', include('conversations.urls')),
    path('api/messages/', include('messages_app.urls')),
    path('api/recognition/', include('recognition.urls')),
    path('api/status/', include('status.urls')),
    path('api/typing/', include('typing_indicators.urls')),
    path('api/llm/', include('llm_service.urls')),
    path('api/chat/', include('chat.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


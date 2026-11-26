from django.urls import path
from .views import RecognizeSignView
from llm_service.isl_chat_views import process_sign_sequence, flush_sign_sequence

urlpatterns = [
    path('recognize/', RecognizeSignView.as_view(), name='recognize-sign'),
    path('sequence/',  process_sign_sequence,       name='sign-sequence'),
    path('flush/',     flush_sign_sequence,          name='sign-flush'),
]

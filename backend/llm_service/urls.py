from django.urls import path
from llm_service import views, isl_chat_views

urlpatterns = [
    # Phase 2 & 3: ISL-Chat pipeline
    path('isl-chat/',        isl_chat_views.isl_chat,                name='isl-chat'),
    path('history/',         isl_chat_views.get_conversation_history, name='llm-history'),
    path('clear/',           isl_chat_views.clear_conversation,       name='llm-clear'),
    path('provider-status/', isl_chat_views.llm_provider_status,     name='llm-provider-status'),
    path('stats/',           isl_chat_views.get_session_stats,        name='llm-stats'),
    path('speak/',           isl_chat_views.speak_message,            name='llm-speak'),

    # Original features
    path('translate-signs/', views.translate_signs,         name='translate-signs'),
    path('convert-to-isl/',  views.convert_to_isl,          name='convert-to-isl'),
    path('suggest-responses/',views.suggest_responses,      name='suggest-responses'),
    path('explain-sign/',    views.explain_sign,             name='explain-sign'),
    path('summarize/',       views.summarize_conversation,   name='summarize'),
    path('status/',          views.llm_status,               name='llm-status'),
    path('chatbot/start/',   views.chatbot_start,            name='chatbot-start'),
    path('chatbot/chat/',    views.chatbot_message,          name='chatbot-chat'),
    path('chatbot/reset/',   views.chatbot_reset,            name='chatbot-reset'),
    path('chatbot/explain/', views.chatbot_explain_sign,     name='chatbot-explain'),
]

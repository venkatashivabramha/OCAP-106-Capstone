"""
Contacts URL patterns
"""
from django.urls import path
from .views import ContactListView, ContactDetailView, ContactSearchView

urlpatterns = [
    path('', ContactListView.as_view(), name='contact-list'),
    path('<uuid:contact_id>/', ContactDetailView.as_view(), name='contact-detail'),
    path('search/', ContactSearchView.as_view(), name='contact-search'),
]

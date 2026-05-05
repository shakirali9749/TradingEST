from django.urls import path

from . import views

app_name = "transactions"

urlpatterns = [
    path("", views.TransactionListView.as_view(), name="list"),
    path("<int:pk>/", views.TransactionDetailView.as_view(), name="detail"),
    path("add/", views.TransactionCreateView.as_view(), name="add"),
    path("<int:pk>/edit/", views.TransactionUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.TransactionDeleteView.as_view(), name="delete"),
    path("legacy/", views.LegacyPayableListView.as_view(), name="legacy_list"),
    path("legacy/add/", views.LegacyPayableCreateView.as_view(), name="legacy_add"),
    path("legacy/<int:pk>/edit/", views.LegacyPayableUpdateView.as_view(), name="legacy_edit"),
    path("legacy/<int:pk>/delete/", views.LegacyPayableDeleteView.as_view(), name="legacy_delete"),
]

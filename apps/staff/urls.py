from django.urls import path

from apps.staff.views import wish_views

app_name = "staff"

urlpatterns = [
    # Wish management URLs
    path("wishes/", wish_views.WishListView.as_view(), name="wish-list"),
    path("wishes/create/", wish_views.WishCreateView.as_view(), name="wish-create"),
    path("wishes/<int:pk>/", wish_views.WishDetailView.as_view(), name="wish-detail"),
    path(
        "wishes/<int:pk>/update/",
        wish_views.WishUpdateView.as_view(),
        name="wish-update",
    ),
    path(
        "wishes/<int:pk>/delete/",
        wish_views.WishDeleteView.as_view(),
        name="wish-delete",
    ),
    path(
        "wishes/<int:pk>/delete-modal/",
        wish_views.WishDeleteModalView.as_view(),
        name="wish-delete-modal",
    ),
    path(
        "wishes/<int:pk>/complete/",
        wish_views.WishCompleteView.as_view(),
        name="wish-complete",
    ),
]

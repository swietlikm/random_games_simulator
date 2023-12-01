from django.urls import path

from .views import (
    ClearUserNumbersView,
    LottoGameCreateView,
    LottoGameDeleteView,
    LottoGameDetailsView,
    LottoGameUpdateView,
    LottoHomePageView,
    RandomLottoView,
)

app_name = "lotto"

urlpatterns = [
    path("", view=LottoHomePageView.as_view(), name="index"),
    path("create/", view=LottoGameCreateView.as_view(), name="create"),
    path("<int:pk>/", view=LottoGameDetailsView.as_view(), name="details"),
    path("<int:pk>/update/", view=LottoGameUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", view=LottoGameDeleteView.as_view(), name="delete"),
    path("<int:pk>/clear/", view=ClearUserNumbersView.as_view(), name="clear"),
    path("<int:pk>/random/", view=RandomLottoView.as_view(), name="random"),
]

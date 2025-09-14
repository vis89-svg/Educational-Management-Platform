from django.urls import path
from .views import ResultEntryView, ResultView

urlpatterns = [
    path("entry/", ResultEntryView.as_view(), name="results-entry"),
    path("view/", ResultView.as_view(), name="results-view"),
]

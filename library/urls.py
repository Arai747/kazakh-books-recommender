
from django.urls import path
from .views import book_list, reading_list, recommendations

urlpatterns = [
    path("books/", book_list, name="book_list"),
    path("reading-list/", reading_list, name="reading_list"),
    path(
        "recommendations/",
        recommendations,
        name="recommendations"
    ),
]

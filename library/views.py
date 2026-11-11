
from django.http import JsonResponse
from .models import Book


def book_list(request):
    books = Book.objects.all()

    genre = request.GET.get("genre")
    author = request.GET.get("author")
    max_pages = request.GET.get("max_pages")

    if genre:
        books = books.filter(genre__icontains=genre)

    if author:
        books = books.filter(author__icontains=author)

    if max_pages:
        try:
            max_pages = int(max_pages)
            if max_pages < 0:
                raise ValueError
        except ValueError:
            return JsonResponse(
                {"error": "max_pages оң сан болуы керек"},
                status=400
            )

        books = books.filter(pages__lte=max_pages)

    results = list(
        books.values(
            "id", "title", "author",
            "genre", "description", "pages"
        )
    )

    return JsonResponse(
        {"count": len(results), "books": results}
    )

import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import ReadingList


@login_required
@require_http_methods(["GET", "POST", "DELETE"])
def reading_list(request):
    user = request.user

    if request.method == "GET":
        items = ReadingList.objects.filter(
            user=user
        ).select_related("book")

        books = [
            {
                "id": item.book.id,
                "title": item.book.title,
                "author": item.book.author,
                "genre": item.book.genre,
                "pages": item.book.pages,
            }
            for item in items
        ]

        return JsonResponse({
            "count": len(books),
            "books": books
        })

    try:
        data = json.loads(request.body)
        book_id = data.get("book_id")
        book_id = int(book_id)
        if book_id <= 0:
            raise ValueError
    except (ValueError, TypeError, AttributeError):
        return JsonResponse(
            {"error": "Дұрыс book_id енгізіңіз"},
            status=400
        )

    if request.method == "POST":
        from .models import Book

        if not Book.objects.filter(id=book_id).exists():
            return JsonResponse(
                {"error": "Кітап табылмады"},
                status=404
            )

        item, created = ReadingList.objects.get_or_create(
            user=user,
            book_id=book_id
        )

        return JsonResponse({
            "message": "Кітап тізімге қосылды" if created
                       else "Кітап тізімде бұрыннан бар",
            "book_id": book_id
        })

    deleted, _ = ReadingList.objects.filter(
        user=user,
        book_id=book_id
    ).delete()

    if not deleted:
        return JsonResponse(
            {"error": "Кітап оқу тізімінен табылмады"},
            status=404
        )

    return JsonResponse({
        "message": "Кітап тізімнен өшірілді"
    })

@require_http_methods(["GET"])
def recommendations(request):
    return JsonResponse(
        {
            "status": "model_not_connected",
            "message": "ML моделі әлі қосылмаған",
            "books": []
        },
        status=503
    )

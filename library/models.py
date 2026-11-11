from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name="Кітап атауы")
    author = models.CharField(max_length=150, verbose_name="Автор")
    description = models.TextField(verbose_name="Кітап сипаттамасы")
    genre = models.CharField(max_length=100, verbose_name="Жанр")
    cover = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    pages = models.PositiveIntegerField(
        verbose_name="Бет саны",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title


from django.conf import settings


class ReadingList(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reading_list"
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE
    )

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"],
                name="unique_user_book"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

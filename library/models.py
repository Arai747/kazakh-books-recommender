from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name="Кітап атауы")
    author = models.CharField(max_length=150, verbose_name="Автор")
    description = models.TextField(verbose_name="Кітап сипаттамасы")
    genre = models.CharField(max_length=100, verbose_name="Жанр")
    cover = models.ImageField(upload_to='book_covers/', blank=True, null=True)

    def __str__(self):
        return self.title
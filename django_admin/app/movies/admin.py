from django.contrib import admin

from .models import Filmwork, Genre, GenreFilmwork, Person, PersonFilmwork, Files


# Register your models here.
class GenreFilworkInline(admin.TabularInline):
    model = GenreFilmwork


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("full_name",)
    search_fields = ("full_name",)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)
    pass


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilworkInline, PersonFilmworkInline)
    list_filter = ("type",)
    search_fields = ("title", "description", "id")
    list_display = ("title", "type", "creation_date", "rating", "file")


@admin.register(Files)
class FilesAdmin(admin.ModelAdmin):
    search_fields = ("filename", "file_type", "id")
    list_display = ("filename", "size", "file_type", "short_name")

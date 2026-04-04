from django.urls import path

from .views import bookmarks_page, home, lessons_page, search_results, topic_detail


urlpatterns = [
    path("", home, name="home"),
    path("bookmarks/", bookmarks_page, name="bookmarks"),
    path("lessons/", lessons_page, name="lessons"),
    path("search/", search_results, name="search-results"),
    path("topic/<slug:topic_name>/", topic_detail, name="topic-detail"),
]

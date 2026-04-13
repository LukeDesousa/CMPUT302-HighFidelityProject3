from django.urls import path

from .views import (
    browse_topics_page,
    collections_page,
    home,
    research_page,
    search_results,
    topic_detail,
)


urlpatterns = [
    path("", home, name="home"),
    path("collections/", collections_page, name="collections"),
    path("research/", research_page, name="research"),
    path("search/", search_results, name="search-results"),
    path("topics/", browse_topics_page, name="browse-topics"),
    path("topic/<slug:topic_name>/", topic_detail, name="topic-detail"),
]

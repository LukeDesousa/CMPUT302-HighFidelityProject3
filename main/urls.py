from django.urls import path

from .views import (
    browse_topics_page,
    collections_page,
    create_collection_page,
    home,
    research_page,
    search_results,
    select_collection_page,
    topic_detail,
)


urlpatterns = [
    path("", home, name="home"),
    path("collections/", collections_page, name="collections"),
    path("collections/create/", create_collection_page, name="create-collection"),
    path("collections/select/", select_collection_page, name="select-collection"),
    path("research/", research_page, name="research"),
    path("search/", search_results, name="search-results"),
    path("topics/", browse_topics_page, name="browse-topics"),
    path("topic/<slug:topic_name>/", topic_detail, name="topic-detail"),
]

from urllib.parse import urlencode

from django.shortcuts import redirect, render
from django.urls import reverse


MODES = ("Teacher", "Standard", "Research")
DEFAULT_MODE = "Teacher"
TOPICS = (
    {
        "name": "Family",
        "slug": "family",
        "summary": "Words for people close to home.",
        "words": ("mother", "father", "baby", "grandmother"),
    },
    {
        "name": "Sports",
        "slug": "sports",
        "summary": "Words for games and movement.",
        "words": ("hockey", "soccer", "skate", "goal"),
    },
    {
        "name": "Seasons",
        "slug": "seasons",
        "summary": "Season words you can browse from the home page.",
        "words": ("spring", "summer", "autumn", "winter"),
    },
    {
        "name": "Nouns",
        "slug": "nouns",
        "summary": "Starter nouns to browse and explore.",
        "words": ("house", "book", "water", "sun"),
    },
    {
        "name": "Verbs",
        "slug": "verbs",
        "summary": "Common action words.",
        "words": ("run", "eat", "sleep", "sing"),
    },
    {
        "name": "Fruits",
        "slug": "fruits",
        "summary": "Fruit words grouped into one browseable topic.",
        "words": ("apple", "berry", "orange", "grape"),
    },
    {
        "name": "Animals",
        "slug": "animals",
        "summary": "Animal words with Cree translations.",
        "words": ("horse", "rabbit", "dog", "bear", "moose"),
    },
)

TOPIC_LOOKUP = {topic["slug"]: topic for topic in TOPICS}

WORD_LIBRARY = {
    "mother": {"english_word": "mother", "topic": "family"},
    "father": {"english_word": "father", "topic": "family"},
    "baby": {"english_word": "baby", "topic": "family"},
    "grandmother": {"english_word": "grandmother", "topic": "family"},
    "hockey": {"english_word": "hockey", "topic": "sports"},
    "soccer": {"english_word": "soccer", "topic": "sports"},
    "skate": {"english_word": "skate", "topic": "sports"},
    "goal": {"english_word": "goal", "topic": "sports"},
    "spring": {"english_word": "spring", "topic": "seasons"},
    "summer": {"english_word": "summer", "topic": "seasons"},
    "autumn": {"english_word": "autumn", "topic": "seasons"},
    "winter": {"english_word": "winter", "topic": "seasons"},
    "house": {"english_word": "house", "topic": "nouns"},
    "book": {"english_word": "book", "topic": "nouns"},
    "water": {"english_word": "water", "topic": "nouns"},
    "sun": {"english_word": "sun", "topic": "nouns"},
    "run": {"english_word": "run", "topic": "verbs"},
    "eat": {"english_word": "eat", "topic": "verbs"},
    "sleep": {"english_word": "sleep", "topic": "verbs"},
    "sing": {"english_word": "sing", "topic": "verbs"},
    "apple": {"english_word": "apple", "topic": "fruits"},
    "berry": {"english_word": "berry", "topic": "fruits"},
    "orange": {"english_word": "orange", "topic": "fruits"},
    "grape": {"english_word": "grape", "topic": "fruits"},
    "horse": {
        "english_word": "horse",
        "topic": "animals",
        "cree_translation": "mistatim",
        "cree_label": "Plains Cree",
    },
    "rabbit": {
        "english_word": "rabbit",
        "topic": "animals",
        "cree_translation": "wâpos",
        "cree_label": "Plains Cree",
    },
    "dog": {
        "english_word": "dog",
        "topic": "animals",
        "cree_translation": "atim",
        "cree_label": "Plains Cree",
    },
    "bear": {
        "english_word": "bear",
        "topic": "animals",
        "cree_translation": "maskwa",
        "cree_label": "Plains Cree",
    },
    "moose": {
        "english_word": "moose",
        "topic": "animals",
        "cree_translation": "môswa",
        "cree_label": "Plains Cree",
    },
}

RECENT_SEARCHES = ("horse", "rabbit", "apple", "winter")
GRAPH_NODE_SLOTS = (
    (22, 18, "topic"),
    (78, 18, "translation"),
    (16, 58, "related"),
    (34, 82, "related"),
    (66, 82, "related"),
    (84, 58, "related"),
)


def build_url(route_name, *, args=None, params=None):
    url = reverse(route_name, args=args or [])
    cleaned_params = {
        key: value
        for key, value in (params or {}).items()
        if value not in (None, "")
    }
    if cleaned_params:
        return f"{url}?{urlencode(cleaned_params)}"
    return url


def get_current_mode(request):
    requested_mode = (
        request.POST.get("mode")
        or request.GET.get("mode")
        or DEFAULT_MODE
    )
    return requested_mode if requested_mode in MODES else DEFAULT_MODE


def get_safe_back_url(raw_back_url, fallback_url):
    if raw_back_url and raw_back_url.startswith("/"):
        return raw_back_url
    return fallback_url


def get_word_route_name(current_mode):
    return "research" if current_mode == "Research" else "search-results"


def build_word_lookup_url(search_query, current_mode, back_url):
    normalized_query = (search_query or "horse").strip() or "horse"
    return build_url(
        get_word_route_name(current_mode),
        params={
            "q": normalized_query,
            "mode": current_mode,
            "back": back_url,
        },
    )


def get_bookmarks(request):
    bookmarks = request.session.get("bookmarks", [])
    return [word for word in bookmarks if word in WORD_LIBRARY]


def save_bookmarks(request, bookmarks):
    request.session["bookmarks"] = bookmarks


def get_lessons(request):
    lessons = request.session.get("lessons", [])
    return [lesson for lesson in lessons if lesson.get("name")]


def save_lessons(request, lessons):
    request.session["lessons"] = lessons


def build_word_result(word_key):
    entry = WORD_LIBRARY[word_key]
    topic = TOPIC_LOOKUP[entry["topic"]]
    related_words = []

    for related_key in topic["words"]:
        if related_key == word_key:
            continue

        related_entry = WORD_LIBRARY[related_key]
        related_words.append(
            {
                "english": related_entry["english_word"],
                "cree": related_entry.get("cree_translation"),
            }
        )

    return {
        "english_word": entry["english_word"],
        "topic_slug": topic["slug"],
        "topic_name": topic["name"],
        "cree_translation": entry.get("cree_translation"),
        "cree_label": entry.get("cree_label", "Cree"),
        "has_translation": bool(entry.get("cree_translation")),
        "related_words": related_words,
    }


def build_bookmark_results(request):
    return [build_word_result(word) for word in get_bookmarks(request)]


def build_lessons_context(request, current_word=None):
    lessons_context = []
    for lesson in get_lessons(request):
        lesson_words = [
            build_word_result(word)
            for word in lesson.get("words", [])
            if word in WORD_LIBRARY
        ]
        lessons_context.append(
            {
                "name": lesson["name"],
                "words": lesson_words,
                "word_count": len(lesson_words),
                "contains_current": current_word in lesson.get("words", []),
            }
        )
    return lessons_context


def build_graph_data(result):
    nodes = [
        {
            "label": result["english_word"].title(),
            "meta": "Search Word",
            "x": 50,
            "y": 50,
            "kind": "center",
        }
    ]
    lines = []
    graph_items = [{"label": result["topic_name"], "meta": "Topic"}]

    if result["has_translation"]:
        graph_items.append(
            {
                "label": result["cree_translation"],
                "meta": result["cree_label"],
            }
        )

    for related_word in result["related_words"][:4]:
        graph_items.append(
            {
                "label": related_word["english"].title(),
                "meta": related_word["cree"] or "Related Word",
            }
        )

    for item, (x, y, kind) in zip(graph_items, GRAPH_NODE_SLOTS):
        nodes.append(
            {
                "label": item["label"],
                "meta": item["meta"],
                "x": x,
                "y": y,
                "kind": kind,
            }
        )
        lines.append(
            {
                "x1": 50,
                "y1": 50,
                "x2": x,
                "y2": y,
            }
        )

    return {
        "nodes": nodes,
        "lines": lines,
    }


def handle_search_actions(request, current_mode, word_key, back_url):
    action = request.POST.get("action", "").strip()

    if current_mode == "Standard" and action == "toggle_bookmark" and word_key in WORD_LIBRARY:
        bookmarks = get_bookmarks(request)
        if word_key in bookmarks:
            bookmarks = [bookmark for bookmark in bookmarks if bookmark != word_key]
        else:
            bookmarks = [word_key, *[bookmark for bookmark in bookmarks if bookmark != word_key]]
        save_bookmarks(request, bookmarks)

    return redirect(build_word_lookup_url(request.POST.get("q", word_key or "horse"), current_mode, back_url))


def handle_bookmark_actions(request, current_mode, back_url):
    action = request.POST.get("action", "").strip()
    word_key = request.POST.get("word", "").strip().lower()

    if action == "remove_bookmark" and word_key in WORD_LIBRARY:
        bookmarks = [bookmark for bookmark in get_bookmarks(request) if bookmark != word_key]
        save_bookmarks(request, bookmarks)

    return redirect(
        build_url(
            "bookmarks",
            params={
                "mode": current_mode,
                "back": back_url,
            },
        )
    )


def handle_lesson_actions(request, current_mode, selected_word, back_url):
    action = request.POST.get("action", "").strip()
    lessons = get_lessons(request)

    if action == "create_lesson":
        lesson_name = request.POST.get("lesson_name", "").strip()
        if lesson_name and all(lesson["name"].lower() != lesson_name.lower() for lesson in lessons):
            lessons.append({"name": lesson_name, "words": []})
            save_lessons(request, lessons)

    if action == "add_to_lesson" and selected_word in WORD_LIBRARY:
        lesson_name = request.POST.get("lesson_name", "").strip()
        updated_lessons = []
        for lesson in lessons:
            if lesson["name"] == lesson_name and selected_word not in lesson.get("words", []):
                updated_lessons.append(
                    {
                        "name": lesson["name"],
                        "words": [*lesson.get("words", []), selected_word],
                    }
                )
            else:
                updated_lessons.append(lesson)
        save_lessons(request, updated_lessons)

    return redirect(
        build_url(
            "lessons",
            params={
                "mode": current_mode,
                "word": selected_word,
                "back": back_url,
            },
        )
    )


def home(request):
    current_mode = get_current_mode(request)
    home_back_url = request.get_full_path()

    context = {
        "current_mode": current_mode,
        "modes": MODES,
        "search_route_name": get_word_route_name(current_mode),
        "recent_searches": RECENT_SEARCHES,
        "topics": TOPICS,
        "bookmark_count": len(get_bookmarks(request)),
        "lesson_count": len(get_lessons(request)),
        "research_sample_url": build_word_lookup_url("horse", "Research", home_back_url),
        "bookmarks_url": build_url(
            "bookmarks",
            params={
                "mode": current_mode,
                "back": home_back_url,
            },
        ),
        "lessons_url": build_url(
            "lessons",
            params={
                "mode": current_mode,
                "back": home_back_url,
            },
        ),
    }
    return render(request, "home.html", context)


def search_results(request):
    current_mode = get_current_mode(request)
    fallback_back_url = build_url("home", params={"mode": current_mode})
    back_url = get_safe_back_url(
        request.POST.get("back") or request.GET.get("back"),
        fallback_back_url,
    )
    raw_query = (request.POST.get("q") if request.method == "POST" else request.GET.get("q", "horse")) or "horse"
    search_query = raw_query.strip() or "horse"
    normalized_query = search_query.lower()

    if request.method == "POST":
        return handle_search_actions(request, current_mode, normalized_query, back_url)

    if current_mode == "Research":
        return redirect(build_word_lookup_url(search_query, current_mode, back_url))

    result = build_word_result(normalized_query) if normalized_query in WORD_LIBRARY else None
    bookmarks = get_bookmarks(request)

    if result is not None:
        result["is_bookmarked"] = normalized_query in bookmarks

    current_page_url = build_url(
        "search-results",
        params={
            "q": search_query,
            "mode": current_mode,
            "back": back_url,
        },
    )

    context = {
        "current_mode": current_mode,
        "modes": MODES,
        "search_route_name": get_word_route_name(current_mode),
        "search_query": search_query,
        "result": result,
        "back_url": back_url,
        "research_url": build_word_lookup_url(search_query, "Research", current_page_url),
        "suggested_words": [WORD_LIBRARY[word]["english_word"] for word in RECENT_SEARCHES],
        "bookmarks_url": build_url(
            "bookmarks",
            params={
                "mode": current_mode,
                "back": current_page_url,
            },
        ),
        "lessons_url": build_url(
            "lessons",
            params={
                "mode": current_mode,
                "word": normalized_query if result else None,
                "back": current_page_url,
            },
        ),
    }
    return render(request, "search_results.html", context)


def research_page(request):
    requested_mode = request.GET.get("mode") or "Research"
    current_mode = requested_mode if requested_mode in MODES else "Research"
    fallback_back_url = build_url("home", params={"mode": "Research"})
    back_url = get_safe_back_url(request.GET.get("back"), fallback_back_url)
    search_query = (request.GET.get("q", "horse") or "horse").strip() or "horse"

    if current_mode != "Research":
        return redirect(build_word_lookup_url(search_query, current_mode, back_url))

    normalized_query = search_query.lower()
    result = build_word_result(normalized_query) if normalized_query in WORD_LIBRARY else None
    current_page_url = build_word_lookup_url(search_query, current_mode, back_url)

    return render(
        request,
        "research.html",
        {
            "current_mode": current_mode,
            "modes": MODES,
            "search_query": search_query,
            "result": result,
            "back_url": back_url,
            "current_page_url": current_page_url,
            "research_graph": build_graph_data(result) if result else None,
            "suggested_words": [WORD_LIBRARY[word]["english_word"] for word in RECENT_SEARCHES],
        },
    )


def bookmarks_page(request):
    current_mode = get_current_mode(request)
    fallback_back_url = build_url("home", params={"mode": current_mode})
    back_url = get_safe_back_url(
        request.POST.get("back") or request.GET.get("back"),
        fallback_back_url,
    )

    if request.method == "POST":
        return handle_bookmark_actions(request, current_mode, back_url)

    return render(
        request,
        "bookmarks.html",
        {
            "current_mode": current_mode,
            "modes": MODES,
            "search_route_name": get_word_route_name(current_mode),
            "back_url": back_url,
            "bookmarks": build_bookmark_results(request),
        },
    )


def lessons_page(request):
    current_mode = get_current_mode(request)
    fallback_back_url = build_url("home", params={"mode": current_mode})
    back_url = get_safe_back_url(
        request.POST.get("back") or request.GET.get("back"),
        fallback_back_url,
    )
    selected_word = (
        request.POST.get("word")
        or request.GET.get("word")
        or ""
    ).strip().lower()
    selected_word = selected_word if selected_word in WORD_LIBRARY else None

    if request.method == "POST":
        return handle_lesson_actions(request, current_mode, selected_word, back_url)

    return render(
        request,
        "lessons.html",
        {
            "current_mode": current_mode,
            "modes": MODES,
            "search_route_name": get_word_route_name(current_mode),
            "back_url": back_url,
            "selected_word": selected_word,
            "selected_result": build_word_result(selected_word) if selected_word else None,
            "lessons": build_lessons_context(request, current_word=selected_word),
        },
    )


def topic_detail(request, topic_name):
    current_mode = get_current_mode(request)
    fallback_back_url = build_url("home", params={"mode": current_mode})
    back_url = get_safe_back_url(request.GET.get("back"), fallback_back_url)
    topic = TOPIC_LOOKUP.get(topic_name)

    if topic is None:
        return render(
            request,
            "topic_detail.html",
            {
                "current_mode": current_mode,
                "modes": MODES,
                "search_route_name": get_word_route_name(current_mode),
                "topic_exists": False,
                "topic_label": topic_name.replace("-", " ").title(),
                "back_url": back_url,
                "research_sample_url": build_word_lookup_url("horse", "Research", back_url),
            },
        )

    topic_words = [build_word_result(word) for word in topic["words"]]

    return render(
        request,
        "topic_detail.html",
        {
            "current_mode": current_mode,
            "modes": MODES,
            "search_route_name": get_word_route_name(current_mode),
            "topic_exists": True,
            "topic": topic,
            "topic_words": topic_words,
            "back_url": back_url,
            "research_sample_url": build_word_lookup_url(topic["words"][0], "Research", back_url),
        },
    )

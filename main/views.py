import json
from math import cos, radians, sin
from urllib.parse import urlencode

from django.shortcuts import redirect, render
from django.urls import reverse


MODES = ("Teacher", "Standard", "Research")
DEFAULT_MODE = "Teacher"
SEARCH_TYPES = ("word", "category")
DEFAULT_SEARCH_TYPE = "word"
TOPIC_VIEWS = ("list", "map")
HOME_TOPIC_LIMIT = 6
MODE_DETAILS = {
    "Teacher": "Build lessons, add notes, and collect words for class use.",
    "Standard": "Save useful words to a quick review list for later.",
    "Research": "Inspect a word through connected meanings and topic maps.",
}
SEARCH_TYPE_DETAILS = {
    "word": {
        "label": "Word Search",
        "option_label": "Word Search: specific word",
        "description": "Look up a specific word to view its translation and related words.",
        "placeholder": "Search a word...",
    },
    "category": {
        "label": "Category Search",
        "option_label": "Category Search: topic groups",
        "description": "Find categories like animals, seasons, or family before opening a topic.",
        "placeholder": "Search a word category...",
    },
}
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
        "syllabics": "ᒥᐢᑕᑎᒼ",
        "word_class": "NA",
        "dictionary_note": "Animate noun. Dictionary note: horse, plural =wak; alternate spelling misatim appears in some entries.",
        "research_source": "Online Cree Dictionary",
    },
    "rabbit": {
        "english_word": "rabbit",
        "topic": "animals",
        "cree_translation": "wâpos",
        "cree_label": "Plains Cree",
        "syllabics": "ᐚᐳᐢ",
        "word_class": "NA",
        "dictionary_note": "Animate noun. Dictionary note: rabbit or hare, plural =wak.",
        "research_source": "Online Cree Dictionary",
    },
    "dog": {
        "english_word": "dog",
        "topic": "animals",
        "cree_translation": "atim",
        "cree_label": "Plains Cree",
        "syllabics": "ᐊᑎᒼ",
        "word_class": "NA",
        "dictionary_note": "Animate noun. Dictionary note: dog; horse; beast of burden.",
        "research_source": "Online Cree Dictionary",
    },
    "bear": {
        "english_word": "bear",
        "topic": "animals",
        "cree_translation": "maskwa",
        "cree_label": "Plains Cree",
        "syllabics": "ᒪᐢᑿ",
        "word_class": "NA",
        "dictionary_note": "Animate noun. Dictionary note: bear, possessive stem =maskom-, plural =wak.",
        "research_source": "Online Cree Dictionary",
    },
    "moose": {
        "english_word": "moose",
        "topic": "animals",
        "cree_translation": "môswa",
        "cree_label": "Plains Cree",
        "syllabics": "ᒨᐢᐘ",
        "word_class": "NA",
        "dictionary_note": "Animate noun. Dictionary note: moose, plural =k.",
        "research_source": "Online Cree Dictionary",
    },
}

RECENT_SEARCHES = ("horse", "rabbit", "apple", "winter")
GRAPH_NODE_SLOTS = (
    (26, 22, "topic"),
    (74, 22, "translation"),
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


def get_current_search_type(request, default=DEFAULT_SEARCH_TYPE):
    requested_search_type = (
        request.POST.get("search_type")
        or request.GET.get("search_type")
        or default
    )
    return requested_search_type if requested_search_type in SEARCH_TYPES else default


def get_safe_back_url(raw_back_url, fallback_url):
    if raw_back_url and raw_back_url.startswith("/"):
        return raw_back_url
    return fallback_url


def get_topic_view(request):
    requested_view = request.GET.get("view") or "list"
    return requested_view if requested_view in TOPIC_VIEWS else "list"


def get_word_route_name(current_mode):
    return "research" if current_mode == "Research" else "search-results"


def build_word_lookup_url(search_query, current_mode, back_url, search_type=DEFAULT_SEARCH_TYPE):
    normalized_query = (search_query or "horse").strip() or "horse"
    return build_url(
        get_word_route_name(current_mode),
        params={
            "q": normalized_query,
            "mode": current_mode,
            "back": back_url,
            "search_type": search_type,
        },
    )


def build_browse_topics_url(current_mode, back_url, search_query="", search_type="category"):
    return build_url(
        "browse-topics",
        params={
            "q": search_query,
            "mode": current_mode,
            "back": back_url,
            "search_type": search_type,
        },
    )


def build_topic_detail_url(topic_slug, current_mode, back_url, topic_view=None, search_type=None):
    return build_url(
        "topic-detail",
        args=[topic_slug],
        params={
            "mode": current_mode,
            "back": back_url,
            "view": topic_view,
            "search_type": search_type,
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


def set_toast(request, message, kind="success"):
    request.session["toast"] = {
        "message": message,
        "kind": kind,
    }


def pop_toast(request):
    toast = request.session.pop("toast", None)
    if not toast:
        return None
    if isinstance(toast, dict) and toast.get("message"):
        return toast
    return None


def build_mode_options(current_mode):
    return [
        {
            "value": mode,
            "description": MODE_DETAILS[mode],
            "is_current": mode == current_mode,
        }
        for mode in MODES
    ]


def build_search_type_options(current_search_type):
    return [
        {
            "value": search_type,
            "label": SEARCH_TYPE_DETAILS[search_type]["label"],
            "option_label": SEARCH_TYPE_DETAILS[search_type]["option_label"],
            "description": SEARCH_TYPE_DETAILS[search_type]["description"],
            "placeholder": SEARCH_TYPE_DETAILS[search_type]["placeholder"],
            "is_current": search_type == current_search_type,
        }
        for search_type in SEARCH_TYPES
    ]


def build_search_suggestions(current_mode, back_url):
    suggestions = []

    for word_key in sorted(WORD_LIBRARY):
        entry = WORD_LIBRARY[word_key]
        topic = TOPIC_LOOKUP[entry["topic"]]
        searchable_terms = [
            entry["english_word"],
            topic["name"],
            topic["slug"],
        ]
        if entry.get("cree_translation"):
            searchable_terms.append(entry["cree_translation"])

        suggestions.append(
            {
                "label": entry["english_word"].title(),
                "kind": "Word",
                "meta": entry.get("cree_translation") or topic["name"],
                "keywords": " ".join(searchable_terms).lower(),
                "url": build_word_lookup_url(entry["english_word"], current_mode, back_url),
            }
        )

    for topic in TOPICS:
        suggestions.append(
            {
                "label": topic["name"],
                "kind": "Category",
                "meta": f"{len(topic['words'])} words",
                "keywords": " ".join([topic["name"], topic["slug"], topic["summary"], *topic["words"]]).lower(),
                "url": build_topic_detail_url(topic["slug"], current_mode, back_url),
            }
        )

    return suggestions


def build_lesson_word_suggestions(current_mode, back_url):
    suggestions = []

    for word_key in sorted(WORD_LIBRARY):
        entry = WORD_LIBRARY[word_key]
        topic = TOPIC_LOOKUP[entry["topic"]]
        searchable_terms = [
            entry["english_word"],
            topic["name"],
            topic["slug"],
        ]
        if entry.get("cree_translation"):
            searchable_terms.append(entry["cree_translation"])

        suggestions.append(
            {
                "label": entry["english_word"].title(),
                "kind": "Word",
                "meta": entry.get("cree_translation") or topic["name"],
                "keywords": " ".join(searchable_terms).lower(),
                "url": build_url(
                    "lessons",
                    params={
                        "mode": current_mode,
                        "word": entry["english_word"],
                        "back": back_url,
                    },
                ),
            }
        )

    return suggestions


def build_shared_context(request, current_mode, search_type):
    return {
        "modes": MODES,
        "mode_options": build_mode_options(current_mode),
        "current_search_type": search_type,
        "search_types": build_search_type_options(search_type),
        "search_placeholder": SEARCH_TYPE_DETAILS[search_type]["placeholder"],
        "search_helper_text": SEARCH_TYPE_DETAILS[search_type]["description"],
        "search_route_name": get_word_route_name(current_mode),
        "search_word_action": reverse(get_word_route_name(current_mode)),
        "search_category_action": reverse("browse-topics"),
        "toast": pop_toast(request),
    }


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
        "syllabics": entry.get("syllabics"),
        "word_class": entry.get("word_class"),
        "dictionary_note": entry.get("dictionary_note"),
        "research_source": entry.get("research_source"),
        "has_translation": bool(entry.get("cree_translation")),
        "has_research_details": bool(
            entry.get("syllabics")
            or entry.get("word_class")
            or entry.get("dictionary_note")
            or entry.get("research_source")
        ),
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
                "notes": (lesson.get("notes") or "").strip(),
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
    semantic_nodes = [
        {
            "label": result["topic_name"],
            "meta": "Topic",
            "x": GRAPH_NODE_SLOTS[0][0],
            "y": GRAPH_NODE_SLOTS[0][1],
            "kind": GRAPH_NODE_SLOTS[0][2],
        }
    ]

    if result["has_translation"]:
        semantic_nodes.append(
            {
                "label": result["cree_translation"],
                "meta": result["cree_label"],
                "x": GRAPH_NODE_SLOTS[1][0],
                "y": GRAPH_NODE_SLOTS[1][1],
                "kind": GRAPH_NODE_SLOTS[1][2],
            }
        )

    related_positions = {
        1: ((50, 82),),
        2: ((28, 80), (72, 80)),
        3: ((18, 66), (50, 84), (82, 66)),
        4: ((14, 58), (34, 84), (66, 84), (86, 58)),
    }

    for related_word, (x, y) in zip(
        result["related_words"][:4],
        related_positions.get(len(result["related_words"][:4]), ()),
    ):
        semantic_nodes.append(
            {
                "label": related_word["english"].title(),
                "meta": related_word["cree"] or "Related Word",
                "x": x,
                "y": y,
                "kind": "related",
            }
        )

    for node in semantic_nodes:
        nodes.append(node)
        lines.append(
            {
                "x1": 50,
                "y1": 50,
                "x2": node["x"],
                "y2": node["y"],
            }
        )

    return {
        "nodes": nodes,
        "lines": lines,
    }


def build_topic_graph_data(topic, current_mode, back_url):
    nodes = [
        {
            "label": topic["name"],
            "meta": f"{len(topic['words'])} words",
            "x": 50,
            "y": 50,
            "kind": "center",
        }
    ]
    lines = []
    word_count = len(topic["words"])
    radius_x = 34 if word_count <= 4 else 36
    radius_y = 28 if word_count <= 4 else 30

    ring_positions = []
    for index in range(word_count):
        angle = radians(-90 + (360 / word_count) * index)
        ring_positions.append(
            (
                round(50 + radius_x * cos(angle), 2),
                round(50 + radius_y * sin(angle), 2),
            )
        )

    for word_key, (x, y) in zip(topic["words"], ring_positions):
        word_result = build_word_result(word_key)
        nodes.append(
            {
                "label": word_result["english_word"].title(),
                "meta": word_result["cree_translation"] or "Open word",
                "x": x,
                "y": y,
                "kind": "related",
                "url": build_word_lookup_url(word_result["english_word"], current_mode, back_url),
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


def build_topic_cards(current_mode, back_url, topics=None, search_type=None):
    topic_cards = []
    for topic in topics or TOPICS:
        topic_cards.append(
            {
                "name": topic["name"],
                "slug": topic["slug"],
                "summary": topic["summary"],
                "word_count": len(topic["words"]),
                "preview_words": [
                    WORD_LIBRARY[word]["english_word"].title()
                    for word in topic["words"][:3]
                ],
                "url": build_topic_detail_url(
                    topic["slug"],
                    current_mode,
                    back_url,
                    search_type=search_type,
                ),
            }
        )
    return topic_cards


def filter_topics(search_query):
    normalized_query = (search_query or "").strip().lower()
    if not normalized_query:
        return TOPICS

    filtered_topics = []
    for topic in TOPICS:
        searchable_parts = (
            topic["name"],
            topic["summary"],
            *topic["words"],
        )
        if any(normalized_query in part.lower() for part in searchable_parts):
            filtered_topics.append(topic)

    return filtered_topics


def find_exact_topic_match(search_query):
    normalized_query = (search_query or "").strip().lower()
    if not normalized_query:
        return None

    for topic in TOPICS:
        if normalized_query in (topic["slug"].lower(), topic["name"].lower()):
            return topic

    return None


def add_word_to_lessons(lessons, lesson_name, selected_word):
    updated_lessons = []
    for lesson in lessons:
        if lesson["name"] == lesson_name and selected_word in WORD_LIBRARY:
            existing_words = lesson.get("words", [])
            updated_lesson = dict(lesson)
            updated_lesson["words"] = (
                existing_words
                if selected_word in existing_words
                else [*existing_words, selected_word]
            )
            updated_lessons.append(updated_lesson)
            continue

        updated_lessons.append(lesson)

    return updated_lessons


def lesson_name_is_available(lessons, lesson_name):
    return all(lesson["name"].lower() != lesson_name.lower() for lesson in lessons)


def handle_search_actions(request, current_mode, word_key, back_url):
    action = request.POST.get("action", "").strip()
    search_type = get_current_search_type(request)

    if current_mode == "Standard" and action == "toggle_bookmark" and word_key in WORD_LIBRARY:
        bookmarks = get_bookmarks(request)
        if word_key in bookmarks:
            bookmarks = [bookmark for bookmark in bookmarks if bookmark != word_key]
            set_toast(request, "Word removed from your list")
        else:
            bookmarks = [word_key, *[bookmark for bookmark in bookmarks if bookmark != word_key]]
            set_toast(request, "Word saved to your list")
        save_bookmarks(request, bookmarks)

    if current_mode == "Teacher":
        lessons = get_lessons(request)

        if action in ("create_lesson", "save_lesson"):
            lesson_name = request.POST.get("lesson_name", "").strip()
            lesson_notes = request.POST.get("lesson_notes", "").strip()
            if lesson_name and lesson_name_is_available(lessons, lesson_name):
                lessons.append(
                    {
                        "name": lesson_name,
                        "words": [word_key] if word_key in WORD_LIBRARY else [],
                        "notes": lesson_notes,
                    }
                )
                save_lessons(request, lessons)
                set_toast(request, "Lesson saved")
            elif lesson_name:
                set_toast(request, "Choose a different lesson name", kind="warning")

        if action == "add_to_lesson" and word_key in WORD_LIBRARY:
            lesson_name = request.POST.get("lesson_name", "").strip()
            save_lessons(request, add_word_to_lessons(lessons, lesson_name, word_key))
            set_toast(request, "Word added to lesson")

    return redirect(
        build_word_lookup_url(
            request.POST.get("q", word_key or "horse"),
            current_mode,
            back_url,
            search_type=search_type,
        )
    )


def handle_bookmark_actions(request, current_mode, back_url):
    action = request.POST.get("action", "").strip()
    word_key = request.POST.get("word", "").strip().lower()

    if action == "remove_bookmark" and word_key in WORD_LIBRARY:
        bookmarks = [bookmark for bookmark in get_bookmarks(request) if bookmark != word_key]
        save_bookmarks(request, bookmarks)
        set_toast(request, "Word removed from your list")

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
    redirect_word = selected_word

    if action in ("create_lesson", "save_lesson"):
        lesson_name = request.POST.get("lesson_name", "").strip()
        lesson_notes = request.POST.get("lesson_notes", "").strip()
        if lesson_name and lesson_name_is_available(lessons, lesson_name):
            lessons.append(
                {
                    "name": lesson_name,
                    "words": [selected_word] if selected_word in WORD_LIBRARY else [],
                    "notes": lesson_notes,
                }
            )
            save_lessons(request, lessons)
            set_toast(request, "Lesson saved")
            redirect_word = None
        elif lesson_name:
            set_toast(request, "Choose a different lesson name", kind="warning")

    if action == "add_to_lesson" and selected_word in WORD_LIBRARY:
        lesson_name = request.POST.get("lesson_name", "").strip()
        save_lessons(request, add_word_to_lessons(lessons, lesson_name, selected_word))
        set_toast(request, "Word added to lesson")

    if action == "export_lesson":
        lesson_name = request.POST.get("lesson_name", "").strip()
        if any(lesson["name"] == lesson_name for lesson in lessons):
            set_toast(request, "PDF Export started")

    if action == "delete_lesson":
        lesson_name = request.POST.get("lesson_name", "").strip()
        updated_lessons = [lesson for lesson in lessons if lesson["name"] != lesson_name]
        if len(updated_lessons) != len(lessons):
            save_lessons(request, updated_lessons)
            set_toast(request, "Lesson deleted")

    return redirect(
        build_url(
            "lessons",
            params={
                "mode": current_mode,
                "word": redirect_word,
                "back": back_url,
            },
        )
    )


def home(request):
    current_mode = get_current_mode(request)
    current_search_type = get_current_search_type(request)
    home_back_url = request.get_full_path()
    search_suggestions = build_search_suggestions(current_mode, home_back_url)
    topic_cards = build_topic_cards(
        current_mode,
        home_back_url,
        search_type=current_search_type,
    )

    context = {
        "current_mode": current_mode,
        "search_query": "",
        "recent_searches": RECENT_SEARCHES,
        "featured_topics": topic_cards[:HOME_TOPIC_LIMIT],
        "all_topic_count": len(topic_cards),
        "bookmark_count": len(get_bookmarks(request)),
        "lesson_count": len(get_lessons(request)),
        "research_sample_url": build_word_lookup_url("horse", "Research", home_back_url),
        "browse_topics_url": build_browse_topics_url(current_mode, home_back_url),
        "search_suggestions_json": json.dumps(search_suggestions),
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
    context.update(build_shared_context(request, current_mode, current_search_type))
    return render(request, "home.html", context)


def search_results(request):
    current_mode = get_current_mode(request)
    current_search_type = get_current_search_type(request)
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
        return redirect(
            build_word_lookup_url(
                search_query,
                current_mode,
                back_url,
                search_type=current_search_type,
            )
        )

    topic_match = find_exact_topic_match(search_query)
    if topic_match is not None:
        return redirect(build_topic_detail_url(topic_match["slug"], current_mode, back_url))

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
            "search_type": current_search_type,
        },
    )
    search_suggestions = build_search_suggestions(current_mode, current_page_url)

    context = {
        "current_mode": current_mode,
        "search_query": search_query,
        "result": result,
        "back_url": back_url,
        "current_page_url": current_page_url,
        "search_suggestions_json": json.dumps(search_suggestions),
        "research_url": build_word_lookup_url(
            search_query,
            "Research",
            current_page_url,
            search_type=current_search_type,
        ),
        "suggested_words": [WORD_LIBRARY[word]["english_word"] for word in RECENT_SEARCHES],
        "bookmark_count": len(bookmarks),
        "lesson_count": len(get_lessons(request)),
        "lessons": build_lessons_context(request, current_word=normalized_query if result else None),
        "browse_topics_url": build_browse_topics_url(current_mode, current_page_url),
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
    context.update(build_shared_context(request, current_mode, current_search_type))
    return render(request, "search_results.html", context)


def research_page(request):
    requested_mode = request.GET.get("mode") or "Research"
    current_mode = requested_mode if requested_mode in MODES else "Research"
    current_search_type = get_current_search_type(request)
    fallback_back_url = build_url("home", params={"mode": "Research"})
    back_url = get_safe_back_url(request.GET.get("back"), fallback_back_url)
    search_query = (request.GET.get("q", "horse") or "horse").strip() or "horse"

    if current_mode != "Research":
        return redirect(
            build_word_lookup_url(
                search_query,
                current_mode,
                back_url,
                search_type=current_search_type,
            )
        )

    normalized_query = search_query.lower()
    topic_match = find_exact_topic_match(search_query)
    if topic_match is not None:
        return redirect(build_topic_detail_url(topic_match["slug"], current_mode, back_url))

    result = build_word_result(normalized_query) if normalized_query in WORD_LIBRARY else None
    current_page_url = build_word_lookup_url(
        search_query,
        current_mode,
        back_url,
        search_type=current_search_type,
    )
    search_suggestions = build_search_suggestions(current_mode, current_page_url)

    context = {
        "current_mode": current_mode,
        "search_query": search_query,
        "result": result,
        "back_url": back_url,
        "current_page_url": current_page_url,
        "search_suggestions_json": json.dumps(search_suggestions),
        "research_graph": build_graph_data(result) if result else None,
        "suggested_words": [WORD_LIBRARY[word]["english_word"] for word in RECENT_SEARCHES],
        "browse_topics_url": build_browse_topics_url(current_mode, current_page_url),
    }
    context.update(build_shared_context(request, current_mode, current_search_type))
    return render(request, "research.html", context)


def bookmarks_page(request):
    current_mode = get_current_mode(request)
    current_search_type = get_current_search_type(request)
    fallback_back_url = build_url("home", params={"mode": current_mode})
    back_url = get_safe_back_url(
        request.POST.get("back") or request.GET.get("back"),
        fallback_back_url,
    )

    if request.method == "POST":
        return handle_bookmark_actions(request, current_mode, back_url)

    current_page_url = build_url(
        "bookmarks",
        params={
            "mode": current_mode,
            "back": back_url,
        },
    )

    return render(
        request,
        "bookmarks.html",
        {
            **build_shared_context(request, current_mode, current_search_type),
            "current_mode": current_mode,
            "back_url": back_url,
            "current_page_url": current_page_url,
            "bookmarks": build_bookmark_results(request),
            "browse_topics_url": build_browse_topics_url(current_mode, current_page_url),
        },
    )


def lessons_page(request):
    current_mode = get_current_mode(request)
    current_search_type = get_current_search_type(request)
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

    current_page_url = build_url(
        "lessons",
        params={
            "mode": current_mode,
            "word": selected_word,
            "back": back_url,
        },
    )
    lesson_word_suggestions = build_lesson_word_suggestions(current_mode, current_page_url)

    return render(
        request,
        "lessons.html",
        {
            **build_shared_context(request, current_mode, current_search_type),
            "current_mode": current_mode,
            "back_url": back_url,
            "current_page_url": current_page_url,
            "selected_word": selected_word,
            "selected_result": build_word_result(selected_word) if selected_word else None,
            "lessons": build_lessons_context(request, current_word=selected_word),
            "lesson_count": len(get_lessons(request)),
            "browse_topics_url": build_browse_topics_url(current_mode, current_page_url),
            "lesson_word_suggestions_json": json.dumps(lesson_word_suggestions),
        },
    )


def browse_topics_page(request):
    current_mode = get_current_mode(request)
    current_search_type = get_current_search_type(request, default="category")
    fallback_back_url = build_url("home", params={"mode": current_mode})
    back_url = get_safe_back_url(request.GET.get("back"), fallback_back_url)
    search_query = (request.GET.get("q", "") or "").strip()
    matching_topics = filter_topics(search_query)
    current_page_url = build_browse_topics_url(
        current_mode,
        back_url,
        search_query=search_query,
        search_type=current_search_type,
    )
    search_suggestions = build_search_suggestions(current_mode, current_page_url)

    context = {
        "current_mode": current_mode,
        "back_url": back_url,
        "current_page_url": current_page_url,
        "search_query": search_query,
        "search_suggestions_json": json.dumps(search_suggestions),
        "topics": build_topic_cards(
            current_mode,
            current_page_url,
            topics=matching_topics,
            search_type=current_search_type,
        ),
        "topic_count": len(TOPICS),
        "filtered_topic_count": len(matching_topics),
        "has_topic_filter": bool(search_query),
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
                "back": current_page_url,
            },
        ),
        "research_sample_url": build_word_lookup_url("horse", "Research", current_page_url),
    }
    context.update(build_shared_context(request, current_mode, current_search_type))
    return render(request, "topics.html", context)


def topic_detail(request, topic_name):
    current_mode = get_current_mode(request)
    current_search_type = get_current_search_type(request)
    fallback_back_url = build_url("home", params={"mode": current_mode})
    back_url = get_safe_back_url(request.GET.get("back"), fallback_back_url)
    topic_view = get_topic_view(request)
    topic = TOPIC_LOOKUP.get(topic_name)
    topic_label = topic["name"] if topic is not None else topic_name.replace("-", " ").title()
    current_page_url = build_topic_detail_url(
        topic_name,
        current_mode,
        back_url,
        topic_view,
        search_type=current_search_type,
    )

    if topic is None:
        return render(
            request,
            "topic_detail.html",
            {
                **build_shared_context(request, current_mode, current_search_type),
                "current_mode": current_mode,
                "topic_exists": False,
                "topic_label": topic_label,
                "back_url": back_url,
                "current_page_url": current_page_url,
                "topic_view": topic_view,
                "browse_topics_url": build_browse_topics_url(current_mode, current_page_url),
                "research_sample_url": build_word_lookup_url("horse", "Research", current_page_url),
            },
        )

    topic_words = [build_word_result(word) for word in topic["words"]]

    return render(
        request,
        "topic_detail.html",
        {
            **build_shared_context(request, current_mode, current_search_type),
            "current_mode": current_mode,
            "topic_exists": True,
            "topic_label": topic_label,
            "topic": topic,
            "topic_words": topic_words,
            "back_url": back_url,
            "current_page_url": current_page_url,
            "topic_view": topic_view,
            "list_view_url": build_topic_detail_url(
                topic["slug"],
                current_mode,
                back_url,
                "list",
                search_type=current_search_type,
            ),
            "map_view_url": build_topic_detail_url(
                topic["slug"],
                current_mode,
                back_url,
                "map",
                search_type=current_search_type,
            ),
            "topic_graph": build_topic_graph_data(topic, current_mode, current_page_url),
            "browse_topics_url": build_browse_topics_url(current_mode, current_page_url),
            "research_sample_url": build_word_lookup_url(topic["words"][0], "Research", current_page_url),
        },
    )

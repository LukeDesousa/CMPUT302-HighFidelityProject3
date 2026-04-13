import json
from math import cos, radians, sin, sqrt
from urllib.parse import urlencode

from django.shortcuts import redirect, render
from django.urls import reverse


MODES = ("Explore", "Research")
DEFAULT_MODE = "Explore"
SEARCH_TYPES = ("word", "category")
DEFAULT_SEARCH_TYPE = "word"
TOPIC_VIEWS = ("list", "map")
HOME_TOPIC_LIMIT = 6
SEARCH_PLACEHOLDER = "Search words or categories"
PROTOTYPE_SOURCE = "Prototype vocabulary set"
MODE_DETAILS = {
    "Explore": "Search and explore vocabulary",
    "Research": "Explore relationships between words",
}
SEARCH_TYPE_DETAILS = {
    "word": {
        "label": "Word",
        "option_label": "Word",
        "description": "Search for a specific word and open its details.",
        "placeholder": SEARCH_PLACEHOLDER,
    },
    "category": {
        "label": "Category",
        "option_label": "Category",
        "description": "Search for a category before opening a topic.",
        "placeholder": SEARCH_PLACEHOLDER,
    },
}


def make_word(
    english_word,
    topic,
    cree_translation,
    word_class,
    *,
    syllabics=None,
    note=None,
    source=PROTOTYPE_SOURCE,
    cree_label="Plains Cree",
):
    return {
        "english_word": english_word,
        "topic": topic,
        "cree_translation": cree_translation,
        "cree_label": cree_label,
        "syllabics": syllabics,
        "word_class": word_class,
        "dictionary_note": note
        or f"{word_class} prototype entry used to expand the {topic} vocabulary set for the current demo.",
        "research_source": source,
    }


TOPICS = (
    {
        "name": "Family",
        "slug": "family",
        "icon": "family",
        "summary": "Words for people close to home.",
        "words": (
            "mother",
            "father",
            "baby",
            "grandmother",
            "grandfather",
            "child",
            "brother",
            "sister",
        ),
    },
    {
        "name": "Sports",
        "slug": "sports",
        "icon": "sports",
        "summary": "Words for games and movement.",
        "words": (
            "hockey",
            "soccer",
            "skate",
            "goal",
            "ball",
            "team",
            "stick",
            "game",
        ),
    },
    {
        "name": "Seasons",
        "slug": "seasons",
        "icon": "seasons",
        "summary": "Season words you can browse from the home page.",
        "words": (
            "spring",
            "summer",
            "autumn",
            "winter",
            "rain",
            "snow",
            "wind",
            "ice",
        ),
    },
    {
        "name": "Nouns",
        "slug": "nouns",
        "icon": "nouns",
        "summary": "Starter nouns to browse and explore.",
        "words": (
            "house",
            "book",
            "water",
            "sun",
            "moon",
            "fire",
            "tree",
            "school",
        ),
    },
    {
        "name": "Verbs",
        "slug": "verbs",
        "icon": "verbs",
        "summary": "Common action words.",
        "words": (
            "run",
            "eat",
            "sleep",
            "sing",
            "walk",
            "sit",
            "speak",
            "see",
        ),
    },
    {
        "name": "Fruits",
        "slug": "fruits",
        "icon": "fruits",
        "summary": "Fruit words grouped into one browseable topic.",
        "words": (
            "apple",
            "berry",
            "orange",
            "grape",
            "banana",
            "cherry",
            "pear",
            "plum",
        ),
    },
    {
        "name": "Animals",
        "slug": "animals",
        "icon": "animals",
        "summary": "Animal words with Cree translations.",
        "words": (
            "horse",
            "rabbit",
            "dog",
            "bear",
            "moose",
            "fox",
            "wolf",
            "bird",
            "deer",
        ),
    },
)

TOPIC_LOOKUP = {topic["slug"]: topic for topic in TOPICS}
TOPIC_ORDER = [topic["slug"] for topic in TOPICS]
RESEARCH_RELATED_ANGLES = {
    1: (270,),
    2: (235, 305),
    3: (215, 270, 325),
    4: (205, 245, 295, 335),
}

WORD_LIBRARY = {
    "mother": make_word("mother", "family", "nikâwiy", "NA"),
    "father": make_word("father", "family", "ôhtâwiy", "NA"),
    "baby": make_word("baby", "family", "apiysis", "NA"),
    "grandmother": make_word("grandmother", "family", "kôhkom", "NA"),
    "grandfather": make_word("grandfather", "family", "môsom", "NA"),
    "child": make_word("child", "family", "awâsis", "NA"),
    "brother": make_word("brother", "family", "nisîmis", "NA"),
    "sister": make_word("sister", "family", "nisîs", "NA"),
    "hockey": make_word("hockey", "sports", "hoki", "NI"),
    "soccer": make_word("soccer", "sports", "sâkar", "NI"),
    "skate": make_word("skate", "sports", "skêt", "NI"),
    "goal": make_word("goal", "sports", "kôl", "NI"),
    "ball": make_word("ball", "sports", "pâl", "NI"),
    "team": make_word("team", "sports", "tîm", "NI"),
    "stick": make_word("stick", "sports", "stik", "NI"),
    "game": make_word("game", "sports", "kêm", "NI"),
    "spring": make_word("spring", "seasons", "sîkwan", "NI"),
    "summer": make_word("summer", "seasons", "nipin", "NI"),
    "autumn": make_word("autumn", "seasons", "takwâkin", "NI"),
    "winter": make_word("winter", "seasons", "pipon", "NI"),
    "rain": make_word("rain", "seasons", "kimiwan", "NI"),
    "snow": make_word("snow", "seasons", "kona", "NI"),
    "wind": make_word("wind", "seasons", "yôtin", "NI"),
    "ice": make_word("ice", "seasons", "mîkwam", "NI"),
    "house": make_word("house", "nouns", "wâskahikan", "NI"),
    "book": make_word("book", "nouns", "masinahikan", "NI"),
    "water": make_word(
        "water",
        "nouns",
        "nipiy",
        "NI",
        note="Inanimate noun used for water. Prototype entry expanded from the broader water-related research set.",
    ),
    "sun": make_word("sun", "nouns", "pîsim", "NI"),
    "moon": make_word("moon", "nouns", "tipiskâw-pîsim", "NI"),
    "fire": make_word("fire", "nouns", "iskotêw", "NI"),
    "tree": make_word("tree", "nouns", "mistik", "NI"),
    "school": make_word("school", "nouns", "kiskinwahamâtowikamik", "NI"),
    "run": make_word("run", "verbs", "pimipahtâw", "VAI"),
    "eat": make_word("eat", "verbs", "mîcisow", "VAI"),
    "sleep": make_word("sleep", "verbs", "nipâw", "VAI"),
    "sing": make_word("sing", "verbs", "nikamow", "VAI"),
    "walk": make_word("walk", "verbs", "pimohtew", "VAI"),
    "sit": make_word(
        "sit",
        "verbs",
        "apiw",
        "VAI",
        note="Verb entry meaning to sit or be sitting. Prototype dataset expanded using the same action pattern as the research examples.",
    ),
    "speak": make_word(
        "speak",
        "verbs",
        "itêw",
        "VTA-4",
        note="Transitive animate verb used for speaking or saying something to someone. Prototype dataset expanded from the broader research set.",
        source="itwêwina Plains Cree Dictionary",
    ),
    "see": make_word("see", "verbs", "wâpamêw", "VTA"),
    "apple": make_word("apple", "fruits", "minôs", "NI"),
    "berry": make_word("berry", "fruits", "mîna", "NI"),
    "orange": make_word("orange", "fruits", "orans", "NI"),
    "grape": make_word("grape", "fruits", "grêp", "NI"),
    "banana": make_word("banana", "fruits", "panana", "NI"),
    "cherry": make_word("cherry", "fruits", "ceri", "NI"),
    "pear": make_word("pear", "fruits", "pêr", "NI"),
    "plum": make_word("plum", "fruits", "plam", "NI"),
    "horse": make_word(
        "horse",
        "animals",
        "mistatim",
        "NA",
        syllabics="ᒥᐢᑕᑎᒼ",
        note="Animate noun. Dictionary note: horse, plural =wak; alternate spelling misatim appears in some entries.",
        source="Online Cree Dictionary",
    ),
    "rabbit": make_word(
        "rabbit",
        "animals",
        "wâpos",
        "NA",
        syllabics="ᐚᐳᐢ",
        note="Animate noun. Dictionary note: rabbit or hare, plural =wak.",
        source="Online Cree Dictionary",
    ),
    "dog": make_word(
        "dog",
        "animals",
        "atim",
        "NA",
        syllabics="ᐊᑎᒼ",
        note="Animate noun. Dictionary note: dog; horse; beast of burden.",
        source="Online Cree Dictionary",
    ),
    "bear": make_word(
        "bear",
        "animals",
        "maskwa",
        "NA",
        syllabics="ᒪᐢᑿ",
        note="Animate noun. Dictionary note: bear, possessive stem =maskom-, plural =wak.",
        source="Online Cree Dictionary",
    ),
    "moose": make_word(
        "moose",
        "animals",
        "môswa",
        "NA",
        syllabics="ᒨᐢᐘ",
        note="Animate noun. Dictionary note: moose, plural =k.",
        source="Online Cree Dictionary",
    ),
    "fox": make_word("fox", "animals", "makêsis", "NA"),
    "wolf": make_word("wolf", "animals", "mahihkan", "NA"),
    "bird": make_word("bird", "animals", "pihêw", "NA"),
    "deer": make_word("deer", "animals", "atihk", "NA"),
}

RECENT_SEARCHES = ("horse", "fox", "school", "winter")


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
    requested_mode = request.POST.get("mode") or request.GET.get("mode") or DEFAULT_MODE
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


def build_collections_url(current_mode, back_url, selected_word=None):
    return build_url(
        "collections",
        params={
            "mode": "Explore",
            "back": back_url,
            "word": selected_word,
        },
    )


def get_saved_words(request):
    saved_words = request.session.get("saved_words", [])
    return [word for word in saved_words if word in WORD_LIBRARY]


def save_saved_words(request, saved_words):
    request.session["saved_words"] = saved_words


def get_collections(request):
    collections = request.session.get("collections", [])
    cleaned_collections = []

    for collection in collections:
        name = (collection.get("name") or "").strip()
        if not name:
            continue

        cleaned_collections.append(
            {
                "name": name,
                "notes": (collection.get("notes") or "").strip(),
                "words": [
                    word
                    for word in collection.get("words", [])
                    if word in WORD_LIBRARY
                ],
            }
        )

    return cleaned_collections


def save_collections(request, collections):
    request.session["collections"] = collections


def set_toast(request, message, kind="success"):
    request.session["toast"] = {
        "message": message,
        "kind": kind,
    }


def pop_toast(request):
    toast = request.session.pop("toast", None)
    if isinstance(toast, dict) and toast.get("message"):
        return toast
    return None


def set_collection_prompt(request, word_key):
    request.session["collection_prompt_word"] = word_key


def pop_collection_prompt(request):
    prompt_word = request.session.pop("collection_prompt_word", None)
    return prompt_word if prompt_word in WORD_LIBRARY else None


def clear_collection_prompt(request):
    request.session.pop("collection_prompt_word", None)


def build_mode_options(current_mode, current_search_type):
    return [
        {
            "value": mode,
            "description": MODE_DETAILS[mode],
            "is_current": mode == current_mode,
            "url": build_url(
                "home",
                params={
                    "mode": mode,
                    "search_type": current_search_type,
                },
            ),
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
                "url": build_word_lookup_url(
                    entry["english_word"],
                    current_mode,
                    back_url,
                ),
            }
        )

    for topic in TOPICS:
        suggestions.append(
            {
                "label": topic["name"],
                "kind": "Category",
                "meta": f"{len(topic['words'])} words",
                "keywords": " ".join(
                    [topic["name"], topic["slug"], topic["summary"], *topic["words"]]
                ).lower(),
                "url": build_topic_detail_url(
                    topic["slug"],
                    current_mode,
                    back_url,
                ),
            }
        )

    return suggestions


def build_collection_word_suggestions(current_mode, back_url):
    suggestions = []

    for word_key in sorted(WORD_LIBRARY):
        entry = WORD_LIBRARY[word_key]
        topic = TOPIC_LOOKUP[entry["topic"]]
        searchable_terms = [entry["english_word"], topic["name"], topic["slug"]]
        if entry.get("cree_translation"):
            searchable_terms.append(entry["cree_translation"])

        suggestions.append(
            {
                "label": entry["english_word"].title(),
                "kind": "Word",
                "meta": entry.get("cree_translation") or topic["name"],
                "keywords": " ".join(searchable_terms).lower(),
                "url": build_collections_url(
                    current_mode,
                    back_url,
                    selected_word=entry["english_word"],
                ),
            }
        )

    return suggestions


def build_shared_context(request, current_mode, search_type):
    return {
        "mode_options": build_mode_options(current_mode, search_type),
        "current_search_type": search_type,
        "search_types": build_search_type_options(search_type),
        "search_placeholder": SEARCH_TYPE_DETAILS[search_type]["placeholder"],
        "search_helper_text": SEARCH_TYPE_DETAILS[search_type]["description"],
        "search_route_name": get_word_route_name(current_mode),
        "search_word_action": reverse(get_word_route_name(current_mode)),
        "search_category_action": reverse("browse-topics"),
        "toast": pop_toast(request),
    }


def build_mock_embedding(word_key):
    entry = WORD_LIBRARY[word_key]
    english = entry["english_word"].lower()
    cree = (entry.get("cree_translation") or entry["english_word"]).lower()

    english_letters = "abcdefghijklmnopqrstuvwxyz"
    cree_letters = "abcdefghijklmnopqrstuvwxyzâêîô"

    def char_profile(text, alphabet):
        filtered = [character for character in text if character in alphabet]
        text_length = max(len(filtered), 1)
        return [filtered.count(character) / text_length for character in alphabet]

    topic_position = (TOPIC_ORDER.index(entry["topic"]) + 1) / len(TOPIC_ORDER)

    vector = [
        1.0,
        topic_position,
        len(english) / 12,
        sum(character in "aeiou" for character in english) / max(len(english), 1),
        len(cree) / 12,
        sum(character in "aeiouâêîô" for character in cree) / max(len(cree), 1),
        1.0 if entry.get("cree_translation") else 0.45,
        1.0 if entry.get("word_class") else 0.4,
    ]
    vector.extend(char_profile(english, english_letters))
    vector.extend(char_profile(cree, cree_letters))
    return vector


def cosine_similarity(vector_a, vector_b):
    dot_product = sum(left * right for left, right in zip(vector_a, vector_b))
    magnitude_a = sqrt(sum(value * value for value in vector_a))
    magnitude_b = sqrt(sum(value * value for value in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0

    return dot_product / (magnitude_a * magnitude_b)


def build_similarity_score(word_key, related_key):
    raw_similarity = cosine_similarity(
        build_mock_embedding(word_key),
        build_mock_embedding(related_key),
    )
    scaled_similarity = max(0.18, min(0.96, 0.18 + (raw_similarity * 0.74)))
    return round(scaled_similarity, 2)


def build_word_result(word_key):
    entry = WORD_LIBRARY[word_key]
    topic = TOPIC_LOOKUP[entry["topic"]]
    related_words = []

    for related_key in topic["words"]:
        if related_key == word_key:
            continue

        related_entry = WORD_LIBRARY[related_key]
        similarity = build_similarity_score(word_key, related_key)
        related_words.append(
            {
                "english": related_entry["english_word"],
                "cree": related_entry.get("cree_translation"),
                "similarity": similarity,
                "similarity_label": f"{similarity:.2f}",
            }
        )

    related_words.sort(key=lambda related_word: related_word["similarity"], reverse=True)

    return {
        "english_word": entry["english_word"],
        "topic_slug": topic["slug"],
        "topic_name": topic["name"],
        "topic_icon": topic["icon"],
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


def build_saved_word_results(request):
    return [build_word_result(word) for word in get_saved_words(request)]


def build_collections_context(request, current_word=None):
    collections_context = []
    for collection in get_collections(request):
        word_results = [
            build_word_result(word)
            for word in collection.get("words", [])
            if word in WORD_LIBRARY
        ]
        collections_context.append(
            {
                "name": collection["name"],
                "words": word_results,
                "word_count": len(word_results),
                "notes": collection["notes"],
                "contains_current": current_word in collection.get("words", []),
            }
        )
    return collections_context


def build_graph_data(result):
    nodes = [
        {
            "label": result["english_word"].title(),
            "meta": "Selected Word",
            "x": 50,
            "y": 50,
            "kind": "center",
            "draggable": False,
        }
    ]
    lines = []
    semantic_nodes = [
        {
            "label": result["topic_name"],
            "meta": "Category",
            "x": 26,
            "y": 22,
            "kind": "topic",
            "draggable": False,
        }
    ]

    if result["has_translation"]:
        semantic_nodes.append(
            {
                "label": result["cree_translation"],
                "meta": result["cree_label"],
                "x": 74,
                "y": 22,
                "kind": "translation",
                "draggable": False,
            }
        )

    related_words = result["related_words"][:4]
    angles = RESEARCH_RELATED_ANGLES.get(len(related_words), ())

    for related_word, angle in zip(related_words, angles):
        radius = 38 - (related_word["similarity"] * 18)
        x_position = round(50 + radius * cos(radians(angle)), 2)
        y_position = round(50 + radius * sin(radians(angle)), 2)
        semantic_nodes.append(
            {
                "label": related_word["english"].title(),
                "meta": f"Similarity {related_word['similarity_label']}",
                "x": x_position,
                "y": y_position,
                "kind": "related",
                "draggable": True,
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

    for word_key, (x_position, y_position) in zip(topic["words"], ring_positions):
        word_result = build_word_result(word_key)
        nodes.append(
            {
                "label": word_result["english_word"].title(),
                "meta": word_result["cree_translation"] or "Open word",
                "x": x_position,
                "y": y_position,
                "kind": "related",
                "url": build_word_lookup_url(
                    word_result["english_word"],
                    current_mode,
                    back_url,
                ),
            }
        )
        lines.append(
            {
                "x1": 50,
                "y1": 50,
                "x2": x_position,
                "y2": y_position,
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
                "icon": topic["icon"],
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


def normalize_saved_words(saved_words, selected_word):
    if selected_word not in WORD_LIBRARY:
        return saved_words
    return [selected_word, *[word for word in saved_words if word != selected_word]]


def collection_name_is_available(collections, collection_name, current_name=None):
    normalized_name = collection_name.lower()
    normalized_current = (current_name or "").strip().lower()
    return all(
        collection["name"].lower() == normalized_current
        or collection["name"].lower() != normalized_name
        for collection in collections
    )


def add_word_to_collections(collections, collection_name, selected_word):
    updated_collections = []
    for collection in collections:
        if collection["name"] == collection_name and selected_word in WORD_LIBRARY:
            existing_words = collection.get("words", [])
            updated_collections.append(
                {
                    **collection,
                    "words": (
                        existing_words
                        if selected_word in existing_words
                        else [*existing_words, selected_word]
                    ),
                }
            )
            continue

        updated_collections.append(collection)

    return updated_collections


def remove_word_from_collection(collections, collection_name, selected_word):
    updated_collections = []
    for collection in collections:
        if collection["name"] == collection_name:
            updated_collections.append(
                {
                    **collection,
                    "words": [
                        word for word in collection.get("words", [])
                        if word != selected_word
                    ],
                }
            )
            continue

        updated_collections.append(collection)

    return updated_collections


def remove_word_from_all_collections(collections, selected_word):
    return [
        {
            **collection,
            "words": [
                word for word in collection.get("words", [])
                if word != selected_word
            ],
        }
        for collection in collections
    ]


def update_collection_details(collections, current_name, next_name, notes):
    updated_collections = []
    for collection in collections:
        if collection["name"] == current_name:
            updated_collections.append(
                {
                    "name": next_name,
                    "notes": notes,
                    "words": collection.get("words", []),
                }
            )
            continue

        updated_collections.append(collection)

    return updated_collections


def handle_search_actions(request, current_mode, word_key, back_url):
    action = request.POST.get("action", "").strip()
    search_type = get_current_search_type(request)

    if current_mode != "Explore":
        return redirect(
            build_word_lookup_url(
                request.POST.get("q", word_key or "horse"),
                current_mode,
                back_url,
                search_type=search_type,
            )
        )

    saved_words = get_saved_words(request)
    collections = get_collections(request)

    if action == "toggle_saved_word" and word_key in WORD_LIBRARY:
        if word_key in saved_words:
            save_saved_words(
                request,
                [saved_word for saved_word in saved_words if saved_word != word_key],
            )
            save_collections(request, remove_word_from_all_collections(collections, word_key))
            clear_collection_prompt(request)
            set_toast(request, "Removed from Collection")
        else:
            save_saved_words(request, normalize_saved_words(saved_words, word_key))
            set_collection_prompt(request, word_key)
            set_toast(request, "Added to Collection")

    if action == "create_collection" and word_key in WORD_LIBRARY:
        collection_name = request.POST.get("collection_name", "").strip()
        collection_notes = request.POST.get("collection_notes", "").strip()
        if collection_name and collection_name_is_available(collections, collection_name):
            save_saved_words(request, normalize_saved_words(saved_words, word_key))
            save_collections(
                request,
                [
                    {
                        "name": collection_name,
                        "notes": collection_notes,
                        "words": [word_key],
                    },
                    *collections,
                ],
            )
            clear_collection_prompt(request)
            set_toast(request, "Added to Collection")
        elif collection_name:
            set_toast(request, "Choose a different collection name", kind="warning")

    if action == "add_to_collection" and word_key in WORD_LIBRARY:
        collection_name = request.POST.get("collection_name", "").strip()
        save_saved_words(request, normalize_saved_words(saved_words, word_key))
        save_collections(
            request,
            add_word_to_collections(collections, collection_name, word_key),
        )
        clear_collection_prompt(request)
        set_toast(request, "Added to Collection")

    if action == "remove_from_collection" and word_key in WORD_LIBRARY:
        collection_name = request.POST.get("collection_name", "").strip()
        save_collections(
            request,
            remove_word_from_collection(collections, collection_name, word_key),
        )
        set_toast(request, "Removed from Collection")

    return redirect(
        build_word_lookup_url(
            request.POST.get("q", word_key or "horse"),
            current_mode,
            back_url,
            search_type=search_type,
        )
    )


def handle_collection_actions(request, selected_word, back_url):
    action = request.POST.get("action", "").strip()
    collections = get_collections(request)
    saved_words = get_saved_words(request)
    redirect_word = selected_word

    if action == "create_collection":
        collection_name = request.POST.get("collection_name", "").strip()
        collection_notes = request.POST.get("collection_notes", "").strip()
        if collection_name and collection_name_is_available(collections, collection_name):
            initial_words = [selected_word] if selected_word in WORD_LIBRARY else []
            if initial_words:
                save_saved_words(request, normalize_saved_words(saved_words, selected_word))
            save_collections(
                request,
                [
                    {
                        "name": collection_name,
                        "notes": collection_notes,
                        "words": initial_words,
                    },
                    *collections,
                ],
            )
            set_toast(
                request,
                "Added to Collection" if initial_words else "Collection created",
            )
            if initial_words:
                redirect_word = None
        elif collection_name:
            set_toast(request, "Choose a different collection name", kind="warning")

    if action == "save_collection":
        current_name = request.POST.get("current_name", "").strip()
        next_name = request.POST.get("collection_name", "").strip()
        collection_notes = request.POST.get("collection_notes", "").strip()
        if next_name and collection_name_is_available(collections, next_name, current_name):
            save_collections(
                request,
                update_collection_details(collections, current_name, next_name, collection_notes),
            )
            set_toast(request, "Collection updated")
        elif next_name:
            set_toast(request, "Choose a different collection name", kind="warning")

    if action == "delete_collection":
        collection_name = request.POST.get("collection_name", "").strip()
        updated_collections = [
            collection
            for collection in collections
            if collection["name"] != collection_name
        ]
        if len(updated_collections) != len(collections):
            save_collections(request, updated_collections)
            set_toast(request, "Collection deleted")

    if action == "add_to_collection" and selected_word in WORD_LIBRARY:
        collection_name = request.POST.get("collection_name", "").strip()
        save_saved_words(request, normalize_saved_words(saved_words, selected_word))
        save_collections(
            request,
            add_word_to_collections(collections, collection_name, selected_word),
        )
        set_toast(request, "Added to Collection")

    if action == "remove_from_collection":
        collection_name = request.POST.get("collection_name", "").strip()
        word_key = (request.POST.get("word") or selected_word or "").strip().lower()
        if word_key in WORD_LIBRARY:
            save_collections(
                request,
                remove_word_from_collection(collections, collection_name, word_key),
            )
            set_toast(request, "Removed from Collection")

    if action == "remove_saved_word":
        word_key = request.POST.get("word", "").strip().lower()
        if word_key in WORD_LIBRARY:
            save_saved_words(
                request,
                [saved_word for saved_word in saved_words if saved_word != word_key],
            )
            save_collections(request, remove_word_from_all_collections(collections, word_key))
            set_toast(request, "Removed from Collection")
            if word_key == selected_word:
                redirect_word = None

    return redirect(build_collections_url("Explore", back_url, redirect_word))


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
        "saved_word_count": len(get_saved_words(request)),
        "collection_count": len(get_collections(request)),
        "collections_url": build_collections_url("Explore", home_back_url),
        "research_sample_url": build_word_lookup_url("horse", "Research", home_back_url),
        "browse_topics_url": build_browse_topics_url(current_mode, home_back_url),
        "search_suggestions_json": json.dumps(search_suggestions),
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
    raw_query = (
        request.POST.get("q")
        if request.method == "POST"
        else request.GET.get("q", "horse")
    ) or "horse"
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
    saved_words = get_saved_words(request)
    collections = build_collections_context(
        request,
        current_word=normalized_query if result else None,
    )
    collection_prompt_word = pop_collection_prompt(request)

    if result is not None:
        result["is_saved"] = normalized_query in saved_words

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
        "saved_word_count": len(saved_words),
        "collection_count": len(collections),
        "collections": collections,
        "collections_url": build_collections_url("Explore", current_page_url, normalized_query if result else None),
        "show_collection_prompt": collection_prompt_word == normalized_query,
        "browse_topics_url": build_browse_topics_url(current_mode, current_page_url),
    }
    context.update(build_shared_context(request, current_mode, current_search_type))
    return render(request, "search_results.html", context)


def research_page(request):
    current_mode = get_current_mode(request)
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


def collections_page(request):
    current_mode = "Explore"
    current_search_type = get_current_search_type(request)
    fallback_back_url = build_url("home", params={"mode": current_mode})
    back_url = get_safe_back_url(
        request.POST.get("back") or request.GET.get("back"),
        fallback_back_url,
    )
    selected_word = (request.POST.get("word") or request.GET.get("word") or "").strip().lower()
    selected_word = selected_word if selected_word in WORD_LIBRARY else None

    if request.method == "POST":
        return handle_collection_actions(request, selected_word, back_url)

    current_page_url = build_collections_url(current_mode, back_url, selected_word)
    collection_word_suggestions = build_collection_word_suggestions(current_mode, current_page_url)

    return render(
        request,
        "collections.html",
        {
            **build_shared_context(request, current_mode, current_search_type),
            "current_mode": current_mode,
            "back_url": back_url,
            "current_page_url": current_page_url,
            "selected_word": selected_word,
            "selected_result": build_word_result(selected_word) if selected_word else None,
            "saved_words": build_saved_word_results(request),
            "saved_word_count": len(get_saved_words(request)),
            "collections": build_collections_context(request, current_word=selected_word),
            "collection_count": len(get_collections(request)),
            "browse_topics_url": build_browse_topics_url(current_mode, current_page_url),
            "collection_word_suggestions_json": json.dumps(collection_word_suggestions),
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
        "collections_url": build_collections_url("Explore", current_page_url),
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
                "collections_url": build_collections_url("Explore", current_page_url),
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
            "collections_url": build_collections_url("Explore", current_page_url),
            "research_sample_url": build_word_lookup_url(topic["words"][0], "Research", current_page_url),
        },
    )

from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def test_home_page_renders_topic_preview(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recent Searches")
        self.assertContains(response, "Explore by Topics")
        self.assertContains(response, "Search a word or category...")
        self.assertContains(response, 'data-mode-menu', html=False)
        self.assertContains(response, 'data-search-suggestions-source', html=False)
        self.assertContains(response, "Build lessons, add notes, and collect words for class use.")
        self.assertContains(response, "Inspect a word through connected meanings and topic maps.")
        self.assertNotContains(response, "Search By")
        self.assertContains(response, "Browse All")

        for slug, label in (
            ("family", "Family"),
            ("sports", "Sports"),
            ("seasons", "Seasons"),
            ("nouns", "Nouns"),
            ("verbs", "Verbs"),
            ("fruits", "Fruits"),
        ):
            self.assertContains(response, label)
            self.assertContains(response, reverse("topic-detail", args=[slug]))

        self.assertContains(response, 'class="topic-card topic-card-detail"', count=6, html=False)

    def test_browse_topics_page_renders_all_topics(self):
        response = self.client.get(reverse("browse-topics"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Browse Topics")
        self.assertContains(response, "Animals")
        self.assertContains(response, reverse("topic-detail", args=["animals"]))

    def test_research_mode_has_dedicated_graph_page(self):
        redirect_response = self.client.get(
            reverse("search-results"),
            {"q": "horse", "mode": "Research"},
        )

        self.assertEqual(redirect_response.status_code, 302)
        self.assertIn(reverse("research"), redirect_response.url)

        response = self.client.get(
            reverse("research"),
            {"q": "horse", "mode": "Research"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Research Graph")
        self.assertContains(response, "mistatim")
        self.assertContains(response, "ᒥᐢᑕᑎᒼ")
        self.assertContains(response, "Word Class")
        self.assertContains(response, "Drag to move")
        self.assertContains(response, "Zoom In")
        self.assertContains(response, 'data-graph-workspace', html=False)

    def test_category_search_filters_topic_results(self):
        response = self.client.get(
            reverse("browse-topics"),
            {"mode": "Teacher", "search_type": "category", "q": "ani"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Search a word or category...")
        self.assertContains(response, "Animals")
        self.assertContains(response, 'class="browse-topic-card"', count=1, html=False)

    def test_standard_mode_can_toggle_bookmark(self):
        response = self.client.post(
            reverse("search-results"),
            {
                "action": "toggle_bookmark",
                "mode": "Standard",
                "q": "rabbit",
                "back": reverse("home"),
                "search_type": "word",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Remove Bookmark")
        self.assertContains(response, "Word saved to your list")
        self.assertIn("rabbit", self.client.session["bookmarks"])

    def test_bookmarks_page_renders_saved_words(self):
        session = self.client.session
        session["bookmarks"] = ["horse", "rabbit"]
        session.save()

        response = self.client.get(reverse("bookmarks"), {"mode": "Standard"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bookmarks")
        self.assertContains(response, "Horse")
        self.assertContains(response, "Rabbit")

    def test_teacher_mode_can_create_lesson_and_add_word(self):
        self.client.post(
            reverse("lessons"),
            {
                "action": "create_lesson",
                "mode": "Teacher",
                "word": "horse",
                "lesson_name": "Animal Basics",
                "lesson_notes": "Warm-up vocabulary",
                "back": reverse("home"),
            },
            follow=True,
        )

        response = self.client.post(
            reverse("lessons"),
            {
                "action": "add_to_lesson",
                "mode": "Teacher",
                "word": "horse",
                "lesson_name": "Animal Basics",
                "back": reverse("home"),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Animal Basics")
        self.assertContains(response, "Already added")
        self.assertContains(response, "Warm-up vocabulary")
        self.assertEqual(self.client.session["lessons"][0]["words"], ["horse"])
        self.assertEqual(self.client.session["lessons"][0]["notes"], "Warm-up vocabulary")

    def test_teacher_search_result_can_create_lesson_with_current_word(self):
        response = self.client.post(
            reverse("search-results"),
            {
                "action": "create_lesson",
                "mode": "Teacher",
                "q": "horse",
                "lesson_name": "Map Lesson",
                "back": reverse("home"),
                "search_type": "word",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Map Lesson")
        self.assertContains(response, "Already added")
        self.assertEqual(self.client.session["lessons"][0]["words"], ["horse"])

    def test_lessons_page_renders_separately(self):
        response = self.client.get(
            reverse("lessons"),
            {"mode": "Teacher", "word": "horse"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create New Lesson")
        self.assertContains(response, "Save Lesson")
        self.assertContains(response, "Find a word to add...")
        self.assertContains(response, "Horse")

    def test_teacher_search_result_links_to_dedicated_lesson_builder(self):
        response = self.client.get(
            reverse("search-results"),
            {"q": "horse", "mode": "Teacher"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create New Lesson")
        self.assertContains(response, reverse("lessons"))

    def test_subpage_mode_switcher_is_in_nav_and_links_home(self):
        response = self.client.get(
            reverse("search-results"),
            {"q": "horse", "mode": "Teacher"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-mode-menu', html=False)
        self.assertContains(response, '/?mode=Teacher&search_type=word')
        self.assertContains(response, "Save useful words to a quick review list for later.")

    def test_lesson_export_shows_toast(self):
        session = self.client.session
        session["lessons"] = [{"name": "Animal Basics", "words": ["horse"], "notes": ""}]
        session.save()

        response = self.client.post(
            reverse("lessons"),
            {
                "action": "export_lesson",
                "mode": "Teacher",
                "lesson_name": "Animal Basics",
                "back": reverse("home"),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PDF Export started")

    def test_lesson_can_be_deleted(self):
        session = self.client.session
        session["lessons"] = [{"name": "Animal Basics", "words": ["horse"], "notes": ""}]
        session.save()

        response = self.client.post(
            reverse("lessons"),
            {
                "action": "delete_lesson",
                "mode": "Teacher",
                "lesson_name": "Animal Basics",
                "back": reverse("home"),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lesson deleted")
        self.assertEqual(self.client.session["lessons"], [])

    def test_topic_page_preserves_mode_search_links(self):
        response = self.client.get(
            reverse("topic-detail", args=["animals"]),
            {"mode": "Standard"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Animals")
        self.assertContains(response, "mode=Standard")
        self.assertContains(response, "Bookmarks")

    def test_topic_page_supports_map_view_in_all_modes(self):
        response = self.client.get(
            reverse("topic-detail", args=["animals"]),
            {"mode": "Standard", "view": "map"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "List")
        self.assertContains(response, "Map")
        self.assertContains(response, "Interactive topic map")
        self.assertContains(response, 'data-graph-workspace', html=False)

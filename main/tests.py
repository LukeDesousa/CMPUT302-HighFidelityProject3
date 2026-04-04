from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def test_home_page_renders_all_topics(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recent Searches")
        self.assertContains(response, "Explore by Topics")
        self.assertContains(response, "Search by word...")

        for slug, label in (
            ("family", "Family"),
            ("sports", "Sports"),
            ("seasons", "Seasons"),
            ("nouns", "Nouns"),
            ("verbs", "Verbs"),
            ("fruits", "Fruits"),
            ("animals", "Animals"),
        ):
            self.assertContains(response, label)
            self.assertContains(response, reverse("topic-detail", args=[slug]))

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
        self.assertContains(response, "Drag to move")
        self.assertContains(response, "Zoom In")
        self.assertContains(response, 'data-graph-workspace', html=False)

    def test_standard_mode_can_toggle_bookmark(self):
        response = self.client.post(
            reverse("search-results"),
            {
                "action": "toggle_bookmark",
                "mode": "Standard",
                "q": "rabbit",
                "back": reverse("home"),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Remove Bookmark")
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
        self.assertContains(response, "Added")
        self.assertEqual(self.client.session["lessons"][0]["words"], ["horse"])

    def test_lessons_page_renders_separately(self):
        response = self.client.get(
            reverse("lessons"),
            {"mode": "Teacher", "word": "horse"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lesson Builder")
        self.assertContains(response, "Selected Word")
        self.assertContains(response, "Horse")

    def test_topic_page_preserves_mode_search_links(self):
        response = self.client.get(
            reverse("topic-detail", args=["animals"]),
            {"mode": "Standard"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Animals")
        self.assertContains(response, "mode=Standard")
        self.assertContains(response, "Bookmarks")

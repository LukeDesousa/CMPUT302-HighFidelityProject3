from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def test_home_page_renders_topics_and_mode_toggle(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recent Searches")
        self.assertContains(response, "Explore by Categories")
        self.assertContains(response, "Search words or categories")
        self.assertContains(response, "Standard")
        self.assertContains(response, "Advanced")
        self.assertContains(response, 'class="mode-toggle"', html=False)

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

        self.assertContains(response, 'class="topic-card topic-card-detail topic-card-spotlight"', count=6, html=False)

    def test_home_page_shows_session_recent_searches_under_search_bar(self):
        self.client.get(
            reverse("search-results"),
            {"q": "rabbit", "mode": "Explore"},
        )
        self.client.get(
            reverse("search-results"),
            {"q": "horse", "mode": "Explore"},
        )
        self.client.get(
            reverse("search-results"),
            {"q": "rabbit", "mode": "Explore"},
        )

        response = self.client.get(reverse("home"))

        self.assertEqual(self.client.session["recent_searches"], ["rabbit", "horse"])
        self.assertContains(response, "Recent Searches")
        self.assertContains(response, ">rabbit</a>", html=False)
        self.assertContains(response, ">horse</a>", html=False)

        content = response.content.decode()
        self.assertLess(content.index("Recent Searches"), content.index("Explore by Categories"))

    def test_browse_topics_page_renders_all_topics(self):
        response = self.client.get(reverse("browse-topics"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Browse Categories")
        self.assertContains(response, "Animals")
        self.assertContains(response, reverse("topic-detail", args=["animals"]))

    def test_research_mode_has_similarity_graph(self):
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
        self.assertContains(response, "Advanced Graph")
        self.assertContains(response, "English Word")
        self.assertContains(response, "Add to Collection")
        self.assertContains(response, "mistatim")
        self.assertContains(response, "ᒥᐢᑕᑎᒼ")
        self.assertContains(response, "Word Class")
        self.assertContains(response, "Drag nodes to explore connections")
        self.assertContains(response, "Similarity")
        self.assertContains(response, 'data-graph-workspace', html=False)
        self.assertContains(response, 'data-graph-node', html=False)
        self.assertContains(response, reverse("select-collection"), html=False)
        self.assertContains(response, "word=horse", html=False)

    def test_research_mode_collection_flow_returns_to_graph(self):
        session = self.client.session
        session["collections"] = [{"name": "Animals", "words": [], "notes": ""}]
        session.save()

        back_url = f"{reverse('research')}?q=horse&mode=Research"
        response = self.client.post(
            reverse("select-collection"),
            {
                "action": "add_to_collection",
                "mode": "Research",
                "word": "horse",
                "collection_name": "Animals",
                "back": back_url,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Advanced Graph")
        self.assertContains(response, "Horse added to Animals")
        self.assertContains(response, "Add to More Collections")
        self.assertNotContains(response, "This word is saved and ready to organize.")
        self.assertEqual(self.client.session["collections"][0]["words"], ["horse"])

    def test_added_words_render_fuller_prototype_data(self):
        response = self.client.get(
            reverse("search-results"),
            {"q": "school", "mode": "Explore"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "kiskinwahamâtowikamik")

        research_response = self.client.get(
            reverse("research"),
            {"q": "school", "mode": "Research"},
        )

        self.assertEqual(research_response.status_code, 200)
        self.assertContains(research_response, "Word Class")
        self.assertContains(research_response, "Prototype vocabulary set")

    def test_category_search_filters_topic_results(self):
        response = self.client.get(
            reverse("browse-topics"),
            {"mode": "Explore", "search_type": "category", "q": "ani"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Search words or categories")
        self.assertContains(response, "Animals")
        self.assertContains(response, 'class="browse-topic-card"', count=1, html=False)

    def test_explore_mode_word_page_links_to_select_collection(self):
        response = self.client.get(
            reverse("search-results"),
            {
                "mode": "Explore",
                "q": "rabbit",
                "back": reverse("home"),
                "search_type": "word",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add to Collection")
        self.assertContains(response, "English Word")
        self.assertContains(response, "Related Words")
        self.assertNotContains(response, 'id="collection-tools-title"', html=False)
        self.assertContains(response, reverse("select-collection"), html=False)
        self.assertContains(response, "word=rabbit", html=False)

    def test_collections_page_renders_add_word_tools_and_collections(self):
        session = self.client.session
        session["saved_words"] = ["horse", "rabbit"]
        session["collections"] = [{"name": "Animals", "words": ["horse"], "notes": "Warm-up"}]
        session.save()

        response = self.client.get(reverse("collections"), {"mode": "Explore"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add a Word")
        self.assertContains(response, "Search words or categories")
        self.assertContains(response, "Create New Collection")
        self.assertContains(response, "Animals")
        self.assertContains(response, "Warm-up")
        self.assertNotContains(response, "Saved Words")

    def test_collections_page_can_create_and_rename_collection(self):
        create_response = self.client.post(
            reverse("collections"),
            {
                "action": "create_collection",
                "mode": "Explore",
                "word": "horse",
                "collection_name": "Animal Basics",
                "collection_notes": "Warm-up vocabulary",
                "back": reverse("home"),
            },
            follow=True,
        )

        self.assertEqual(create_response.status_code, 200)
        self.assertContains(create_response, "Animal Basics")
        self.assertEqual(self.client.session["collections"][0]["words"], ["horse"])
        self.assertEqual(self.client.session["collections"][0]["notes"], "Warm-up vocabulary")

        rename_response = self.client.post(
            reverse("collections"),
            {
                "action": "save_collection",
                "mode": "Explore",
                "current_name": "Animal Basics",
                "collection_name": "Animal Set",
                "collection_notes": "Updated notes",
                "word": "horse",
                "back": reverse("home"),
            },
            follow=True,
        )

        self.assertEqual(rename_response.status_code, 200)
        self.assertContains(rename_response, "Animal Set")
        self.assertEqual(self.client.session["collections"][0]["name"], "Animal Set")
        self.assertEqual(self.client.session["collections"][0]["notes"], "Updated notes")

    def test_collections_page_can_show_export_toast(self):
        session = self.client.session
        session["collections"] = [{"name": "Animals", "words": ["horse"], "notes": ""}]
        session.save()

        response = self.client.post(
            reverse("collections"),
            {
                "action": "export_collection",
                "mode": "Explore",
                "collection_name": "Animals",
                "back": reverse("home"),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Export started")

    def test_select_collection_page_can_add_word_to_existing_collection(self):
        session = self.client.session
        session["collections"] = [{"name": "Animals", "words": [], "notes": ""}]
        session.save()

        response = self.client.post(
            reverse("select-collection"),
            {
                "action": "add_to_collection",
                "mode": "Explore",
                "word": "horse",
                "collection_name": "Animals",
                "back": reverse("search-results"),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Horse added to Animals")
        self.assertContains(response, "English Word")
        self.assertContains(response, "Add to More Collections")
        self.assertNotContains(response, "This word is saved and ready to organize.")
        self.assertNotContains(response, 'id="collection-tools-title"', html=False)
        self.assertIn("horse", self.client.session["saved_words"])
        self.assertEqual(self.client.session["collections"][0]["words"], ["horse"])

    def test_create_collection_flow_creates_collection_adds_word_and_returns(self):
        response = self.client.post(
            reverse("create-collection"),
            {
                "action": "create_collection",
                "mode": "Explore",
                "word": "horse",
                "back": reverse("select-collection"),
                "return_to": reverse("search-results"),
                "collection_name": "Animal Basics",
                "collection_notes": "Warm-up vocabulary",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Horse added to Animal Basics")
        self.assertEqual(self.client.session["collections"][0]["name"], "Animal Basics")
        self.assertEqual(self.client.session["collections"][0]["notes"], "Warm-up vocabulary")
        self.assertEqual(self.client.session["collections"][0]["words"], ["horse"])

    def test_create_collection_page_can_create_empty_collection_from_collections(self):
        response = self.client.post(
            reverse("create-collection"),
            {
                "action": "create_collection",
                "mode": "Explore",
                "back": reverse("collections"),
                "return_to": reverse("collections"),
                "collection_name": "New Set",
                "collection_notes": "General practice",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Collection created")
        self.assertEqual(self.client.session["collections"][0]["name"], "New Set")
        self.assertEqual(self.client.session["collections"][0]["notes"], "General practice")
        self.assertEqual(self.client.session["collections"][0]["words"], [])

    def test_remove_saved_word_also_removes_collection_membership(self):
        session = self.client.session
        session["saved_words"] = ["horse"]
        session["collections"] = [{"name": "Animals", "words": ["horse"], "notes": ""}]
        session.save()

        response = self.client.post(
            reverse("collections"),
            {
                "action": "remove_saved_word",
                "mode": "Explore",
                "word": "horse",
                "back": reverse("home"),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Removed from Collection")
        self.assertEqual(self.client.session["saved_words"], [])
        self.assertEqual(self.client.session["collections"][0]["words"], [])

    def test_topic_page_preserves_mode_links_and_collections_nav(self):
        response = self.client.get(
            reverse("topic-detail", args=["animals"]),
            {"mode": "Explore"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Animals")
        self.assertContains(response, "mode=Explore")
        self.assertContains(response, "Collections")

    def test_topic_page_supports_map_view_in_all_modes(self):
        response = self.client.get(
            reverse("topic-detail", args=["animals"]),
            {"mode": "Research", "view": "map"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "List")
        self.assertContains(response, "Map")
        self.assertContains(response, "Interactive category map")
        self.assertContains(response, 'data-graph-workspace', html=False)

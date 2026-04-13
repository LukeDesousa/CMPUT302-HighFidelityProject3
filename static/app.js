(() => {
    const MAX_SUGGESTIONS = 6;

    const setupToast = () => {
        const toast = document.querySelector("[data-toast]");
        if (!toast) {
            return;
        }

        window.setTimeout(() => {
            toast.classList.add("is-hidden");
            window.setTimeout(() => toast.remove(), 220);
        }, 3000);
    };

    const rankSuggestion = (suggestion, normalizedQuery) => {
        const label = suggestion.label.toLowerCase();
        const keywords = suggestion.keywords || "";

        if (label === normalizedQuery) {
            return 0;
        }

        if (label.startsWith(normalizedQuery)) {
            return 1;
        }

        if (keywords.startsWith(normalizedQuery)) {
            return 2;
        }

        return 3;
    };

    const setupSearchForms = () => {
        const searchForms = document.querySelectorAll("[data-search-form]");

        searchForms.forEach((form) => {
            const queryField = form.querySelector("[data-search-query]");
            const suggestionsPanel = form.querySelector("[data-search-suggestions]");
            const suggestionsSource = form.querySelector("[data-search-suggestions-source]");

            if (!queryField || !suggestionsPanel || !suggestionsSource) {
                return;
            }

            let suggestions = [];

            try {
                suggestions = JSON.parse(suggestionsSource.textContent);
            } catch {
                suggestions = [];
            }

            const getMatches = (query) => {
                const normalizedQuery = query.trim().toLowerCase();

                if (!normalizedQuery) {
                    return [];
                }

                return suggestions
                    .filter((suggestion) => suggestion.keywords.includes(normalizedQuery))
                    .sort((left, right) => {
                        const rankDifference = rankSuggestion(left, normalizedQuery) - rankSuggestion(right, normalizedQuery);
                        if (rankDifference !== 0) {
                            return rankDifference;
                        }

                        return left.label.localeCompare(right.label);
                    })
                    .slice(0, MAX_SUGGESTIONS);
            };

            const renderMatches = (matches) => {
                if (matches.length === 0) {
                    suggestionsPanel.hidden = true;
                    suggestionsPanel.innerHTML = "";
                    return;
                }

                suggestionsPanel.hidden = false;
                suggestionsPanel.innerHTML = `
                    <p class="search-suggestions-title">Suggestions</p>
                    <div class="search-suggestion-list">
                        ${matches.map((suggestion) => `
                            <a class="search-suggestion-chip" href="${suggestion.url}">
                                <strong>${suggestion.label}</strong>
                                <span>${suggestion.kind} · ${suggestion.meta}</span>
                            </a>
                        `).join("")}
                    </div>
                `;
            };

            const refreshSuggestions = () => {
                renderMatches(getMatches(queryField.value));
            };

            queryField.addEventListener("input", refreshSuggestions);
            queryField.addEventListener("focus", refreshSuggestions);

            queryField.addEventListener("keydown", (event) => {
                if (event.key !== "Escape") {
                    return;
                }

                suggestionsPanel.hidden = true;
            });

            form.addEventListener("submit", (event) => {
                const matches = getMatches(queryField.value);
                if (matches.length === 0) {
                    return;
                }

                event.preventDefault();
                window.location.assign(matches[0].url);
            });
        });

        document.addEventListener("click", (event) => {
            searchForms.forEach((form) => {
                const suggestionsPanel = form.querySelector("[data-search-suggestions]");
                if (!suggestionsPanel || form.contains(event.target)) {
                    return;
                }

                suggestionsPanel.hidden = true;
            });
        });
    };

    document.addEventListener("DOMContentLoaded", () => {
        setupToast();
        setupSearchForms();
    });
})();

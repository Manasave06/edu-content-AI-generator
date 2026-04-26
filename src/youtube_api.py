import urllib.parse


def search_youtube_videos(query: str, max_results: int = 6) -> list:
    """Search YouTube videos - returns direct search links."""
    try:
        from youtubesearchpython import VideosSearch
        search = VideosSearch(query, limit=max_results)
        results = search.result()
        videos = []
        for video in results.get("result", []):
            videos.append({
                "title": video.get("title", ""),
                "url": video.get("link", ""),
                "thumbnail": video.get("thumbnails", [{}])[0].get("url", ""),
                "duration": video.get("duration", ""),
                "channel": video.get("channel", {}).get("name", ""),
                "views": video.get("viewCount", {}).get("short", "")
            })
        if videos:
            return videos
        raise Exception("No results")
    except:
        # Fallback with correct query
        base = query.strip()
        topics = [
            f"{base} introduction",
            f"{base} tutorial for beginners",
            f"{base} explained simply",
            f"{base} full lecture",
            f"{base} full course free",
            f"{base} study guide"
        ]
        return [
            {
                "title": f"🔍 {t}",
                "url": f"https://www.youtube.com/results?search_query={urllib.parse.quote(t)}",
                "thumbnail": "",
                "duration": "Click to open YouTube",
                "channel": "YouTube Search",
                "views": "Free"
            }
            for t in topics[:max_results]
        ]


def get_educational_links(topic: str) -> list:
    """Get free educational website links for any topic."""
    try:
        encoded = urllib.parse.quote(topic)
        return [
            {
                "name": "📚 Khan Academy",
                "url": f"https://www.khanacademy.org/search?page_search_query={encoded}",
                "desc": "Free courses and practice exercises",
                "color": "#14BF96"
            },
            {
                "name": "📖 Wikipedia",
                "url": f"https://en.wikipedia.org/wiki/Special:Search?search={encoded}",
                "desc": "Detailed encyclopedia articles",
                "color": "#636466"
            },
            {
                "name": "🎓 MIT OpenCourseWare",
                "url": f"https://ocw.mit.edu/search/?q={encoded}",
                "desc": "Free MIT university courses",
                "color": "#A31F34"
            },
            {
                "name": "🔬 Google Scholar",
                "url": f"https://scholar.google.com/scholar?q={encoded}",
                "desc": "Academic papers and research",
                "color": "#4285F4"
            },
            {
                "name": "📝 Coursera",
                "url": f"https://www.coursera.org/search?query={encoded}",
                "desc": "Online courses from top universities",
                "color": "#0056D2"
            },
            {
                "name": "💡 TED Talks",
                "url": f"https://www.ted.com/search?q={encoded}",
                "desc": "Expert talks and ideas",
                "color": "#E62B1E"
            },
            {
                "name": "🏫 edX",
                "url": f"https://www.edx.org/search?q={encoded}",
                "desc": "Courses from Harvard MIT and more",
                "color": "#02262B"
            },
            {
                "name": "📊 Britannica",
                "url": f"https://www.britannica.com/search?query={encoded}",
                "desc": "Encyclopedia Britannica articles",
                "color": "#003366"
            },
            {
                "name": "🧪 National Geographic",
                "url": f"https://www.nationalgeographic.com/search?q={encoded}",
                "desc": "Science nature and geography",
                "color": "#FFCC00"
            }
        ]
    except Exception as e:
        return []


def get_subject_category(text: str) -> str:
    """Detect subject category from document text."""
    try:
        text_lower = text.lower()
        subjects = {
            "🔬 Science": [
                "biology", "chemistry", "physics", "cell", "molecule",
                "atom", "dna", "evolution", "genetics", "organism",
                "photosynthesis", "ecosystem", "enzyme", "protein"
            ],
            "💻 Computer Science": [
                "programming", "algorithm", "software", "computer", "code",
                "python", "database", "network", "ai", "machine learning",
                "deep learning", "neural", "data structure", "variable"
            ],
            "📐 Mathematics": [
                "equation", "calculus", "algebra", "geometry", "theorem",
                "integral", "derivative", "matrix", "probability", "statistics",
                "function", "vector", "polynomial", "trigonometry"
            ],
            "📜 History": [
                "war", "empire", "civilization", "century", "revolution",
                "ancient", "historical", "dynasty", "colonial", "medieval",
                "kingdom", "independence", "battle", "treaty"
            ],
            "🌍 Geography": [
                "country", "continent", "climate", "ocean", "mountain",
                "population", "capital", "region", "map", "river",
                "latitude", "longitude", "terrain", "weather"
            ],
            "💰 Economics": [
                "economy", "market", "supply", "demand", "inflation",
                "gdp", "trade", "finance", "investment", "business",
                "profit", "revenue", "tax", "currency", "bank"
            ],
            "🏥 Medicine": [
                "disease", "treatment", "patient", "diagnosis", "drug",
                "symptom", "clinical", "medical", "health", "hospital",
                "surgery", "vaccine", "infection", "therapy", "anatomy"
            ],
            "⚖️ Law": [
                "legal", "court", "law", "rights", "constitution",
                "justice", "legislation", "verdict", "contract",
                "crime", "judge", "lawyer", "penalty", "regulation"
            ],
            "🎨 Arts": [
                "painting", "sculpture", "music", "literature", "poetry",
                "drama", "culture", "artistic", "aesthetic", "design",
                "film", "theatre", "creative", "visual", "performance"
            ],
            "🧠 Psychology": [
                "behavior", "cognition", "emotion", "mental", "therapy",
                "personality", "learning", "memory", "brain", "psychology",
                "anxiety", "motivation", "perception", "consciousness"
            ],
            "⚗️ Chemistry": [
                "chemical", "reaction", "compound", "element", "periodic",
                "acid", "base", "oxidation", "bond", "solution",
                "titration", "catalyst", "organic", "inorganic"
            ],
            "🌱 Environmental Science": [
                "environment", "pollution", "climate change", "ecology",
                "biodiversity", "conservation", "sustainability", "carbon",
                "renewable", "deforestation", "habitat", "species"
            ],
            "🏛️ Political Science": [
                "government", "democracy", "policy", "election", "political",
                "parliament", "president", "constitution", "voting", "party",
                "diplomacy", "sovereignty", "federalism"
            ],
            "📡 Engineering": [
                "mechanical", "electrical", "civil", "structural", "circuit",
                "force", "stress", "energy", "power", "voltage",
                "construction", "design", "material", "system"
            ]
        }

        scores = {}
        for subject, keywords in subjects.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[subject] = score

        if scores:
            return max(scores, key=scores.get)
        return "📚 General Studies"

    except Exception as e:
        return "📚 General Studies"


def get_study_schedule(weak_topics: list, available_hours: int = 2) -> list:
    """Generate a simple study schedule based on weak topics."""
    try:
        if not weak_topics:
            return []

        schedule = []
        days = ["Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday", "Saturday", "Sunday"]
        hours_per_topic = max(1, available_hours // max(len(weak_topics), 1))

        for i, topic in enumerate(weak_topics[:7]):
            schedule.append({
                "day": days[i % 7],
                "topic": topic,
                "hours": hours_per_topic,
                "activities": [
                    f"📖 Read notes on {topic}",
                    f"📝 Take a quiz on {topic}",
                    f"🃏 Review flashcards for {topic}",
                    f"🎥 Watch a video about {topic}"
                ]
            })
        return schedule

    except Exception as e:
        return []


def get_performance_insights(quiz_results: list) -> dict:
    """Analyze quiz results and return insights."""
    try:
        if not quiz_results:
            return {}

        scores = [r[1]/r[2]*100 for r in quiz_results]
        avg_score = sum(scores) / len(scores)
        best_score = max(scores)
        worst_score = min(scores)

        if len(scores) >= 2:
            recent = sum(scores[:3]) / min(3, len(scores))
            older = sum(scores[-3:]) / min(3, len(scores))
            if recent > older:
                trend = "📈 Improving"
            elif recent < older:
                trend = "📉 Needs work"
            else:
                trend = "➡️ Stable"
        else:
            trend = "➡️ Not enough data"

        difficulty_scores = {}
        for r in quiz_results:
            diff = r[5] if len(r) > 5 else "Medium"
            if diff not in difficulty_scores:
                difficulty_scores[diff] = []
            difficulty_scores[diff].append(r[1]/r[2]*100)

        diff_avg = {k: sum(v)/len(v) for k, v in difficulty_scores.items()}

        recommendations = []
        if avg_score < 50:
            recommendations.append("📚 Start with Easy level to build confidence")
            recommendations.append("🃏 Review flashcards before taking quizzes")
            recommendations.append("📖 Re-read the study notes carefully")
        elif avg_score < 70:
            recommendations.append("🎯 Focus on Medium level questions")
            recommendations.append("💡 Review explanations for wrong answers")
            recommendations.append("🔄 Retake quizzes on weak topics")
        else:
            recommendations.append("🏆 Try Hard level questions for a challenge")
            recommendations.append("🎓 You are doing great keep it up!")
            recommendations.append("📊 Track your streak to maintain momentum")

        return {
            "avg_score": avg_score,
            "best_score": best_score,
            "worst_score": worst_score,
            "trend": trend,
            "diff_avg": diff_avg,
            "recommendations": recommendations,
            "total_quizzes": len(quiz_results)
        }

    except Exception as e:
        return {}
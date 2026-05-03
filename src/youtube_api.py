import urllib.parse
import requests


# ── API 1: YouTube Search ─────────────────────────────────────────────────
def search_youtube_videos(query: str, max_results: int = 6) -> list:
    """Search YouTube videos with fallback."""
    try:
        from youtubesearchpython import VideosSearch
        search = VideosSearch(query, limit=max_results)
        results = search.result()
        videos = []
        for video in results.get("result", []):
            videos.append({
                "title": video.get("title", ""),
                "url": video.get("link", ""),
                "duration": video.get("duration", ""),
                "channel": video.get("channel", {}).get("name", ""),
                "views": video.get("viewCount", {}).get("short", "")
            })
        if videos:
            return videos
        raise Exception("No results")
    except:
        base = query.strip()
        topics = [
            f"{base} introduction",
            f"{base} tutorial for beginners",
            f"{base} explained",
            f"{base} full lecture",
            f"{base} full course free",
            f"{base} study guide"
        ]
        return [
            {
                "title": f"🔍 {t}",
                "url": f"https://www.youtube.com/results?search_query={urllib.parse.quote(t)}",
                "duration": "Click to open YouTube",
                "channel": "YouTube Search",
                "views": "Free"
            }
            for t in topics[:max_results]
        ]


# ── API 2: Wikipedia ──────────────────────────────────────────────────────
def search_wikipedia(topic: str) -> dict:
    """Search Wikipedia for topic summary."""
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(topic)}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("title", ""),
                "summary": data.get("extract", "")[:500] + "...",
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                "image": data.get("thumbnail", {}).get("source", "")
            }
    except:
        pass
    return {}


# ── API 3: Open Library ───────────────────────────────────────────────────
def search_books(topic: str, max_results: int = 4) -> list:
    """Search Open Library for free books."""
    try:
        url = f"https://openlibrary.org/search.json?q={urllib.parse.quote(topic)}&limit={max_results}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            books = []
            for doc in data.get("docs", [])[:max_results]:
                books.append({
                    "title": doc.get("title", ""),
                    "author": ", ".join(doc.get("author_name", ["Unknown"])[:2]),
                    "year": doc.get("first_publish_year", ""),
                    "url": f"https://openlibrary.org{doc.get('key', '')}"
                })
            return books
    except:
        pass
    return []


# ── API 4: Educational Links ──────────────────────────────────────────────
def get_educational_links(topic: str) -> list:
    """Get free educational website links."""
    try:
        encoded = urllib.parse.quote(topic)
        return [
            {
                "name": "📚 Khan Academy",
                "url": f"https://www.khanacademy.org/search?page_search_query={encoded}",
                "desc": "Free courses and exercises",
                "color": "#14BF96"
            },
            {
                "name": "📖 Wikipedia",
                "url": f"https://en.wikipedia.org/wiki/Special:Search?search={encoded}",
                "desc": "Encyclopedia articles",
                "color": "#636466"
            },
            {
                "name": "🎓 MIT OpenCourseWare",
                "url": f"https://ocw.mit.edu/search/?q={encoded}",
                "desc": "Free MIT courses",
                "color": "#A31F34"
            },
            {
                "name": "🔬 Google Scholar",
                "url": f"https://scholar.google.com/scholar?q={encoded}",
                "desc": "Academic papers",
                "color": "#4285F4"
            },
            {
                "name": "📝 Coursera",
                "url": f"https://www.coursera.org/search?query={encoded}",
                "desc": "University courses",
                "color": "#0056D2"
            },
            {
                "name": "💡 TED Talks",
                "url": f"https://www.ted.com/search?q={encoded}",
                "desc": "Expert talks",
                "color": "#E62B1E"
            },
            {
                "name": "🏫 edX",
                "url": f"https://www.edx.org/search?q={encoded}",
                "desc": "Harvard MIT courses",
                "color": "#02262B"
            },
            {
                "name": "📚 Open Library",
                "url": f"https://openlibrary.org/search?q={encoded}",
                "desc": "Free books online",
                "color": "#CC4B00"
            },
            {
                "name": "🧪 National Geographic",
                "url": f"https://www.nationalgeographic.com/search?q={encoded}",
                "desc": "Science and nature",
                "color": "#FFCC00"
            }
        ]
    except:
        return []


# ── Subject Detection ─────────────────────────────────────────────────────
def get_subject_category(text: str) -> str:
    """Detect subject category from document text."""
    try:
        text_lower = text.lower()
        subjects = {
            "🔬 Science": ["biology","chemistry","physics","cell","molecule","atom","dna","evolution","genetics","organism","photosynthesis","ecosystem","enzyme","protein"],
            "💻 Computer Science": ["programming","algorithm","software","computer","code","python","database","network","ai","machine learning","deep learning","neural","data structure","variable"],
            "📐 Mathematics": ["equation","calculus","algebra","geometry","theorem","integral","derivative","matrix","probability","statistics","function","vector","polynomial","trigonometry"],
            "📜 History": ["war","empire","civilization","century","revolution","ancient","historical","dynasty","colonial","medieval","kingdom","independence","battle","treaty"],
            "🌍 Geography": ["country","continent","climate","ocean","mountain","population","capital","region","map","river","latitude","longitude","terrain","weather"],
            "💰 Economics": ["economy","market","supply","demand","inflation","gdp","trade","finance","investment","business","profit","revenue","tax","currency","bank"],
            "🏥 Medicine": ["disease","treatment","patient","diagnosis","drug","symptom","clinical","medical","health","hospital","surgery","vaccine","infection","therapy","anatomy"],
            "⚖️ Law": ["legal","court","law","rights","constitution","justice","legislation","verdict","contract","crime","judge","lawyer","penalty","regulation"],
            "🎨 Arts": ["painting","sculpture","music","literature","poetry","drama","culture","artistic","aesthetic","design","film","theatre","creative","visual","performance"],
            "🧠 Psychology": ["behavior","cognition","emotion","mental","therapy","personality","learning","memory","brain","psychology","anxiety","motivation","perception","consciousness"],
            "⚗️ Chemistry": ["chemical","reaction","compound","element","periodic","acid","base","oxidation","bond","solution","titration","catalyst","organic","inorganic"],
            "🌱 Environmental Science": ["environment","pollution","climate change","ecology","biodiversity","conservation","sustainability","carbon","renewable","deforestation","habitat","species"],
            "🏛️ Political Science": ["government","democracy","policy","election","political","parliament","president","constitution","voting","party","diplomacy","sovereignty","federalism"],
            "📡 Engineering": ["mechanical","electrical","civil","structural","circuit","force","stress","energy","power","voltage","construction","design","material","system"]
        }
        scores = {}
        for subject, keywords in subjects.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[subject] = score
        if scores:
            return max(scores, key=scores.get)
        return "📚 General Studies"
    except:
        return "📚 General Studies"


# ── Adaptive Difficulty ───────────────────────────────────────────────────
def get_adaptive_difficulty(quiz_results: list) -> str:
    """Calculate adaptive difficulty based on past performance."""
    try:
        if not quiz_results:
            return "Medium"
        recent = quiz_results[:5]
        scores = [r[1]/r[2]*100 for r in recent]
        avg = sum(scores) / len(scores)
        if avg >= 80:
            return "Hard"
        elif avg >= 50:
            return "Medium"
        else:
            return "Easy"
    except:
        return "Medium"


# ── Performance Insights ──────────────────────────────────────────────────
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
            trend = "📈 Improving" if recent > older else "📉 Needs work" if recent < older else "➡️ Stable"
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
            "total_quizzes": len(quiz_results),
            "adaptive_difficulty": get_adaptive_difficulty(quiz_results)
        }
    except:
        return {}


# ── Study Schedule ────────────────────────────────────────────────────────
def get_study_schedule(weak_topics: list, available_hours: int = 2) -> list:
    """Generate study schedule."""
    try:
        if not weak_topics:
            return []
        schedule = []
        days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
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
    except:
        return []
def generate_study_content(text: str) -> dict:
    """Generate comprehensive study content — summary, key points, mind map, exam tips."""
    llm = get_llm()
    prompt = f"""
You are an expert educator. Analyze the text and generate comprehensive study content.

Return ONLY a valid JSON object with these exact keys:
- "summary": A clear 3-4 sentence summary of the main topic
- "key_points": List of 6-8 most important points to remember
- "mind_map": Dictionary with main topic as key and list of subtopics as value
- "exam_tips": List of 4-5 tips for answering exam questions on this topic
- "difficult_terms": List of objects with "term" and "definition" for 5 hard words
- "one_liner": One powerful sentence that captures the entire topic

Text:
{text[:3000]}

Return ONLY the JSON object. No extra text. No markdown.
"""
    response = llm.invoke([
        SystemMessage(content="You are a study content generator. Output only valid JSON."),
        HumanMessage(content=prompt)
    ])
    raw = response.content.strip()
    clean = re.sub(r"```json|```", "", raw, flags=re.MULTILINE).strip()
    return json.loads(clean)
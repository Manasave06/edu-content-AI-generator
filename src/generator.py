def generate_quiz(text: str, num_questions: int, difficulty: str = "Medium") -> list:
    """Generate MCQ questions with strict difficulty level."""
    llm = get_llm()

    difficulty_instructions = {
        "Easy": """
EASY LEVEL RULES - STRICTLY FOLLOW:
- Ask ONLY about basic definitions and simple facts
- Questions should start with: "What is...", "Which of the following is...", "Define..."
- Answer should be directly stated in the text
- Wrong options should be obviously incorrect
- A student reading for first time should answer correctly
- Example: "What is Artificial Intelligence?" or "Which term means..."
- DO NOT ask about processes, mechanisms or analysis
""",
        "Medium": """
MEDIUM LEVEL RULES - STRICTLY FOLLOW:
- Ask about HOW things work and WHY things happen
- Questions should start with: "How does...", "Why is...", "What happens when...", "Which process..."
- Requires understanding, not just memorization
- Wrong options should be plausible but clearly wrong on reflection
- Example: "How does machine learning differ from traditional programming?"
- DO NOT ask simple definitions (that is Easy level)
- DO NOT ask deep analysis (that is Hard level)
""",
        "Hard": """
HARD LEVEL RULES - STRICTLY FOLLOW:
- Ask about ANALYSIS, COMPARISON, EVALUATION and CRITICAL THINKING
- Questions should start with: "Analyze...", "Compare...", "Evaluate...", "Which combination...", "In what scenario..."
- Requires deep understanding and connecting multiple concepts
- All 4 options should seem plausible — only an expert can distinguish
- Example: "Which combination of factors would most likely cause..." or "Evaluate the trade-off between..."
- DO NOT ask simple definitions or basic facts
- These questions should challenge even students who studied the topic
"""
    }

    prompt = f"""
You are an expert university professor creating a {difficulty.upper()} level exam.

{difficulty_instructions[difficulty]}

TASK: Generate EXACTLY {num_questions} questions at {difficulty} level.

CRITICAL RULES:
- Every question MUST follow the {difficulty} level rules above
- Questions must be UNIQUE and test DIFFERENT concepts
- NEVER repeat similar questions
- NEVER ask about: emails, phone numbers, author names, institution names,
  dates of publication, journal names, page numbers, contact details
- ONLY ask about: concepts, mechanisms, processes, classifications,
  applications, effects, definitions, comparisons

Return ONLY a valid JSON array with {num_questions} objects:
- "question": the question string
- "options": list of exactly 4 answer strings
- "answer": correct option (must exactly match one item in options)
- "explanation": detailed explanation of why this is correct
- "difficulty": "{difficulty}"

Text to generate from:
{text[:3000]}

Return ONLY the JSON array. No extra text. No markdown fences.
"""
    response = llm.invoke([
        SystemMessage(content=f"""You are a strict {difficulty} level exam question generator.
You MUST follow the {difficulty} level rules exactly.
Easy = definitions only. Medium = understanding/application. Hard = analysis/critical thinking.
Never mix difficulty levels. Never ask about document metadata.
Output only valid JSON arrays."""),
        HumanMessage(content=prompt)
    ])
    return parse_json(response.content.strip())


def generate_true_false(text: str, num_questions: int, difficulty: str = "Medium") -> list:
    """Generate True/False questions with strict difficulty."""
    llm = get_llm()

    difficulty_instructions = {
        "Easy": """
EASY LEVEL:
- Simple factual statements directly from the text
- Obviously true or obviously false
- Example: "Artificial Intelligence simulates human intelligence. (True)"
- Student just needs to recall basic facts
""",
        "Medium": """
MEDIUM LEVEL:
- Statements about processes, relationships and applications
- Requires understanding to determine true/false
- Include some tricky statements that seem true but are false
- Example: "Machine learning always requires labeled data to function."
- Student needs to understand concepts, not just recall facts
""",
        "Hard": """
HARD LEVEL:
- Complex statements combining multiple concepts
- Statements with subtle errors that require deep knowledge to catch
- Example: "Deep learning outperforms traditional ML in all scenarios regardless of data size."
- Only an expert who deeply understands the topic can answer correctly
- Include nuanced statements where common misconceptions lead to wrong answers
"""
    }

    prompt = f"""
You are an expert professor creating {difficulty.upper()} level True/False questions.

{difficulty_instructions[difficulty]}

Generate EXACTLY {num_questions} True/False statements at {difficulty} level.

RULES:
- Follow the {difficulty} level rules strictly
- Mix of True and False answers (roughly 50/50)
- NEVER ask about emails, authors, institutions, dates or document metadata
- Each statement must test a DIFFERENT concept

Return ONLY a valid JSON array:
- "question": a clear statement (true or false)
- "answer": exactly "True" or "False"
- "explanation": why the statement is true or false
- "difficulty": "{difficulty}"

Text:
{text[:3000]}

Return ONLY the JSON array. No extra text. No markdown.
"""
    response = llm.invoke([
        SystemMessage(content=f"You are a {difficulty} level True/False generator. Output only valid JSON arrays."),
        HumanMessage(content=prompt)
    ])
    return parse_json(response.content.strip())


def generate_fill_blanks(text: str, num_questions: int, difficulty: str = "Medium") -> list:
    """Generate Fill in the Blank questions with strict difficulty."""
    llm = get_llm()

    difficulty_instructions = {
        "Easy": """
EASY LEVEL:
- Blank should be a KEY TERM or SIMPLE WORD directly from the text
- The sentence makes it very obvious what word goes in the blank
- Example: "_____ Intelligence is the simulation of human intelligence by computers."
- Hint should almost give away the answer
- One word answers only
""",
        "Medium": """
MEDIUM LEVEL:
- Blank should be a CONCEPT or PROCESS name
- Requires understanding of the topic to fill correctly
- Example: "The process by which machines learn from data without explicit programming is called _____."
- Hint should be helpful but not give it away
- One or two word answers
""",
        "Hard": """
HARD LEVEL:
- Blank should be a SPECIFIC TECHNICAL TERM or COMPLEX CONCEPT
- Multiple words in the sentence could fit but only one is technically correct
- Example: "In neural networks, the _____ layer is responsible for extracting spatial hierarchies from images."
- Hint should be cryptic and challenging
- Requires deep knowledge to answer correctly
"""
    }

    prompt = f"""
You are an expert professor creating {difficulty.upper()} level Fill-in-the-Blank questions.

{difficulty_instructions[difficulty]}

Generate EXACTLY {num_questions} fill-in-the-blank questions at {difficulty} level.

RULES:
- Follow {difficulty} level rules strictly
- Use _____ to indicate the blank
- NEVER ask about emails, authors, institutions, dates or document metadata
- Each question must test a DIFFERENT concept

Return ONLY a valid JSON array:
- "question": sentence with _____ for the blank
- "answer": correct word or phrase
- "hint": helpful hint for the student
- "explanation": why this is the correct answer
- "difficulty": "{difficulty}"

Text:
{text[:3000]}

Return ONLY the JSON array. No extra text. No markdown.
"""
    response = llm.invoke([
        SystemMessage(content=f"You are a {difficulty} level fill-in-the-blank generator. Output only valid JSON arrays."),
        HumanMessage(content=prompt)
    ])
    return parse_json(response.content.strip())
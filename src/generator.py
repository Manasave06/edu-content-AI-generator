def generate_quiz(text: str, num_questions: int) -> list:
    """Generate meaningful educational questions only."""
    llm = get_llm()
    prompt = f"""
You are an expert educator creating exam questions for college students.

YOUR TASK: Generate exactly {num_questions} high-quality exam questions.

STRICTLY FORBIDDEN - NEVER ask about:
- Email addresses or contact information
- Author names or researcher names  
- Institution or college names
- Dates of publication or submission
- Journal names or article titles
- Page numbers or volume numbers
- Phone numbers or addresses
- Funding sources or acknowledgements
- Any metadata about the document itself

ONLY ASK ABOUT:
- Scientific concepts and definitions
- Biological/chemical/medical processes
- How something works or functions
- Causes and effects
- Classification and types
- Treatment methods or applications
- Key findings and conclusions
- Important terminology
- Mechanisms and pathways

Each question MUST be something a professor would ask in an exam.
Each question MUST test actual subject knowledge.

Return ONLY a valid JSON array with exactly {num_questions} objects.
Each object must have:
- "question": exam-worthy question string
- "options": list of exactly 4 answer strings
- "answer": correct option (must exactly match one item in options)
- "explanation": why this answer is correct

Text to generate questions from:
{text[:3000]}

Return ONLY the JSON array. No extra text. No markdown fences.
"""
    response = llm.invoke([
        SystemMessage(content="""You are a strict exam question generator.
You ONLY create questions about subject concepts, processes, definitions and mechanisms.
You NEVER create questions about emails, authors, dates, institutions or document metadata.
Treat every document like a textbook chapter - only ask about the academic content.
Output only valid JSON arrays."""),
        HumanMessage(content=prompt)
    ])
    return parse_json(response.content.strip())
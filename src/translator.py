from googletrans import Translator

translator = Translator()

def translate_text(text: str, target_lang: str) -> str:
    try:
        if target_lang == "en":
            return text
        result = translator.translate(text, dest=target_lang)
        return result.text
    except:
        return text

def translate_quiz(questions: list, target_lang: str) -> list:
    if target_lang == "en":
        return questions
    translated = []
    for q in questions:
        try:
            translated.append({
                "question": translate_text(q["question"], target_lang),
                "options": [translate_text(o, target_lang) for o in q["options"]],
                "answer": translate_text(q["answer"], target_lang),
                "explanation": translate_text(q.get("explanation",""), target_lang)
            })
        except:
            translated.append(q)
    return translated

def translate_flashcards(cards: list, target_lang: str) -> list:
    if target_lang == "en":
        return cards
    translated = []
    for card in cards:
        try:
            translated.append({
                "front": translate_text(card["front"], target_lang),
                "back": translate_text(card["back"], target_lang)
            })
        except:
            translated.append(card)
    return translated
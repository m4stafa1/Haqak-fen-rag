import ollama
from app.core.config import settings

def build_prompt(query: str, retrieved_chunks: list[dict]) -> str:
    context = "\n\n".join(
        f"[مصدر: {c['source']}]\n{c['text']}" for c in retrieved_chunks
    )
    return f"""أنت مساعد توعية لحقوق المستهلك في مصر. أجب بالاعتماد فقط على السياق أدناه،
باللغة العربية الفصحى فقط، بدون أي حروف أو كلمات من أي لغة أخرى.

خطوات الإجابة:
1. حدد أولاً: هل السؤال عن "حق استرجاع/استبدال سلعة" أم عن موضوع آخر (شكوى، ضمان، التزام مورد...)؟
2. إذا كان عن استرجاع سلعة محددة: تحقق هل هذه السلعة مذكورة ضمن قائمة استثناءات في السياق.
   إن وُجدت، فالحق لا ينطبق عليها. إن لم توجد، فالحق العام ينطبق.
3. إذا كان السؤال عن موضوع آخر غير الاسترجاع، أجب مباشرة من المعلومات ذات الصلة في السياق
   بدون أي إشارة للاستثناءات.
4. إذا لم يحتوِ السياق على إجابة كافية، قل ذلك صراحة.

في نهاية إجابتك، اذكر المصدر.
هذه معلومات عامة للتوعية وليست استشارة قانونية.

السياق:
{context}

سؤال المستخدم: {query}

الإجابة (بالعربية فقط):"""

def generate_answer(query: str, retrieved_chunks: list[dict]) -> str:
    prompt = build_prompt(query, retrieved_chunks)
    response = ollama.generate(
        model=settings.ollama_model,
        prompt=prompt,
        options={"temperature": 0}
    )
    return response["response"]
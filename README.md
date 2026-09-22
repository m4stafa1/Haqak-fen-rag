#  حقك فين؟ (Haqak Fen)

**مساعد ذكاء اصطناعي لتوعية المستهلك المصري بحقوقه — مبني بنظام RAG (Retrieval-Augmented Generation) ومعتمد بالكامل على مصادر جهاز حماية المستهلك المصري الرسمية.**

> مشروع تخرج فردي — ITI Level 2 Summer Training

---

## نظرة عامة (Overview)

قوانين ولوائح حماية المستهلك في مصر طويلة ومكتوبة بلغة قانونية معقدة، والمستهلك غالبًا لا يعرف حقوقه الأساسية: مدة الاسترجاع، الاستثناءات، إجراءات تقديم الشكوى. المعلومة الرسمية الصحيحة موجودة لكنها مبعثرة بين مصادر متعددة.

**حقك فين؟** يحل هذه المشكلة عبر نظام RAG عربي يجاوب على أسئلة المستهلك بالاعتماد **فقط** على نصوص رسمية من جهاز حماية المستهلك (CPA) — لا على المعرفة العامة للنموذج — ويذكر المصدر في كل إجابة.

 **إخلاء مسؤولية:** هذا النظام يقدّم معلومات عامة للتوعية بناءً على مصادر رسمية، وهو **ليس بديلاً عن استشارة قانونية شخصية**.

---

##  الـ Architecture

```
   ┌──────────────┐     ┌───────────────────┐     ┌──────────────┐
   │     Data     │ ──▶ │      Notebook       │ ──▶ │ Vector Store │
   │ (Law+Guides) │     │ Clean→Chunk→Embed   │     │   (Chroma)   │
   └──────────────┘     └───────────────────┘     └───────┬──────┘
                                                            │ loaded once
                                                            │ at startup
                                                    ┌───────▼──────┐
                                                    │   Backend     │
                                                    │ FastAPI+Ollama│
                                                    └───────┬──────┘
                                                            │ HTTP
                                                    ┌───────▼──────┐
                                                    │   Frontend    │
                                                    │  (Streamlit)  │
                                                    └───────────────┘
```

الموديل (Embedding + LLM) ومخزن المتجهات (Vector Store) يتم تحميلهم **مرة واحدة فقط** عند إقلاع السيرفر (FastAPI `lifespan`)، وليس مع كل طلب.

---

##  Tech Stack

| المكوّن | التقنية |
|---|---|
| اللغة | Python 3.11 |
| Backend Framework | FastAPI |
| Vector Database | ChromaDB (persistent) |
| Embedding Model | `paraphrase-multilingual-MiniLM-L12-v2` |
| LLM | Ollama — `qwen2.5:3b` (محلي، temperature=0) |
| Frontend | Streamlit (واجهة شات، دعم RTL كامل) |
| PDF Parsing | pypdf / pdfplumber |

---

##  هيكل المشروع (Project Structure)

```
haqak-fen/
├── notebooks/
│   └── rag_pipeline.ipynb        # تنظيف، chunking، embeddings، تقييم
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app + lifespan + CORS
│   │   ├── api/routes/query.py   # GET /health, POST /query
│   │   ├── core/config.py        # الإعدادات من .env
│   │   ├── schemas/query.py      # QueryRequest / QueryResponse
│   │   ├── services/
│   │   │   ├── retrieval.py      # تحميل الـ vector store + الاسترجاع
│   │   │   └── generation.py     # بناء الـ prompt + استدعاء Ollama
│   │   └── utils/logging_config.py
│   ├── tests/test_query.py
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── app.py                    # واجهة Streamlit
│   ├── api_client.py             # التواصل مع الـ backend
│   ├── .env
│   └── requirements.txt
├── data/
│   ├── laws/                     # القانون الأساسي
│   ├── official_guides/          # الأسئلة المتكررة + تعريفات
│   ├── complaints/                # إجراءات الشكاوى
│   └── vector_store/              # يُنتج من النوتبوك (غير مرفوع على GitHub)
├── .gitignore
└── README.md
```

---

##  وصف الدومين والبيانات (Data)

الـ corpus مبني بالكامل من مصادر رسمية لجهاز حماية المستهلك المصري (CPA):

| المستند | النوع | المحتوى |
|---|---|---|
| قانون حماية المستهلك رقم 181/2018 | PDF | النص القانوني الكامل (32 صفحة) |
| الأسئلة المتكررة (CPA) | TXT | سياسة الاستبدال والاسترجاع والضمان |
| تعريفات | TXT | تعريفات قانونية + تفاصيل حق الاسترجاع |
| كيف تتقدم بشكوى | TXT | قنوات وإجراءات ومستندات الشكوى |

**ملفات مستبعدة (وتم توثيق السبب في النوتبوك):**
- اللائحة التنفيذية — PDF ممسوح ضوئيًا بلا نص قابل للاستخراج (يحتاج OCR خارج نطاق الوقت المتاح)
- صفحة "نصائح عامة" — تبيّن أنها صفحة فهرس لنشرات موسمية غير ذات صلة بنطاق المشروع

**استراتيجية الـ Chunking:** تقسيم ثابت الحجم (500 حرف، overlap 100 حرف) — تم تفضيله على semantic chunking لضمان الدقة والسرعة ضمن الوقت المتاح، مع نسبة overlap 20% لتقليل خطر قطع الشروط القانونية عند حدود الـ chunks.

---

##  التثبيت والتشغيل (Setup)

### المتطلبات
- Python 3.11
- [Ollama](https://ollama.com/download) مثبّت ومشغّل
- Git

### 1. تحميل موديل الـ LLM

```bash
ollama pull qwen2.5:3b
```

### 2. تجهيز الـ Notebook وبناء الـ Vector Store

```bash
cd notebooks
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install jupyter pandas numpy chromadb sentence-transformers pypdf ollama python-dotenv
jupyter notebook rag_pipeline.ipynb
```
شغّل كل الخلايا بالترتيب (Kernel → Restart & Run All) — هذا ينتج مخزن المتجهات في `data/vector_store/`.

### 3. تشغيل الـ Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt

copy .env.example .env      # وعدّل القيم لو لزم (Windows)
# cp .env.example .env      # macOS/Linux

python -m uvicorn app.main:app --reload
```
تأكد إن `/docs` بيفتح على: `http://localhost:8000/docs`

### 4. تشغيل الـ Frontend

```bash
cd frontend
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
هيفتح تلقائيًا على: `http://localhost:8501`

 **الـ backend لازم يكون شغال قبل ما تفتح الـ frontend.**

---

##  متغيرات البيئة (Environment Variables)

### `backend/.env`

| المتغير | الوصف | مثال |
|---|---|---|
| `VECTOR_STORE_PATH` | مسار مخزن Chroma على الديسك | `../data/vector_store` |
| `COLLECTION_NAME` | اسم الـ collection في Chroma | `cpa_consumer_rights` |
| `EMBEDDING_MODEL` | موديل الـ embeddings | `paraphrase-multilingual-MiniLM-L12-v2` |
| `OLLAMA_MODEL` | موديل الـ LLM في Ollama | `qwen2.5:3b` |
| `CORS_ORIGINS` | أصل الـ frontend المسموح له | `http://localhost:8501` |

### `frontend/.env`

| المتغير | الوصف | مثال |
|---|---|---|
| `API_BASE_URL` | رابط الـ backend | `http://localhost:8000` |

---

##  API Reference

### `GET /health`
فحص إن السيرفر شغال.

**Response:**
```json
{ "status": "ok" }
```

### `POST /query`
إرسال سؤال واستقبال إجابة مبنية على المصادر الرسمية.

**Request:**
```json
{ "question": "ما هي مدة الاسترجاع للسلعة المعيبة؟" }
```

**Response:**
```json
{
  "answer": "مدة الاسترجاع للسلعة المعيبة هي 30 يوم من تاريخ الاستلام.",
  "sources": [
    "data/official_guides/اسئلة متكررة.txt",
    "data/official_guides/page_text_تعريف.txt"
  ]
}
```

**مثال cURL:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "ما هي مدة الاسترجاع للسلعة المعيبة؟"}'
```

---

##  نتائج التقييم (Evaluation)

تم اختبار النظام على 7 أسئلة تمثيلية تغطي: مدة الاسترجاع، الاستثناءات، إجراءات الشكوى، المستندات المطلوبة، والتزامات المورد.

| السؤال | التقييم |
|---|---|
| مدة استرجاع السلعة المعيبة |  صحيح ومؤسس على المصدر |
| استرجاع الملابس الداخلية بعد فتح الغلاف |  عدم ثبات — موثّق كـ Known Limitation |
| جهاز فيه عيب بعد أسبوعين |  صحيح ومؤسس على المصدر |
| طرق تقديم الشكوى |  صحيح ومؤسس على المصدر |
| المستندات المطلوبة للشكوى | صحيح ومؤسس على المصدر |
| استرجاع الكتب والمجلات |  صحيح ومؤسس على المصدر |
| التزام المورد عند وجود عيب |  صحيح ومؤسس على المصدر |

**النتيجة: 6/7 (≈86%)** إجابات صحيحة ومبنية بالكامل على المصدر المسترجع.

###  Known Limitations
1. **عدم ثبات الاستدلال المنطقي على الاستثناءات المتداخلة:** الموديل الصغير (`qwen2.5:3b`) لم يطبّق منطق استثناءات الاسترجاع بثبات كامل عبر كل الأسئلة، رغم توفر الـ grounding الصحيح في السياق المسترجع في كل الحالات. تم تحسين الدقة بشكل ملموس عبر Chain-of-Thought prompting، لكن لم يتم الوصول لثبات 100%. **التوصية:** استخدام موديل أكبر (7B+) أو إضافة طبقة تحقق منفصلة (verification layer) في نسخة إنتاجية.
2. **ضعف الحساسية الدلالية للاستعلامات الإجرائية:** لوحظ أن نموذج الـ embedding متعدد اللغات أظهر حساسية محدودة للفرق بين محتوى "إجرائي" (كيفية تقديم شكوى) ومحتوى "تعريفي" (تعريفات عامة) في النصوص العربية القصيرة، مما أثّر على ترتيب نتائج الاسترجاع. تمت معالجته جزئيًا بإضافة keyword-based fallback بسيط لكلمة "شكوى". **التوصية:** موديل embedding عربي متخصص (AraBERT أو E5-multilingual) في نسخة مستقبلية.
3. **بيانات مستبعدة:** اللائحة التنفيذية (PDF ممسوح ضوئيًا) وصفحة "نصائح عامة" (فهرس غير ذي صلة) — راجع قسم البيانات أعلاه.

---



##  التطوير المستقبلي (Future Work)

- موديل embedding عربي متخصص لتحسين دقة الاسترجاع
- Evidence Card منظّمة + توليد مسودة شكوى رسمية تلقائيًا
- طبقة تحقق منفصلة (verification layer) لأسئلة الاستثناءات القانونية
- تقييم أوسع (30+ سؤال) وربط مصادر رسمية إضافية

---

## 👤 المطوّر

**Mustafa Ahmed**
[GitHub](https://github.com/m4stafa1) · [LinkedIn](https://linkedin.com/in/mustafa-ahmed-ai)

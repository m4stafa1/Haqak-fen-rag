import streamlit as st
from api_client import ask_question, check_health, APIError

st.set_page_config(
    page_title="حقك فين؟ - مساعد حقوق المستهلك",
    page_icon="⚖️",
    layout="centered",
)

# دعم RTL للعربي
st.markdown(
    """
    <style>
    .stApp { direction: rtl; text-align: right; }
    .stChatMessage { direction: rtl; text-align: right; }
    .stTextInput input { direction: rtl; text-align: right; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("⚖️ حقك فين؟")
st.caption("مساعد توعية لحقوق المستهلك في مصر — إجابات مبنية على مصادر جهاز حماية المستهلك الرسمية")

st.info(
    "ℹ️ هذا النظام يقدّم معلومات عامة للتوعية بناءً على مصادر رسمية، وليس استشارة قانونية شخصية.",
    icon="ℹ️",
)

# فحص إن الـ backend شغال
if not check_health():
    st.error("⚠️ السيرفر (Backend) مش شغال حاليًا. شغّل الـ backend الأول ثم أعد تحميل الصفحة.")
    st.stop()

# تخزين المحادثة في session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة السابقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander("📄 المصادر"):
                for src in msg["sources"]:
                    st.markdown(f"- `{src}`")

# مربع إدخال السؤال
if question := st.chat_input("اكتب سؤالك عن حقوقك كمستهلك..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("جاري البحث في المصادر الرسمية..."):
            try:
                result = ask_question(question)
                answer = result.get("answer", "لم يتم العثور على إجابة.")
                sources = result.get("sources", [])

                st.markdown(answer)
                if sources:
                    with st.expander("📄 المصادر"):
                        for src in sources:
                            st.markdown(f"- `{src}`")

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer, "sources": sources}
                )
            except APIError as e:
                error_msg = f"❌ {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# زرار مسح المحادثة
with st.sidebar:
    st.markdown("### حقك فين؟")
    st.markdown("مساعد ذكاء اصطناعي لتوعية المستهلك المصري بحقوقه، معتمد على مصادر رسمية من جهاز حماية المستهلك.")
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.rerun()

        
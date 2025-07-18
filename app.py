# app.py — DreamDate AI (Streamlit + Groq)
import streamlit as st
from openai import OpenAI  # openai>=1.1.0

# --- 1. Groq client ---
client = OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)
MODEL = "llama3-70b-8192"

# --- 2. Анкета (sidebar) ---
st.title("DreamDate AI — тренируйся в дейтинге")
with st.sidebar:
    st.header("Параметры анкеты")
    gender   = st.selectbox("Пол персонажа", ["Девушка", "Парень", "Небинарный"])
    age      = st.slider("Возраст", 18, 60, 25)
    city     = st.text_input("Город/часовой пояс", "Москва")
    
    st.markdown("### Внешний вайб")
    fashion  = st.selectbox("Стиль одежды", ["Casual", "Спорт‑шик", "Elegant", "Dark‑academia", "Soft‑girl"])
    vibe     = st.selectbox("Визуальный вайб", ["Солнечный", "Таинственный", "Гик", "Арт‑бохо"])
    
    st.markdown("### Хобби & интересы")
    hobbies  = st.text_input("Хобби (через запятую)", "кино, бег, комиксы")
    music    = st.text_input("Любимая музыка/группы", "The 1975, Arctic Monkeys")
    
    st.markdown("### Характер")
    traits   = st.multiselect("Черты", ["Юмористичный", "Романтичный", "Sassy", "Интроверт", "Экстраверт"])
    temper   = st.selectbox("Темперамент", ["Спокойный", "Энергичный", "Сбалансированный"])
    
    st.markdown("### Красные флаги")
    dislikes = st.text_input("Что бот не любит", "опоздания, грубость")

# --- 2.5. Стильная визуальная анкета в центре страницы ---
st.markdown("""
    <style>
        .form-container {
            background-color: #c8c8cc;
            padding: 40px 30px;
            border-radius: 35px;
            width: 400px;
            margin: 30px auto;
        }
        .form-input > div > input,
        .form-input > div > div {
            background-color: #fcd966 !important;
            color: black !important;
            border-radius: 6px;
        }
    </style>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    name = st.text_input("Имя", key="name", label_visibility="visible")
    sex = st.selectbox("Пол", options=["Мужской", "Женский"], key="sex")
    max_birthdate = datetime.date(2007, 12, 31)  # лимит — 2007 год
    birthdate = st.date_input("Дата рождения", max_value=max_birthdate, key="birthdate")

    st.markdown('</div>', unsafe_allow_html=True)

# --- 3. System‑prompt на основе анкеты ---
SYSTEM_PROMPT = f"""
Ты — {gender.lower()} {age} лет из {city}. Внешний стиль: {fashion}, вайб: {vibe}.
Увлечения: {hobbies}. Любимая музыка: {music}.
Характер: {', '.join(traits) or 'нейтральный'}, темперамент {temper.lower()}.
Тебе не нравятся: {dislikes}.
Общайся в чате, как на первом свидании в Тиндере: флиртуй, задавай вопросы, поддерживай тему.
"""

# --- 4. История диалога ---
if "msgs" not in st.session_state:
    st.session_state.msgs = []

# --- 5. Чат ---
user_input = st.chat_input("Напиши сообщение идеальному партнёру…")
if user_input:
    st.session_state.msgs.append({"role": "user", "content": user_input})
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.msgs
    
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.85,
            max_tokens=256
        )
        bot = resp.choices[0].message.content.strip()
        st.session_state.msgs.append({"role": "assistant", "content": bot})
    except Exception as e:
        st.error(f"Groq error: {e}")

# вывод чата
for m in st.session_state.msgs:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 6. Feedback ---
st.divider()
if st.button("Получить фидбек о моём стиле общения"):
    user_dialog = "\n".join(
        [m["content"] for m in st.session_state.msgs if m["role"] == "user"]
    )[:4000]  # safety slice
    
    fb_prompt = f"""
    Ты — эксперт по коммуникациям и дейтингу. Проанализируй сообщения пользователя
    ниже и дай три пункта: 1) что привлекательно, 2) что может оттолкнуть, 3) совет
    по следующему шагу. Сообщения:\n{user_dialog}
    """
    try:
        fb = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": fb_prompt}],
            temperature=0.5,
            max_tokens=300
        )
        with st.chat_message("assistant"):
            st.subheader("📝 Фидбек от эксперта:")
            st.markdown(fb.choices[0].message.content)
    except Exception as e:
        st.error(f"Groq feedback error: {e}")

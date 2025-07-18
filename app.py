# app.py — DreamDate AI (Streamlit + Groq)

import datetime
import random
import streamlit as st
from openai import OpenAI  # openai>=1.1.0

# --- 1. Groq client ---
client = OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)
MODEL = "llama3-70b-8192"

# --- Состояние ---
if "form_saved" not in st.session_state:
    st.session_state.form_saved = False
if "msgs" not in st.session_state:
    st.session_state.msgs = []

# --- 2. Анкета (sidebar) ---
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

# --- 2.5. Центральная анкета ---
if not st.session_state.form_saved:
    st.title("DreamDate AI — тренируйся в дейтинге")
    st.markdown("""
        <style>
            .form-container {
                background-color: #00dc00;
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
        default_birthdate = datetime.date(2000, 1, 1)
        max_birthdate = datetime.date(2007, 12, 31)
        birthdate = st.date_input("Дата рождения", value=default_birthdate, max_value=max_birthdate, key="birthdate")

        if st.button("Сохранить анкету"):
            st.session_state.form_saved = True
            st.session_state.user_name = name

        st.markdown('</div>', unsafe_allow_html=True)

# --- 3. Этап: выбор характера ---
if st.session_state.form_saved and "personality_saved" not in st.session_state:
    st.title("Выберите характер персонажа")

    st.markdown("""
        <style>
            .slider-labels {
                display: flex;
                justify-content: space-between;
                margin-bottom: -12px;
                font-weight: 500;
            }
            .slider-block {
                margin: 35px 0;
            }
        </style>
    """, unsafe_allow_html=True)

    def labeled_slider(label_left, label_right, key):
        st.markdown(f"""
        <div class="slider-block">
            <div class="slider-labels">
                <span>{label_left}</span>
                <span>{label_right}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.slider(
            label=" ", min_value=0, max_value=100, step=25, value=50, key=key, label_visibility="collapsed"
        )

    labeled_slider("Экстраверт", "Интроверт", "mbti_ei")
    labeled_slider("Реалист", "Мечтатель", "mbti_ns")
    labeled_slider("Рациональный", "Эмоциональный", "mbti_tf")
    labeled_slider("Структурный", "Спонтанный", "mbti_jp")

    selected_gender = st.radio("Выберите пол персонажа", ["Мужской", "Женский"], horizontal=True)

    male_names = ["Илья", "Максим", "Артём", "Лев", "Кирилл", "Миша", "Саша", "Егор", "Никита", "Тимур"]
    female_names = ["Аня", "Лера", "Катя", "Софа", "Маша", "Даша", "Оля", "Ксюша", "Ира", "Лиза"]

    if st.button("Сохранить характер"):
        st.session_state.personality_saved = True
        st.session_state.mbti_ei = st.session_state["mbti_ei"]
        st.session_state.mbti_ns = st.session_state["mbti_ns"]
        st.session_state.mbti_tf = st.session_state["mbti_tf"]
        st.session_state.mbti_jp = st.session_state["mbti_jp"]
        st.session_state.selected_gender = selected_gender

        if selected_gender == "Мужской":
            st.session_state.bot_name = random.choice(male_names)
        else:
            st.session_state.bot_name = random.choice(female_names)


# --- 4. Чат ---
if st.session_state.get("personality_saved", False):
    mbti_text = f"""
    MBTI черты: {'Экстраверт' if st.session_state.mbti_ei > 50 else 'Интроверт'}, 
    {'Мечтатель' if st.session_state.mbti_ns > 50 else 'Реалист'}, 
    {'Эмоциональный' if st.session_state.mbti_tf > 50 else 'Рациональный'}, 
    {'Спонтанный' if st.session_state.mbti_jp > 50 else 'Структурный'}.
    Стиль общения: {st.session_state.selected_gender.lower()}.
    """

    bot_name = st.session_state.get("bot_name", "Партнёр")

    SYSTEM_PROMPT = f"""
    Ты — {gender.lower()} по имени {bot_name}, тебе {age} лет, ты из {city}.
    Внешний стиль: {fashion}, вайб: {vibe}.
    Увлечения: {hobbies}. Любимая музыка: {music}.
    Характер: {', '.join(traits) or 'нейтральный'}, темперамент {temper.lower()}.
    Тебе не нравятся: {dislikes}.
    {mbti_text}
    Общайся в чате, как на первом свидании в Тиндере: флиртуй, задавай вопросы, поддерживай тему.
    """

    user_input = st.chat_input("Напиши сообщение идеальному партнёру…")
    if user_input:
        username = st.session_state.user_name
        user_message = f"**{username}:** {user_input}"
        st.session_state.msgs.append({"role": "user", "content": user_message})

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.msgs
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.85,
                max_tokens=256
            )
            bot = resp.choices[0].message.content.strip()
            bot_message = f"**{bot_name}:** {bot}"
            st.session_state.msgs.append({"role": "assistant", "content": bot_message})
        except Exception as e:
            st.error(f"Groq error: {e}")

    for m in st.session_state.msgs:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    st.divider()
    if st.button("Получить фидбек о моём стиле общения"):
        user_dialog = "\n".join(
            [m["content"] for m in st.session_state.msgs if "user_name" in st.session_state and m["role"] == "user"]
        )[:4000]

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

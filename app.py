# app.py — DreamDate AI (Streamlit + Groq)
import datetime
import streamlit as st
from openai import OpenAI  # openai>=1.1.0

# --- 1. Groq client ---
client = OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)
MODEL = "llama3-70b-8192"

# --- 1.5. Функция генерации изображения персонажа ---
def generate_character_image(prompt: str):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="hd",
            response_format="url"
        )
        return response.data[0].url
    except Exception as e:
        st.error(f"Ошибка генерации изображения: {e}")
        return None

# --- Состояние анкеты ---
if "form_saved" not in st.session_state:
    st.session_state.form_saved = False
if "next_step" not in st.session_state:
    st.session_state.next_step = None
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
    music    = st.text_input("Любимая музыка/группы", "The 1975, Arctic Monkeys")

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

# --- 3. Промежуточный экран ---
if st.session_state.form_saved and st.session_state.next_step is None:
    st.success("💚 Пройдите небольшой тест, и мы подберем вам идеального партнера")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Вперёд!"):
            st.session_state.next_step = "test"
    with col2:
        if st.button("🛠️ Я создам персонажа самостоятельно"):
            st.session_state.next_step = "custom"

# --- 4. Генерация фона персонажа ---
if st.session_state.next_step in ["test", "custom"] and "bg_url" not in st.session_state:
    character_prompt = f"anime girl, {fashion} clothes, {vibe.lower()} vibe, "
    character_prompt += f"{', '.join(traits or ['neutral'])}, full color, fantasy background, digital art"
    img_url = generate_character_image(character_prompt)
    if img_url:
        st.session_state.bg_url = img_url

# --- 5. System prompt и чат ---
if st.session_state.next_step in ["test", "custom"]:
    SYSTEM_PROMPT = f"""
    Ты — {gender.lower()} {age} лет из {city}. Внешний стиль: {fashion}, вайб: {vibe}.
    Увлечения: {hobbies}. Любимая музыка: {music}.
    Характер: {', '.join(traits) or 'нейтральный'}, темперамент {temper.lower()}.
    Тебе не нравятся: {dislikes}.
    Общайся в чате, как на первом свидании в Тиндере: флиртуй, задавай вопросы, поддерживай тему.
    """

    # --- Фон страницы ---
    if "bg_url" in st.session_state:
        st.markdown(f"""
            <style>
                .stApp {{
                    background-image: url({st.session_state.bg_url});
                    background-size: cover;
                    background-position: center;
                    background-attachment: fixed;
                }}
                .stChatMessage {{
                    background-color: rgba(255, 255, 255, 0.85) !important;
                    border-radius: 10px;
                    padding: 8px;
                }}
            </style>
        """, unsafe_allow_html=True)

    # --- Чат: Ввод пользователя ---
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
            st.session_state.msgs.append({"role": "assistant", "content": bot})
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

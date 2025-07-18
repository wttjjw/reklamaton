# app.py — DreamDate AI (Streamlit + Groq)
import datetime
import streamlit as st
from openai import OpenAI  # openai>=1.1.0

# --- 1. Groq client ---
client = OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)
MODEL = "llama3-70b-8192"

# --- Состояния анкеты ---
if "form_saved" not in st.session_state:
    st.session_state.form_saved = False
if "character_created" not in st.session_state:
    st.session_state.character_created = False
if "msgs" not in st.session_state:
    st.session_state.msgs = []

# --- 2. Анкета пользователя (sidebar) ---
with st.sidebar:
    st.header("Параметры анкеты")
    gender = st.selectbox("Пол персонажа", ["Девушка", "Парень", "Небинарный"])
    age = st.slider("Возраст", 18, 60, 25)
    city = st.text_input("Город/часовой пояс", "Москва")
    
    st.markdown("### Внешний вайб")
    fashion = st.selectbox("Стиль одежды", ["Casual", "Спорт‑шик", "Elegant", "Dark‑academia", "Soft‑girl"])
    vibe = st.selectbox("Визуальный вайб", ["Солнечный", "Таинственный", "Гик", "Арт‑бохо"])
    
    st.markdown("### Хобби & интересы")
    hobbies = st.text_input("Хобби (через запятую)", "кино, бег, комиксы")
    music = st.text_input("Любимая музыка/группы", "The 1975, Arctic Monkeys")
    
    st.markdown("### Характер")
    traits = st.multiselect("Черты", ["Юмористичный", "Романтичный", "Sassy", "Интроверт", "Экстраверт"])
    temper = st.selectbox("Темперамент", ["Спокойный", "Энергичный", "Сбалансированный"])
    
    st.markdown("### Красные флаги")
    dislikes = st.text_input("Что бот не любит", "опоздания, грубость")

# --- 3. Центральная анкета пользователя (без зеленой шапки) ---
if not st.session_state.form_saved:
    st.title("DreamDate AI — тренируйся в дейтинге")
    
    name = st.text_input("Имя", key="name", label_visibility="visible")
    sex = st.selectbox("Пол", options=["Мужской", "Женский"], key="sex")
    default_birthdate = datetime.date(2000, 1, 1)
    max_birthdate = datetime.date(2007, 12, 31)
    birthdate = st.date_input("Дата рождения", value=default_birthdate, 
                            max_value=max_birthdate, key="birthdate")

    if st.button("Сохранить анкету", type="primary"):
        st.session_state.form_saved = True
        st.session_state.user_name = name
        # Сбрасываем предыдущие состояния
        st.session_state.character_created = False
        st.session_state.personality_saved = False
        st.rerun()

# --- 4. Выбор типа персонажа (стильные кликабельные кнопки) ---
if st.session_state.form_saved and not st.session_state.character_created:
    st.title("Выберите тип персонажа")
    
    st.markdown("""
        <style>
            .char-btn {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 25px;
                border-radius: 16px;
                background: linear-gradient(145deg, #ffffff, #f0f0f0);
                box-shadow: 5px 5px 15px #d9d9d9, 
                            -5px -5px 15px #ffffff;
                transition: all 0.3s ease;
                text-align: center;
                height: 100%;
                cursor: pointer;
                border: none;
            }
            .char-btn:hover {
                transform: translateY(-5px);
                box-shadow: 8px 8px 20px #d0d0d0, 
                            -8px -8px 20px #ffffff;
            }
            .char-btn:active {
                transform: translateY(0);
                box-shadow: 3px 3px 10px #d9d9d9, 
                            -3px -3px 10px #ffffff;
            }
            .char-btn h3 {
                margin: 0 0 10px 0;
                color: #333;
            }
            .char-btn p {
                margin: 0;
                color: #666;
                font-size: 0.9em;
            }
            .btn-icon {
                font-size: 36px;
                margin-bottom: 15px;
            }
            .create-btn {
                background: linear-gradient(145deg, #4CAF50, #43A047);
                color: white !important;
            }
            .create-btn h3, .create-btn p {
                color: white !important;
            }
            .premade-btn-1 { background: linear-gradient(145deg, #2196F3, #1E88E5); }
            .premade-btn-2 { background: linear-gradient(145deg, #9C27B0, #8E24AA); }
            .premade-btn-3 { background: linear-gradient(145deg, #FF9800, #FB8C00); }
            .premade-btn-1 h3, .premade-btn-1 p,
            .premade-btn-2 h3, .premade-btn-2 p,
            .premade-btn-3 h3, .premade-btn-3 p {
                color: white !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Основные кнопки в 2 колонки
    col_main1, col_main2 = st.columns([1, 1], gap="large")
    
    with col_main1:
        # Создание своего персонажа
        if st.button("", key="create_custom_main"):
            st.session_state.character_type = "custom"
            st.session_state.character_created = True
            st.rerun()
        st.markdown("""
            <button class="char-btn create-btn">
                <div class="btn-icon">✨</div>
                <h3>Создать своего персонажа</h3>
                <p>Полная кастомизация характера и стиля</p>
            </button>
        """, unsafe_allow_html=True)
    
    with col_main2:
        # Готовые персонажи заголовок
        st.subheader("Или выберите готового:")
        
        # Три персонажа в ряд
        col1, col2, col3 = st.columns(3, gap="medium")
        
        with col1:
            if st.button("", key="premade_1_main"):
                st.session_state.character_type = "premade_1"
                st.session_state.character_created = True
                st.rerun()
            st.markdown("""
                <button class="char-btn premade-btn-1">
                    <div class="btn-icon">⚡</div>
                    <h3>Энергичный экстраверт</h3>
                    <p>Любит активный отдых</p>
                </button>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("", key="premade_2_main"):
                st.session_state.character_type = "premade_2"
                st.session_state.character_created = True
                st.rerun()
            st.markdown("""
                <button class="char-btn premade-btn-2">
                    <div class="btn-icon">🌹</div>
                    <h3>Романтичный интроверт</h3>
                    <p>Ценит глубокие разговоры</p>
                </button>
            """, unsafe_allow_html=True)
        
        with col3:
            if st.button("", key="premade_3_main"):
                st.session_state.character_type = "premade_3"
                st.session_state.character_created = True
                st.rerun()
            st.markdown("""
                <button class="char-btn premade-btn-3">
                    <div class="btn-icon">🎨</div>
                    <h3>Загадочный артистичный</h3>
                    <p>Творческий взгляд на мир</p>
                </button>
            """, unsafe_allow_html=True)

# --- 5. Создание кастомного персонажа ---
if st.session_state.get("character_created", False) and st.session_state.character_type == "custom":
    if "personality_saved" not in st.session_state:
        st.session_state.personality_saved = False
    
    if not st.session_state.personality_saved:
        st.title("Настройте характер персонажа")
        
        st.markdown("""
            <style>
                .slider-container {
                    background: #f0f2f6;
                    border-radius: 12px;
                    padding: 20px;
                    margin-bottom: 25px;
                    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
                }
                .slider-header {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 10px;
                    font-weight: bold;
                    color: #444;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Инициализация значений
        if "mbti_ei" not in st.session_state:
            st.session_state.mbti_ei = 50
        if "mbti_ns" not in st.session_state:
            st.session_state.mbti_ns = 50
        if "mbti_tf" not in st.session_state:
            st.session_state.mbti_tf = 50
        if "mbti_jp" not in st.session_state:
            st.session_state.mbti_jp = 50
        
        # Первая строка слайдеров
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            with st.container():
                st.markdown('<div class="slider-container">', unsafe_allow_html=True)
                st.markdown('<div class="slider-header"><span>👥 Экстраверт</span><span>🧘 Интроверт</span></div>', unsafe_allow_html=True)
                st.session_state.mbti_ei = st.slider(
                    "Экстраверт/Интроверт", 
                    0, 100, st.session_state.mbti_ei, 
                    key="slider_ei", 
                    label_visibility="collapsed"
                )
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            with st.container():
                st.markdown('<div class="slider-container">', unsafe_allow_html=True)
                st.markdown('<div class="slider-header"><span>📐 Реалист</span><span>🌈 Мечтатель</span></div>', unsafe_allow_html=True)
                st.session_state.mbti_ns = st.slider(
                    "Реалист/Мечтатель", 
                    0, 100, st.session_state.mbti_ns, 
                    key="slider_ns", 
                    label_visibility="collapsed"
                )
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Вторая строка слайдеров
        col3, col4 = st.columns(2, gap="medium")
        with col3:
            with st.container():
                st.markdown('<div class="slider-container">', unsafe_allow_html=True)
                st.markdown('<div class="slider-header"><span>📊 Рациональный</span><span>❤️ Эмоциональный</span></div>', unsafe_allow_html=True)
                st.session_state.mbti_tf = st.slider(
                    "Рациональный/Эмоциональный", 
                    0, 100, st.session_state.mbti_tf, 
                    key="slider_tf", 
                    label_visibility="collapsed"
                )
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            with st.container():
                st.markdown('<div class="slider-container">', unsafe_allow_html=True)
                st.markdown('<div class="slider-header"><span>📅 Структурный</span><span>🎲 Спонтанный</span></div>', unsafe_allow_html=True)
                st.session_state.mbti_jp = st.slider(
                    "Структурный/Спонтанный", 
                    0, 100, st.session_state.mbti_jp, 
                    key="slider_jp", 
                    label_visibility="collapsed"
                )
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Выбор пола
        st.markdown("### Пол персонажа")
        if "selected_gender" not in st.session_state:
            st.session_state.selected_gender = "Мужской"
        st.session_state.selected_gender = st.radio(
            "", 
            ["Мужской", "Женский"], 
            horizontal=True, 
            key="char_gender",
            index=0 if st.session_state.selected_gender == "Мужской" else 1
        )
        
        # Кнопка сохранения
        if st.button("Сохранить характер", type="primary"):
            st.session_state.personality_saved = True
            st.rerun()

# --- 6. Чат и логика взаимодействия ---
if st.session_state.get("personality_saved", False) or (
    st.session_state.get("character_created", False) and st.session_state.character_type != "custom"
):
    # Для готовых персонажей устанавливаем предустановки
    if st.session_state.character_type.startswith("premade"):
        if st.session_state.character_type == "premade_1":
            st.session_state.mbti_ei = 80  # Экстраверт
            st.session_state.mbti_ns = 30  # Реалист
            st.session_state.mbti_tf = 60  # Эмоциональный
            st.session_state.mbti_jp = 70  # Спонтанный
            st.session_state.selected_gender = "Мужской"
        elif st.session_state.character_type == "premade_2":
            st.session_state.mbti_ei = 20  # Интроверт
            st.session_state.mbti_ns = 80  # Мечтатель
            st.session_state.mbti_tf = 70  # Эмоциональный
            st.session_state.mbti_jp = 40  # Структурный
            st.session_state.selected_gender = "Женский"
        elif st.session_state.character_type == "premade_3":
            st.session_state.mbti_ei = 50  # Нейтральный
            st.session_state.mbti_ns = 65  # Склонен к мечтательности
            st.session_state.mbti_tf = 75  # Эмоциональный
            st.session_state.mbti_jp = 60  # Спонтанный
            st.session_state.selected_gender = "Небинарный"

    # Текстовое описание характеристик
    mbti_text = f"""
    MBTI черты: {'Экстраверт' if st.session_state.get('mbti_ei', 50) > 50 else 'Интроверт'}, 
    {'Мечтатель' if st.session_state.get('mbti_ns', 50) > 50 else 'Реалист'}, 
    {'Эмоциональный' if st.session_state.get('mbti_tf', 50) > 50 else 'Рациональный'}, 
    {'Спонтанный' if st.session_state.get('mbti_jp', 50) > 50 else 'Структурный'}.
    Стиль общения: {st.session_state.get('selected_gender', 'Нейтральный').lower()}.
    """

    SYSTEM_PROMPT = f"""
    Ты — {gender.lower()} {age} лет из {city}. Внешний стиль: {fashion}, вайб: {vibe}.
    Увлечения: {hobbies}. Любимая музыка: {music}.
    Характер: {', '.join(traits) or 'нейтральный'}, темперамент {temper.lower()}.
    Тебе не нравятся: {dislikes}.
    {mbti_text}
    Общайся в чате, как на первом свидании в Тиндере: флиртуй, задавай вопросы, поддерживай тему.
    """

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

    # --- Вывод чата ---
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # --- Feedback ---
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

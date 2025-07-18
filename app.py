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
if "char_settings" not in st.session_state:
    st.session_state.char_settings = {
        "gender": "Девушка",
        "age": 25,
        "city": "Москва",
        "fashion": "Casual",
        "vibe": "Солнечный",
        "hobbies": [],
        "music": [],
        "traits": [],
        "temper": "Сбалансированный",
        "dislikes": []
    }

# --- 3. Центральная анкета пользователя ---
if not st.session_state.form_saved:
    st.title("DreamDate AI — тренируйся в дейтинге")
    
    with st.form("user_form"):
        name = st.text_input("Имя", key="name", label_visibility="visible")
        sex = st.selectbox("Пол", options=["Мужской", "Женский"], key="sex")
        default_birthdate = datetime.date(2000, 1, 1)
        max_birthdate = datetime.date(2007, 12, 31)
        birthdate = st.date_input("Дата рождения", value=default_birthdate, 
                                max_value=max_birthdate, key="birthdate")
        
        if st.form_submit_button("Сохранить анкету", type="primary"):
            st.session_state.form_saved = True
            st.session_state.user_name = name
            # Сбрасываем предыдущие состояния
            st.session_state.character_created = False
            st.session_state.personality_saved = False
            st.rerun()

# --- 4. Выбор типа персонажа (обновлённые кнопки) ---
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
                margin-bottom: 20px;
                width: 100%;
            }
            .char-btn:hover {
                transform: translateY(-5px);
                box-shadow: 8px 8px 20px #d0d0d0, 
                            -8px -8px 20px #ffffff;
            }
            .char-btn h3 {
                margin: 0 0 10px 0;
                color: #333;
                font-size: 1.4rem;
            }
            .char-btn p {
                margin: 0;
                color: #666;
                font-size: 1rem;
            }
            .btn-icon {
                font-size: 42px;
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
            .btn-container {
                margin: 0 auto;
                max-width: 800px;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Контейнер для всех кнопок
    with st.container():
        st.markdown('<div class="btn-container">', unsafe_allow_html=True)
        
        # Кнопка создания персонажа
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
        
        # Готовые персонажи заголовок
        st.markdown('<h2 style="text-align: center; margin: 30px 0 20px 0;">Или выберите готового персонажа:</h2>', unsafe_allow_html=True)
        
        # Три персонажа вертикально
        # Персонаж 1
        if st.button("", key="premade_1_main"):
            st.session_state.character_type = "premade_1"
            st.session_state.character_created = True
            st.rerun()
        st.markdown("""
            <button class="char-btn premade-btn-1">
                <div class="btn-icon">⚡</div>
                <h3>Энергичный экстраверт</h3>
                <p>Любит активный отдых, легко заводит знакомства, всегда в движении</p>
            </button>
        """, unsafe_allow_html=True)
        
        # Персонаж 2
        if st.button("", key="premade_2_main"):
            st.session_state.character_type = "premade_2"
            st.session_state.character_created = True
            st.rerun()
        st.markdown("""
            <button class="char-btn premade-btn-2">
                <div class="btn-icon">🌹</div>
                <h3>Романтичный интроверт</h3>
                <p>Ценит глубокие разговоры, любит искусство, ищет настоящую связь</p>
            </button>
        """, unsafe_allow_html=True)
        
        # Персонаж 3
        if st.button("", key="premade_3_main"):
            st.session_state.character_type = "premade_3"
            st.session_state.character_created = True
            st.rerun()
        st.markdown("""
            <button class="char-btn premade-btn-3">
                <div class="btn-icon">🎨</div>
                <h3>Загадочный артистичный</h3>
                <p>Творческая личность с необычным взглядом на мир, полна сюрпризов</p>
            </button>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. Создание кастомного персонажа (исправленная версия) ---
if st.session_state.get("character_created", False) and st.session_state.character_type == "custom":
    if "personality_saved" not in st.session_state:
        st.session_state.personality_saved = False
    
    if not st.session_state.personality_saved:
        st.title("Настройте персонажа")
        
        # Инициализация значений
        if "mbti_ei" not in st.session_state:
            st.session_state.mbti_ei = 50
        if "mbti_ns" not in st.session_state:
            st.session_state.mbti_ns = 50
        if "mbti_tf" not in st.session_state:
            st.session_state.mbti_tf = 50
        if "mbti_jp" not in st.session_state:
            st.session_state.mbti_jp = 50
        if "selected_gender" not in st.session_state:
            st.session_state.selected_gender = "Мужской"
        
        # Проверка и инициализация char_settings
        if not st.session_state.char_settings:
            st.session_state.char_settings = {
                "gender": "Девушка",
                "age": 25,
                "city": "Москва",
                "fashion": "Casual",
                "vibe": "Солнечный",
                "hobbies": [],
                "music": [],
                "traits": [],
                "temper": "Сбалансированный",
                "dislikes": []
            }
        
        # --- Основные настройки ---
        with st.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.session_state.char_settings["gender"] = st.selectbox(
                    "Пол персонажа", 
                    ["Девушка", "Парень", "Небинарный"],
                    index=["Девушка", "Парень", "Небинарный"].index(st.session_state.char_settings["gender"])
                )
            with col2:
                st.session_state.char_settings["age"] = st.slider(
                    "Возраст", 18, 60, st.session_state.char_settings["age"]
                )
            with col3:
                st.session_state.char_settings["city"] = st.text_input(
                    "Город/часовой пояс", 
                    st.session_state.char_settings["city"]
                )
        
        # --- Слайдеры характера ---
        st.markdown("### Характер персонажа")
        col1, col2 = st.columns(2)
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
        
        col3, col4 = st.columns(2)
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
        st.markdown("### Стиль общения")
        st.session_state.selected_gender = st.radio(
            "", 
            ["Мужской", "Женский"], 
            horizontal=True, 
            key="char_gender",
            index=0 if st.session_state.get('selected_gender', 'Мужской') == "Мужской" else 1
        )
        
        # --- Блок "Мне интересно" ---
        st.markdown("### 🎯 Мне интересно")
        
        # Хобби
        st.markdown("**Хобби:**")
        hobbies_options = ["Кино", "Бег", "Комиксы", "Путешествия", "Фотография", "Кулинария", "Игры", "Чтение", "Йога"]
        cols = st.columns(3)
        for i, hobby in enumerate(hobbies_options):
            with cols[i % 3]:
                if st.button(hobby, key=f"hobby_{hobby}"):
                    if hobby in st.session_state.char_settings["hobbies"]:
                        st.session_state.char_settings["hobbies"].remove(hobby)
                    else:
                        st.session_state.char_settings["hobbies"].append(hobby)
                    st.rerun()
                selected = hobby in st.session_state.char_settings["hobbies"]
                color = "#4CAF50" if selected else "#E0E0E0"
                st.markdown(f"""
                    <div style="
                        background-color: {color};
                        border-radius: 16px;
                        padding: 8px 16px;
                        margin: 5px 0;
                        text-align: center;
                        color: {'white' if selected else 'black'};
                        font-weight: {'bold' if selected else 'normal'};
                    ">
                        {hobby}
                    </div>
                """, unsafe_allow_html=True)
        
        # Музыка
        st.markdown("**Музыкальные предпочтения:**")
        music_options = ["Рок", "Поп", "Хип-хоп", "Электроника", "Джаз", "Классика", "Инди", "Метал", "R&B"]
        cols = st.columns(3)
        for i, music in enumerate(music_options):
            with cols[i % 3]:
                if st.button(music, key=f"music_{music}"):
                    if music in st.session_state.char_settings["music"]:
                        st.session_state.char_settings["music"].remove(music)
                    else:
                        st.session_state.char_settings["music"].append(music)
                    st.rerun()
                selected = music in st.session_state.char_settings["music"]
                color = "#4CAF50" if selected else "#E0E0E0"
                st.markdown(f"""
                    <div style="
                        background-color: {color};
                        border-radius: 16px;
                        padding: 8px 16px;
                        margin: 5px 0;
                        text-align: center;
                        color: {'white' if selected else 'black'};
                        font-weight: {'bold' if selected else 'normal'};
                    ">
                        {music}
                    </div>
                """, unsafe_allow_html=True)
        
        # --- Блок "Внешний вайб" ---
        st.markdown("### 👗 Внешний вайб")
        
        # Стиль одежды
        st.markdown("**Стиль одежды:**")
        fashion_options = ["Casual", "Спорт-шик", "Elegant", "Dark-academia", "Soft-girl", "Бохо", "Минимализм"]
        selected_fashion = st.session_state.char_settings["fashion"]
        cols = st.columns(4)
        for i, fashion in enumerate(fashion_options):
            with cols[i % 4]:
                if st.button(fashion, key=f"fashion_{fashion}"):
                    st.session_state.char_settings["fashion"] = fashion
                    st.rerun()
                selected = fashion == selected_fashion
                color = "#2196F3" if selected else "#E0E0E0"
                st.markdown(f"""
                    <div style="
                        background-color: {color};
                        border-radius: 16px;
                        padding: 8px 5px;
                        margin: 5px 0;
                        text-align: center;
                        color: {'white' if selected else 'black'};
                        font-weight: {'bold' if selected else 'normal'};
                    ">
                        {fashion}
                    </div>
                """, unsafe_allow_html=True)
        
        # Визуальный вайб
        st.markdown("**Визуальный вайб:**")
        vibe_options = ["Солнечный", "Таинственный", "Гик", "Арт-бохо", "Романтичный", "Брутальный", "Утонченный"]
        selected_vibe = st.session_state.char_settings["vibe"]
        cols = st.columns(4)
        for i, vibe in enumerate(vibe_options):
            with cols[i % 4]:
                if st.button(vibe, key=f"vibe_{vibe}"):
                    st.session_state.char_settings["vibe"] = vibe
                    st.rerun()
                selected = vibe == selected_vibe
                color = "#2196F3" if selected else "#E0E0E0"
                st.markdown(f"""
                    <div style="
                        background-color: {color};
                        border-radius: 16px;
                        padding: 8px 5px;
                        margin: 5px 0;
                        text-align: center;
                        color: {'white' if selected else 'black'};
                        font-weight: {'bold' if selected else 'normal'};
                    ">
                        {vibe}
                    </div>
                """, unsafe_allow_html=True)
        
        # --- Блок "Характер" ---
        st.markdown("### 😊 Черты характера")
        
        # Черты характера
        st.markdown("**Основные черты:**")
        traits_options = ["Юмористичный", "Романтичный", "Sassy", "Интроверт", "Экстраверт", "Добрый", "Уверенный", "Скромный"]
        cols = st.columns(4)
        for i, trait in enumerate(traits_options):
            with cols[i % 4]:
                if st.button(trait, key=f"trait_{trait}"):
                    if trait in st.session_state.char_settings["traits"]:
                        st.session_state.char_settings["traits"].remove(trait)
                    else:
                        st.session_state.char_settings["traits"].append(trait)
                    st.rerun()
                selected = trait in st.session_state.char_settings["traits"]
                color = "#9C27B0" if selected else "#E0E0E0"
                st.markdown(f"""
                    <div style="
                        background-color: {color};
                        border-radius: 16px;
                        padding: 8px 5px;
                        margin: 5px 0;
                        text-align: center;
                        color: {'white' if selected else 'black'};
                        font-weight: {'bold' if selected else 'normal'};
                    ">
                        {trait}
                    </div>
                """, unsafe_allow_html=True)
        
        # Темперамент
        st.markdown("**Темперамент:**")
        temper_options = ["Спокойный", "Энергичный", "Сбалансированный", "Импульсивный", "Флегматичный"]
        selected_temper = st.session_state.char_settings["temper"]
        cols = st.columns(5)
        for i, temper in enumerate(temper_options):
            with cols[i % 5]:
                if st.button(temper, key=f"temper_{temper}"):
                    st.session_state.char_settings["temper"] = temper
                    st.rerun()
                selected = temper == selected_temper
                color = "#9C27B0" if selected else "#E0E0E0"
                st.markdown(f"""
                    <div style="
                        background-color: {color};
                        border-radius: 16px;
                        padding: 8px 5px;
                        margin: 5px 0;
                        text-align: center;
                        color: {'white' if selected else 'black'};
                        font-weight: {'bold' if selected else 'normal'};
                    ">
                        {temper}
                    </div>
                """, unsafe_allow_html=True)
        
        # --- Блок "Красные флаги" ---
        st.markdown("### 🚩 Красные флаги")
        
        st.markdown("**Что не нравится:**")
        dislikes_options = ["Опоздания", "Грубость", "Ложь", "Нарциссизм", "Эгоизм", "Пассивность", "Агрессия"]
        cols = st.columns(4)
        for i, dislike in enumerate(dislikes_options):
            with cols[i % 4]:
                if st.button(dislike, key=f"dislike_{dislike}"):
                    if dislike in st.session_state.char_settings["dislikes"]:
                        st.session_state.char_settings["dislikes"].remove(dislike)
                    else:
                        st.session_state.char_settings["dislikes"].append(dislike)
                    st.rerun()
                selected = dislike in st.session_state.char_settings["dislikes"]
                color = "#F44336" if selected else "#FFEBEE"
                st.markdown(f"""
                    <div style="
                        background-color: {color};
                        border-radius: 16px;
                        padding: 8px 5px;
                        margin: 5px 0;
                        text-align: center;
                        color: {'white' if selected else '#B71C1C'};
                        font-weight: {'bold' if selected else 'normal'};
                    ">
                        {dislike}
                    </div>
                """, unsafe_allow_html=True)
        
        # Кнопка сохранения
        if st.button("Сохранить персонажа", type="primary", use_container_width=True):
            st.session_state.personality_saved = True
            st.rerun()

# --- 6. Чат и логика взаимодействия ---
if st.session_state.get("personality_saved", False) or (
    st.session_state.get("character_created", False) and st.session_state.character_type != "custom"
):
    # Для готовых персонажей устанавливаем предустановки
    if st.session_state.character_type.startswith("premade"):
        if st.session_state.character_type == "premade_1":
            # Энергичный экстраверт
            st.session_state.mbti_ei = 80
            st.session_state.mbti_ns = 30
            st.session_state.mbti_tf = 60
            st.session_state.mbti_jp = 70
            st.session_state.selected_gender = "Мужской"
            st.session_state.char_settings = {
                "gender": "Парень",
                "age": 28,
                "city": "Москва",
                "fashion": "Спорт-шик",
                "vibe": "Энергичный",
                "hobbies": ["Спорт", "Путешествия", "Кино"],
                "music": ["Рок", "Электроника"],
                "traits": ["Экстраверт", "Уверенный"],
                "temper": "Энергичный",
                "dislikes": ["Лень", "Пассивность"]
            }
        elif st.session_state.character_type == "premade_2":
            # Романтичный интроверт
            st.session_state.mbti_ei = 20
            st.session_state.mbti_ns = 80
            st.session_state.mbti_tf = 70
            st.session_state.mbti_jp = 40
            st.session_state.selected_gender = "Женский"
            st.session_state.char_settings = {
                "gender": "Девушка",
                "age": 24,
                "city": "Санкт-Петербург",
                "fashion": "Романтичный",
                "vibe": "Нежный",
                "hobbies": ["Чтение", "Искусство", "Музыка"],
                "music": ["Инди", "Классика"],
                "traits": ["Романтичный", "Интроверт"],
                "temper": "Спокойный",
                "dislikes": ["Грубость", "Нарциссизм"]
            }
        elif st.session_state.character_type == "premade_3":
            # Загадочный артистичный
            st.session_state.mbti_ei = 50
            st.session_state.mbti_ns = 65
            st.session_state.mbti_tf = 75
            st.session_state.mbti_jp = 60
            st.session_state.selected_gender = "Небинарный"
            st.session_state.char_settings = {
                "gender": "Небинарный",
                "age": 26,
                "city": "Калининград",
                "fashion": "Бохо",
                "vibe": "Загадочный",
                "hobbies": ["Искусство", "Фотография", "Путешествия"],
                "music": ["Инди", "Джаз", "Экспериментальная"],
                "traits": ["Творческий", "Мечтатель"],
                "temper": "Сбалансированный",
                "dislikes": ["Ограничения", "Консерватизм"]
            }

    # Текстовое описание характеристик
    mbti_text = f"""
    MBTI черты: {'Экстраверт' if st.session_state.get('mbti_ei', 50) > 50 else 'Интроверт'}, 
    {'Мечтатель' if st.session_state.get('mbti_ns', 50) > 50 else 'Реалист'}, 
    {'Эмоциональный' if st.session_state.get('mbti_tf', 50) > 50 else 'Рациональный'}, 
    {'Спонтанный' if st.session_state.get('mbti_jp', 50) > 50 else 'Структурный'}.
    Стиль общения: {st.session_state.get('selected_gender', 'Нейтральный').lower()}.
    """
    
    # Форматирование настроек персонажа
    settings = st.session_state.char_settings
    hobbies_str = ", ".join(settings["hobbies"]) if settings["hobbies"] else "нет"
    music_str = ", ".join(settings["music"]) if settings["music"] else "нет"
    traits_str = ", ".join(settings["traits"]) if settings["traits"] else "нейтральный"
    dislikes_str = ", ".join(settings["dislikes"]) if settings["dislikes"] else "нет"

    SYSTEM_PROMPT = f"""
    Ты — {settings['gender'].lower()} {settings['age']} лет из {settings['city']}. 
    Внешний стиль: {settings['fashion']}, вайб: {settings['vibe']}.
    Увлечения: {hobbies_str}. Любимая музыка: {music_str}.
    Характер: {traits_str}, темперамент {settings['temper'].lower()}.
    Тебе не нравятся: {dislikes_str}.
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

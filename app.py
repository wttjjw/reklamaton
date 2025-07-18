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
        "dislikes": [],
        "style": "Дружелюбный"
    }

# --- Глобальный стиль с градиентным фоном ---
st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            background-attachment: fixed;
            background-size: cover;
            color: #333;
        }
        .stApp {
            background: rgba(255, 255, 255, 0.85);
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            backdrop-filter: blur(4px);
            margin: 2rem auto;
            padding: 2rem;
            max-width: 1200px;
        }
        .stButton>button {
            border-radius: 12px !important;
            padding: 10px 20px !important;
            transition: all 0.3s !important;
        }
        .stButton>button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1) !important;
        }
        .section {
            background: rgba(255, 255, 255, 0.7);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        }
        .tag {
            display: inline-block;
            border-radius: 16px;
            padding: 8px 16px;
            margin: 5px;
            cursor: pointer;
            transition: all 0.2s;
            text-align: center;
            width: 100%;
            font-weight: 500;
        }
        .tag:hover {
            transform: scale(1.05);
        }
        .tag.selected {
            color: white !important;
            font-weight: 600;
        }
        .char-btn {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 30px;
            border-radius: 20px;
            background: linear-gradient(145deg, #ffffff, #f0f0f0);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            text-align: center;
            height: 100%;
            cursor: pointer;
            border: none;
            margin-bottom: 25px;
            width: 100%;
        }
        .char-btn:hover {
            transform: translateY(-8px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        }
        .char-btn h3 {
            margin: 15px 0 10px 0;
            color: #333;
            font-size: 1.5rem;
        }
        .char-btn p {
            margin: 0;
            color: #666;
            font-size: 1.1rem;
            line-height: 1.4;
        }
        .btn-icon {
            font-size: 48px;
            margin-bottom: 15px;
        }
        .create-btn {
            background: linear-gradient(145deg, #4CAF50, #2E7D32);
            color: white !important;
        }
        .create-btn h3, .create-btn p {
            color: white !important;
        }
        .premade-btn-1 { background: linear-gradient(145deg, #2196F3, #0D47A1); }
        .premade-btn-2 { background: linear-gradient(145deg, #9C27B0, #6A1B9A); }
        .premade-btn-3 { background: linear-gradient(145deg, #FF9800, #EF6C00); }
        .premade-btn-1 h3, .premade-btn-1 p,
        .premade-btn-2 h3, .premade-btn-2 p,
        .premade-btn-3 h3, .premade-btn-3 p {
            color: white !important;
        }
        .btn-container {
            margin: 0 auto;
            max-width: 800px;
        }
        .trait-btn {
            background: rgba(156, 39, 176, 0.15);
            color: #6A1B9A;
        }
        .trait-btn.selected {
            background: linear-gradient(145deg, #9C27B0, #6A1B9A);
        }
        .dislike-btn {
            background: rgba(244, 67, 54, 0.15);
            color: #B71C1C;
        }
        .dislike-btn.selected {
            background: linear-gradient(145deg, #F44336, #C62828);
        }
        .hobby-btn {
            background: rgba(33, 150, 243, 0.15);
            color: #0D47A1;
        }
        .hobby-btn.selected {
            background: linear-gradient(145deg, #2196F3, #0D47A1);
        }
        .music-btn {
            background: rgba(255, 152, 0, 0.15);
            color: #E65100;
        }
        .music-btn.selected {
            background: linear-gradient(145deg, #FF9800, #EF6C00);
        }
        .fashion-btn {
            background: rgba(76, 175, 80, 0.15);
            color: #1B5E20;
        }
        .fashion-btn.selected {
            background: linear-gradient(145deg, #4CAF50, #2E7D32);
        }
        .vibe-btn {
            background: rgba(156, 39, 176, 0.15);
            color: #6A1B9A;
        }
        .vibe-btn.selected {
            background: linear-gradient(145deg, #9C27B0, #6A1B9A);
        }
        .temper-btn {
            background: rgba(33, 150, 243, 0.15);
            color: #0D47A1;
        }
        .temper-btn.selected {
            background: linear-gradient(145deg, #2196F3, #0D47A1);
        }
        .mbti-option {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 15px;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.7);
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
            height: 100%;
        }
        .mbti-option:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        }
        .mbti-option.selected {
            background: linear-gradient(145deg, #6a11cb, #2575fc);
            color: white;
        }
        .mbti-icon {
            font-size: 36px;
            margin-bottom: 10px;
        }
        .mbti-title {
            font-weight: bold;
            margin-bottom: 5px;
            font-size: 1.1rem;
        }
        .chat-container {
            max-height: 500px;
            overflow-y: auto;
            padding: 10px;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.7);
            margin-bottom: 20px;
        }
        .user-message {
            background: linear-gradient(135deg, #6a11cb, #2575fc);
            color: white;
            border-radius: 18px 18px 4px 18px;
            padding: 12px 18px;
            margin: 10px 0;
            max-width: 80%;
            align-self: flex-end;
        }
        .bot-message {
            background: rgba(255, 255, 255, 0.9);
            color: #333;
            border-radius: 18px 18px 18px 4px;
            padding: 12px 18px;
            margin: 10px 0;
            max-width: 80%;
            align-self: flex-start;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .message-container {
            display: flex;
            flex-direction: column;
            margin-bottom: 15px;
        }
        .user-container {
            align-items: flex-end;
        }
        .bot-container {
            align-items: flex-start;
        }
        .message-name {
            font-weight: bold;
            margin-bottom: 4px;
            font-size: 0.9rem;
        }
        .character-card {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            display: flex;
            align-items: center;
        }
        .avatar {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            margin-right: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 40px;
        }
        .character-info {
            flex-grow: 1;
        }
        .character-name {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .character-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }
        .character-tag {
            background: rgba(156, 39, 176, 0.15);
            color: #6A1B9A;
            border-radius: 16px;
            padding: 6px 12px;
            font-size: 0.9rem;
        }
    </style>
""", unsafe_allow_html=True)

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
            st.session_state.character_created = False
            st.session_state.personality_saved = False
            st.rerun()

# --- 4. Выбор типа персонажа ---
if st.session_state.form_saved and not st.session_state.character_created:
    st.title("Выберите тип персонажа")
    
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

# --- 5. Создание кастомного персонажа (только кнопки) ---
if st.session_state.get("character_created", False) and st.session_state.character_type == "custom":
    if "personality_saved" not in st.session_state:
        st.session_state.personality_saved = False
    
    if not st.session_state.personality_saved:
        st.title("🎭 Создайте своего персонажа")
        
        # --- Основные настройки ---
        with st.container():
            st.markdown("### Основная информация")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**Пол персонажа**")
                options = ["Девушка", "Парень", "Небинарный"]
                for gender in options:
                    if st.button(gender, key=f"gender_{gender}"):
                        st.session_state.char_settings["gender"] = gender
                        st.rerun()
                    selected = st.session_state.char_settings["gender"] == gender
                    st.markdown(f"""
                        <div class="tag {'selected' if selected else ''} 
                                   {'temper-btn' if selected else 'temper-btn'}" 
                             style="{'background: linear-gradient(145deg, #9C27B0, #6A1B9A); color: white;' if selected else ''}">
                            {gender}
                        </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("**Возраст**")
                ages = ["18-22", "23-27", "28-32", "33+"]
                for age in ages:
                    if st.button(age, key=f"age_{age}"):
                        st.session_state.char_settings["age"] = age
                        st.rerun()
                    selected = st.session_state.char_settings["age"] == age
                    st.markdown(f"""
                        <div class="tag {'selected' if selected else ''} 
                                   {'temper-btn' if selected else 'temper-btn'}" 
                             style="{'background: linear-gradient(145deg, #2196F3, #0D47A1); color: white;' if selected else ''}">
                            {age}
                        </div>
                    """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("**Город**")
                cities = ["Москва", "Санкт-Петербург", "Другой"]
                for city in cities:
                    if st.button(city, key=f"city_{city}"):
                        st.session_state.char_settings["city"] = city
                        st.rerun()
                    selected = st.session_state.char_settings["city"] == city
                    st.markdown(f"""
                        <div class="tag {'selected' if selected else ''} 
                                   {'temper-btn' if selected else 'temper-btn'}" 
                             style="{'background: linear-gradient(145deg, #4CAF50, #2E7D32); color: white;' if selected else ''}">
                            {city}
                        </div>
                    """, unsafe_allow_html=True)
        
        # --- Характер ---
        st.markdown("### 🧠 Характер персонажа")
        
        # Слайдеры для характеристик
        st.markdown("**Экстраверт vs Интроверт**")
        ei_value = st.slider("", 0, 100, 50, key="mbti_ei", label_visibility="collapsed")
        col1, col2, col3 = st.columns(3)
        col1.markdown("<div style='text-align: center;'>Экстраверт</div>", unsafe_allow_html=True)
        col2.markdown(f"<div style='text-align: center; font-weight: bold;'>{ei_value}</div>", unsafe_allow_html=True)
        col3.markdown("<div style='text-align: center;'>Интроверт</div>", unsafe_allow_html=True)
        
        st.markdown("**Реалист vs Мечтатель**")
        ns_value = st.slider("", 0, 100, 50, key="mbti_ns", label_visibility="collapsed")
        col1, col2, col3 = st.columns(3)
        col1.markdown("<div style='text-align: center;'>Реалист</div>", unsafe_allow_html=True)
        col2.markdown(f"<div style='text-align: center; font-weight: bold;'>{ns_value}</div>", unsafe_allow_html=True)
        col3.markdown("<div style='text-align: center;'>Мечтатель</div>", unsafe_allow_html=True)
        
        st.markdown("**Рациональный vs Эмоциональный**")
        tf_value = st.slider("", 0, 100, 50, key="mbti_tf", label_visibility="collapsed")
        col1, col2, col3 = st.columns(3)
        col1.markdown("<div style='text-align: center;'>Рациональный</div>", unsafe_allow_html=True)
        col2.markdown(f"<div style='text-align: center; font-weight: bold;'>{tf_value}</div>", unsafe_allow_html=True)
        col3.markdown("<div style='text-align: center;'>Эмоциональный</div>", unsafe_allow_html=True)
        
        st.markdown("**Структурный vs Спонтанный**")
        jp_value = st.slider("", 0, 100, 50, key="mbti_jp", label_visibility="collapsed")
        col1, col2, col3 = st.columns(3)
        col1.markdown("<div style='text-align: center;'>Структурный</div>", unsafe_allow_html=True)
        col2.markdown(f"<div style='text-align: center; font-weight: bold;'>{jp_value}</div>", unsafe_allow_html=True)
        col3.markdown("<div style='text-align: center;'>Спонтанный</div>", unsafe_allow_html=True)
        
        # Стиль общения
        st.markdown("### 💬 Стиль общения")
        styles = ["Дружелюбный", "Флиртующий", "Прямолинейный", "Загадочный", "Интеллектуальный"]
        cols = st.columns(len(styles))
        for i, style in enumerate(styles):
            with cols[i]:
                if st.button(style, key=f"style_{style}"):
                    st.session_state.char_settings["style"] = style
                    st.rerun()
                selected = st.session_state.char_settings["style"] == style
                color = "#6a11cb" if selected else "#f0f0f0"
                text_color = "white" if selected else "#333"
                st.markdown(f"""
                    <div style="
                        background: {'linear-gradient(145deg, #6a11cb, #2575fc)' if selected else '#f0f0f0'};
                        border-radius: 16px;
                        padding: 15px 5px;
                        text-align: center;
                        color: {text_color};
                        font-weight: bold;
                        font-size: 1rem;
                    ">
                        {style}
                    </div>
                """, unsafe_allow_html=True)
        
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
                st.markdown(f"""
                    <div class="tag {'selected' if selected else ''} hobby-btn">
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
                st.markdown(f"""
                    <div class="tag {'selected' if selected else ''} music-btn">
                        {music}
                    </div>
                """, unsafe_allow_html=True)
        
        # --- Блок "Внешний вайб" ---
        st.markdown("### 👗 Внешний вайб")
        
        # Стиль одежды
        st.markdown("**Стиль одежды:**")
        fashion_options = ["Casual", "Спорт-шик", "Elegant", "Dark-academia", "Soft-girl", "Бохо", "Минимализм"]
        cols = st.columns(4)
        for i, fashion in enumerate(fashion_options):
            with cols[i % 4]:
                if st.button(fashion, key=f"fashion_{fashion}"):
                    st.session_state.char_settings["fashion"] = fashion
                    st.rerun()
                selected = fashion == st.session_state.char_settings["fashion"]
                st.markdown(f"""
                    <div class="tag {'selected' if selected else ''} fashion-btn">
                        {fashion}
                    </div>
                """, unsafe_allow_html=True)
        
        # Визуальный вайб
        st.markdown("**Визуальный вайб:**")
        vibe_options = ["Солнечный", "Таинственный", "Гик", "Арт-бохо", "Романтичный", "Брутальный", "Утонченный"]
        cols = st.columns(4)
        for i, vibe in enumerate(vibe_options):
            with cols[i % 4]:
                if st.button(vibe, key=f"vibe_{vibe}"):
                    st.session_state.char_settings["vibe"] = vibe
                    st.rerun()
                selected = vibe == st.session_state.char_settings["vibe"]
                st.markdown(f"""
                    <div class="tag {'selected' if selected else ''} vibe-btn">
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
                st.markdown(f"""
                    <div class="tag {'selected' if selected else ''} trait-btn">
                        {trait}
                    </div>
                """, unsafe_allow_html=True)
        
        # Темперамент
        st.markdown("**Темперамент:**")
        temper_options = ["Спокойный", "Энергичный", "Сбалансированный", "Импульсивный", "Флегматичный"]
        cols = st.columns(5)
        for i, temper in enumerate(temper_options):
            with cols[i % 5]:
                if st.button(temper, key=f"temper_{temper}"):
                    st.session_state.char_settings["temper"] = temper
                    st.rerun()
                selected = temper == st.session_state.char_settings["temper"]
                st.markdown(f"""
                    <div class="tag {'selected' if selected else ''} temper-btn">
                        {temper}
                    </div>
                """, unsafe_allow_html=True)
        
        # --- Блок "Красные флаги" ---
        st.markdown("### 🚩 Что вам не нравится?")
        
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
                st.markdown(f"""
                    <div class="tag {'selected' if selected else ''} dislike-btn">
                        {dislike}
                    </div>
                """, unsafe_allow_html=True)
        
        # Кнопка сохранения
        if st.button("✅ Сохранить персонажа", type="primary", use_container_width=True):
            st.session_state.personality_saved = True
            st.rerun()

# --- 6. Чат и логика взаимодействия ---
if st.session_state.get("personality_saved", False) or (
    st.session_state.get("character_created", False) and st.session_state.character_type != "custom"
):
    # Карточка персонажа
    with st.container():
        st.markdown('<div class="character-card">', unsafe_allow_html=True)
        
        # Определение аватара в зависимости от типа персонажа
        if st.session_state.character_type == "premade_1":
            avatar = "⚡"
            name = "Алексей"
        elif st.session_state.character_type == "premade_2":
            avatar = "🌹"
            name = "Анна"
        elif st.session_state.character_type == "premade_3":
            avatar = "🎨"
            name = "Макс"
        else:
            gender = st.session_state.char_settings["gender"]
            if gender == "Девушка":
                avatar = "👩"
                name = "София"
            elif gender == "Парень":
                avatar = "👨"
                name = "Марк"
            else:
                avatar = "👤"
                name = "Тейлор"
        
        st.markdown(f'<div class="avatar" style="background: linear-gradient(145deg, #6a11cb, #2575fc); color: white;">{avatar}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="character-info">', unsafe_allow_html=True)
        st.markdown(f'<div class="character-name">{name}</div>', unsafe_allow_html=True)
        
        # Описание персонажа
        if st.session_state.character_type == "premade_1":
            desc = "Энергичный экстраверт, любит спорт и активный отдых"
        elif st.session_state.character_type == "premade_2":
            desc = "Романтичная интровертка, ценит искусство и глубокие разговоры"
        elif st.session_state.character_type == "premade_3":
            desc = "Загадочный артистичный тип, полон творческих идей"
        else:
            desc = f"{st.session_state.char_settings['age']} лет, {st.session_state.char_settings['city']}"
        
        st.markdown(f'<div>{desc}</div>', unsafe_allow_html=True)
        
        # Теги персонажа
        st.markdown('<div class="character-tags">', unsafe_allow_html=True)
        if st.session_state.character_type == "premade_1":
            tags = ["Экстраверт", "Спорт", "Энергичный"]
        elif st.session_state.character_type == "premade_2":
            tags = ["Романтик", "Искусство", "Интроверт"]
        elif st.session_state.character_type == "premade_3":
            tags = ["Творческий", "Необычный", "Сюрпризы"]
        else:
            tags = []
            if st.session_state.char_settings["traits"]:
                tags.extend(st.session_state.char_settings["traits"][:2])
            if st.session_state.char_settings["hobbies"]:
                tags.append(st.session_state.char_settings["hobbies"][0])
            if st.session_state.char_settings["temper"]:
                tags.append(st.session_state.char_settings["temper"])
        
        for tag in tags[:3]:
            st.markdown(f'<div class="character-tag">{tag}</div>', unsafe_allow_html=True)
        
        st.markdown('</div></div></div>', unsafe_allow_html=True)
    
    # Для готовых персонажей устанавливаем предустановки
    if st.session_state.character_type.startswith("premade"):
        if st.session_state.character_type == "premade_1":
            # Энергичный экстраверт
            st.session_state.mbti_ei = 80
            st.session_state.mbti_ns = 30
            st.session_state.mbti_tf = 60
            st.session_state.mbti_jp = 70
            st.session_state.char_settings = {
                "gender": "Парень",
                "age": "23-27",
                "city": "Москва",
                "fashion": "Спорт-шик",
                "vibe": "Энергичный",
                "hobbies": ["Спорт", "Путешествия", "Кино"],
                "music": ["Рок", "Электроника"],
                "traits": ["Экстраверт", "Уверенный"],
                "temper": "Энергичный",
                "dislikes": ["Лень", "Пассивность"],
                "style": "Прямолинейный"
            }
        elif st.session_state.character_type == "premade_2":
            # Романтичный интроверт
            st.session_state.mbti_ei = 20
            st.session_state.mbti_ns = 80
            st.session_state.mbti_tf = 70
            st.session_state.mbti_jp = 40
            st.session_state.char_settings = {
                "gender": "Девушка",
                "age": "23-27",
                "city": "Санкт-Петербург",
                "fashion": "Романтичный",
                "vibe": "Нежный",
                "hobbies": ["Чтение", "Искусство", "Музыка"],
                "music": ["Инди", "Классика"],
                "traits": ["Романтичный", "Интроверт"],
                "temper": "Спокойный",
                "dislikes": ["Грубость", "Нарциссизм"],
                "style": "Романтичный"
            }
        elif st.session_state.character_type == "premade_3":
            # Загадочный артистичный
            st.session_state.mbti_ei = 50
            st.session_state.mbti_ns = 65
            st.session_state.mbti_tf = 75
            st.session_state.mbti_jp = 60
            st.session_state.char_settings = {
                "gender": "Небинарный",
                "age": "23-27",
                "city": "Другой",
                "fashion": "Бохо",
                "vibe": "Загадочный",
                "hobbies": ["Искусство", "Фотография", "Путешествия"],
                "music": ["Инди", "Джаз", "Экспериментальная"],
                "traits": ["Творческий", "Мечтатель"],
                "temper": "Сбалансированный",
                "dislikes": ["Ограничения", "Консерватизм"],
                "style": "Загадочный"
            }

    # Текстовое описание характеристик
    mbti_text = f"""
    MBTI черты: {'Экстраверт' if st.session_state.get('mbti_ei', 50) > 50 else 'Интроверт'}, 
    {'Мечтатель' if st.session_state.get('mbti_ns', 50) > 50 else 'Реалист'}, 
    {'Эмоциональный' if st.session_state.get('mbti_tf', 50) > 50 else 'Рациональный'}, 
    {'Спонтанный' if st.session_state.get('mbti_jp', 50) > 50 else 'Структурный'}.
    Стиль общения: {st.session_state.char_settings.get("style", "Дружелюбный").lower()}.
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
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    for m in st.session_state.msgs:
        if m["role"] == "user":
            st.markdown(f"""
                <div class="message-container user-container">
                    <div class="message-name">Вы</div>
                    <div class="user-message">{m["content"].split(':', 1)[1].strip()}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="message-container bot-container">
                    <div class="message-name">{name}</div>
                    <div class="bot-message">{m["content"]}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Feedback ---
    st.divider()
    if st.button("Получить фидбек о моём стиле общения", use_container_width=True):
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

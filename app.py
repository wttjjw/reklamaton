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
        "age": "23-27",
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
        :root {
            --primary: #6a11cb;
            --secondary: #2575fc;
            --accent: #ff6b6b;
            --success: #4CAF50;
            --warning: #FF9800;
            --danger: #F44336;
            --light: #f8f9fa;
            --dark: #212529;
        }
        
        body {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            background-attachment: fixed;
            background-size: cover;
            color: var(--dark);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .stApp {
            background: rgba(255, 255, 255, 0.92);
            border-radius: 24px;
            box-shadow: 0 12px 40px rgba(31, 38, 135, 0.3);
            backdrop-filter: blur(8px);
            margin: 2rem auto;
            padding: 2.5rem;
            max-width: 900px;
        }
        
        h1, h2, h3 {
            color: var(--primary);
            font-weight: 700;
            margin-bottom: 1.2rem;
        }
        
        .section {
            background: rgba(255, 255, 255, 0.8);
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 28px;
            box-shadow: 0 6px 24px rgba(0,0,0,0.08);
            border-left: 5px solid var(--primary);
            transition: all 0.3s ease;
        }
        
        .section:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.12);
        }
        
        .section-title {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 1.8rem;
            margin-bottom: 1.5rem;
            color: var(--primary);
        }
        
        .tag {
            display: inline-block;
            border-radius: 20px;
            padding: 10px 20px;
            margin: 8px 6px;
            cursor: pointer;
            transition: all 0.25s;
            text-align: center;
            font-weight: 600;
            box-shadow: 0 4px 10px rgba(0,0,0,0.08);
            border: 2px solid transparent;
            min-width: 120px;
        }
        
        .tag:hover {
            transform: translateY(-3px) scale(1.03);
            box-shadow: 0 8px 15px rgba(0,0,0,0.12);
        }
        
        .tag.selected {
            color: white !important;
            font-weight: 700;
            box-shadow: 0 6px 15px rgba(0,0,0,0.15);
            border: 2px solid white;
        }
        
        .slider-container {
            background: rgba(255, 255, 255, 0.7);
            border-radius: 16px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }
        
        .slider-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            font-weight: 600;
            color: var(--primary);
        }
        
        .slider-values {
            display: flex;
            justify-content: space-between;
            margin-top: 5px;
            color: var(--dark);
            font-weight: 500;
        }
        
        .save-btn {
            background: linear-gradient(145deg, var(--success), #2E7D32);
            color: white !important;
            font-size: 1.2rem;
            font-weight: 700;
            padding: 16px 32px !important;
            border-radius: 16px !important;
            margin-top: 20px;
            width: 100%;
            transition: all 0.3s !important;
            box-shadow: 0 8px 20px rgba(76, 175, 80, 0.3) !important;
        }
        
        .save-btn:hover {
            transform: translateY(-5px) !important;
            box-shadow: 0 12px 25px rgba(76, 175, 80, 0.4) !important;
        }
        
        .emoji-badge {
            font-size: 1.8rem;
            margin-right: 10px;
            vertical-align: middle;
        }
        
        .character-card {
            background: linear-gradient(145deg, #ffffff, #f8f9fa);
            border-radius: 24px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 12px 30px rgba(0,0,0,0.12);
            text-align: center;
            border: 2px solid rgba(106, 17, 203, 0.2);
        }
        
        .character-avatar {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: linear-gradient(145deg, var(--primary), var(--secondary));
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 60px;
            color: white;
            box-shadow: 0 8px 20px rgba(106, 17, 203, 0.3);
        }
        
        .character-name {
            font-size: 2rem;
            font-weight: 800;
            color: var(--primary);
            margin-bottom: 10px;
        }
        
        .character-desc {
            font-size: 1.2rem;
            color: var(--dark);
            margin-bottom: 20px;
            line-height: 1.6;
        }
        
        .character-tags {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 12px;
            margin-top: 20px;
        }
        
        .character-tag {
            background: rgba(106, 17, 203, 0.15);
            color: var(--primary);
            border-radius: 20px;
            padding: 8px 16px;
            font-size: 1rem;
            font-weight: 600;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }
        
        .chat-container {
            background: rgba(255, 255, 255, 0.85);
            border-radius: 24px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            max-height: 500px;
            overflow-y: auto;
        }
        
        .message-container {
            margin-bottom: 20px;
        }
        
        .user-message {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            border-radius: 24px 24px 8px 24px;
            padding: 16px 22px;
            margin-left: 20%;
            box-shadow: 0 6px 15px rgba(106, 17, 203, 0.25);
        }
        
        .bot-message {
            background: white;
            color: var(--dark);
            border-radius: 24px 24px 24px 8px;
            padding: 16px 22px;
            margin-right: 20%;
            box-shadow: 0 6px 15px rgba(0,0,0,0.08);
            border: 1px solid rgba(106, 17, 203, 0.1);
        }
        
        .message-name {
            font-weight: 700;
            margin-bottom: 8px;
            font-size: 0.95rem;
            color: var(--primary);
        }
        
        .feedback-btn {
            background: linear-gradient(145deg, var(--warning), #EF6C00);
            color: white !important;
            font-weight: 700;
            padding: 14px 28px !important;
            border-radius: 16px !important;
            width: 100%;
            margin-top: 20px;
            transition: all 0.3s !important;
            box-shadow: 0 8px 20px rgba(255, 152, 0, 0.3) !important;
        }
        
        .feedback-btn:hover {
            transform: translateY(-5px) !important;
            box-shadow: 0 12px 25px rgba(255, 152, 0, 0.4) !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. Центральная анкета пользователя ---
if not st.session_state.form_saved:
    st.title("✨ DreamDate AI — тренируйся в дейтинге")
    
    with st.form("user_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Ваше имя", key="name", label_visibility="visible", 
                                placeholder="Как к вам обращаться?")
        with col2:
            sex = st.selectbox("Ваш пол", options=["Мужской", "Женский"], key="sex")
        
        birthdate = st.date_input("Дата рождения", 
                                min_value=datetime.date(1950, 1, 1),
                                max_value=datetime.date(2007, 12, 31))
        
        if st.form_submit_button("Сохранить анкету", type="primary", use_container_width=True):
            st.session_state.form_saved = True
            st.session_state.user_name = name
            st.session_state.character_created = False
            st.session_state.personality_saved = False
            st.rerun()

# --- 4. Выбор типа персонажа ---
if st.session_state.form_saved and not st.session_state.character_created:
    st.title("👥 Выберите тип персонажа")
    
    # Кнопка создания персонажа
    st.markdown("""
        <div class="character-card" style="cursor:pointer;" onclick="this.nextElementSibling.click()">
            <div class="character-avatar">✨</div>
            <div class="character-name">Создать своего персонажа</div>
            <div class="character-desc">Полная кастомизация характера и стиля</div>
            <div class="character-tags">
                <div class="character-tag">Индивидуально</div>
                <div class="character-tag">Уникально</div>
                <div class="character-tag">Персонализировано</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Создать персонажа", key="create_custom_main", use_container_width=True):
        st.session_state.character_type = "custom"
        st.session_state.character_created = True
        st.rerun()
    
    # Готовые персонажи
    st.markdown('<h2 style="text-align: center; margin: 40px 0 25px 0; color: #6a11cb;">Или выберите готового персонажа:</h2>', unsafe_allow_html=True)
    
    # Персонаж 1
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="character-card" style="cursor:pointer;" onclick="this.nextElementSibling.click()">
                <div class="character-avatar" style="background:linear-gradient(145deg, #2196F3, #0D47A1);">⚡</div>
                <div class="character-name">Алексей</div>
                <div class="character-desc">Энергичный экстраверт, любит спорт и активный отдых</div>
                <div class="character-tags">
                    <div class="character-tag">Экстраверт</div>
                    <div class="character-tag">Спорт</div>
                    <div class="character-tag">Энергичный</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Выбрать", key="premade_1_main", use_container_width=True):
            st.session_state.character_type = "premade_1"
            st.session_state.character_created = True
            st.rerun()
    
    # Персонаж 2
    with col2:
        st.markdown("""
            <div class="character-card" style="cursor:pointer;" onclick="this.nextElementSibling.click()">
                <div class="character-avatar" style="background:linear-gradient(145deg, #9C27B0, #6A1B9A);">🌹</div>
                <div class="character-name">Анна</div>
                <div class="character-desc">Романтичная интровертка, ценит искусство и разговоры</div>
                <div class="character-tags">
                    <div class="character-tag">Романтик</div>
                    <div class="character-tag">Искусство</div>
                    <div class="character-tag">Интроверт</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Выбрать", key="premade_2_main", use_container_width=True):
            st.session_state.character_type = "premade_2"
            st.session_state.character_created = True
            st.rerun()
    
    # Персонаж 3
    with col3:
        st.markdown("""
            <div class="character-card" style="cursor:pointer;" onclick="this.nextElementSibling.click()">
                <div class="character-avatar" style="background:linear-gradient(145deg, #FF9800, #EF6C00);">🎨</div>
                <div class="character-name">Макс</div>
                <div class="character-desc">Творческая личность с необычным взглядом на мир</div>
                <div class="character-tags">
                    <div class="character-tag">Творческий</div>
                    <div class="character-tag">Необычный</div>
                    <div class="character-tag">Сюрпризы</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Выбрать", key="premade_3_main", use_container_width=True):
            st.session_state.character_type = "premade_3"
            st.session_state.character_created = True
            st.rerun()

# --- 5. Создание кастомного персонажа ---
if st.session_state.get("character_created", False) and st.session_state.character_type == "custom":
    if "personality_saved" not in st.session_state:
        st.session_state.personality_saved = False
    
    if not st.session_state.personality_saved:
        st.title("🎭 Создайте своего персонажа")
        
        # --- Основные настройки ---
        with st.container():
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><span>👤</span> Основная информация</div>', unsafe_allow_html=True)
            
            # Пол персонажа
            st.markdown('<div class="slider-header"><span>👫</span> Пол персонажа</div>', unsafe_allow_html=True)
            genders = ["Девушка", "Парень", "Небинарный"]
            cols = st.columns(3)
            for i, gender in enumerate(genders):
                with cols[i]:
                    if st.button(gender, key=f"gender_{gender}"):
                        st.session_state.char_settings["gender"] = gender
                        st.rerun()
                    selected = st.session_state.char_settings["gender"] == gender
                    bg = "linear-gradient(145deg, #9C27B0, #6A1B9A)" if selected else "rgba(156, 39, 176, 0.15)"
                    st.markdown(f"""
                        <div class="tag {'selected' if selected else ''}" 
                             style="background: {bg}; {'color: white;' if selected else 'color: #6A1B9A;'}">
                            {gender}
                        </div>
                    """, unsafe_allow_html=True)
            
            # Возраст
            st.markdown('<div class="slider-header"><span>🎂</span> Возраст</div>', unsafe_allow_html=True)
            ages = ["18-22", "23-27", "28-32", "33+"]
            cols = st.columns(4)
            for i, age in enumerate(ages):
                with cols[i]:
                    if st.button(age, key=f"age_{age}"):
                        st.session_state.char_settings["age"] = age
                        st.rerun()
                    selected = st.session_state.char_settings["age"] == age
                    bg = "linear-gradient(145deg, #2196F3, #0D47A1)" if selected else "rgba(33, 150, 243, 0.15)"
                    st.markdown(f"""
                        <div class="tag {'selected' if selected else ''}" 
                             style="background: {bg}; {'color: white;' if selected else 'color: #0D47A1;'}">
                            {age}
                        </div>
                    """, unsafe_allow_html=True)
            
            # Город
            st.markdown('<div class="slider-header"><span>🏙️</span> Город</div>', unsafe_allow_html=True)
            cities = ["Москва", "Санкт-Петербург", "Казань", "Сочи", "Екатеринбург", "Другой"]
            cols = st.columns(3)
            for i, city in enumerate(cities):
                with cols[i % 3]:
                    if st.button(city, key=f"city_{city}"):
                        st.session_state.char_settings["city"] = city
                        st.rerun()
                    selected = st.session_state.char_settings["city"] == city
                    bg = "linear-gradient(145deg, #4CAF50, #2E7D32)" if selected else "rgba(76, 175, 80, 0.15)"
                    st.markdown(f"""
                        <div class="tag {'selected' if selected else ''}" 
                             style="background: {bg}; {'color: white;' if selected else 'color: #1B5E20;'}">
                            {city}
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)  # конец секции
        
        # --- Характер ---
        with st.container():
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><span>🧠</span> Характер персонажа</div>', unsafe_allow_html=True)
            
            # Слайдеры для характеристик
            st.markdown('<div class="slider-container">', unsafe_allow_html=True)
            st.markdown('<div class="slider-header"><span>🔊</span> Экстраверт vs Интроверт</div>', unsafe_allow_html=True)
            ei_value = st.slider("", 0, 100, 50, key="mbti_ei", label_visibility="collapsed")
            st.markdown('<div class="slider-values">', unsafe_allow_html=True)
            st.markdown('<div>Общительный</div><div>Созерцательный</div>', unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)
            
            st.markdown('<div class="slider-container">', unsafe_allow_html=True)
            st.markdown('<div class="slider-header"><span>🌈</span> Реалист vs Мечтатель</div>', unsafe_allow_html=True)
            ns_value = st.slider("", 0, 100, 50, key="mbti_ns", label_visibility="collapsed")
            st.markdown('<div class="slider-values">', unsafe_allow_html=True)
            st.markdown('<div>Практичный</div><div>Творческий</div>', unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)
            
            st.markdown('<div class="slider-container">', unsafe_allow_html=True)
            st.markdown('<div class="slider-header"><span>💖</span> Рациональный vs Эмоциональный</div>', unsafe_allow_html=True)
            tf_value = st.slider("", 0, 100, 50, key="mbti_tf", label_visibility="collapsed")
            st.markdown('<div class="slider-values">', unsafe_allow_html=True)
            st.markdown('<div>Логичный</div><div>Чувствительный</div>', unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)
            
            st.markdown('<div class="slider-container">', unsafe_allow_html=True)
            st.markdown('<div class="slider-header"><span>📅</span> Структурный vs Спонтанный</div>', unsafe_allow_html=True)
            jp_value = st.slider("", 0, 100, 50, key="mbti_jp", label_visibility="collapsed")
            st.markdown('<div class="slider-values">', unsafe_allow_html=True)
            st.markdown('<div>Организованный</div><div>Импульсивный</div>', unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)  # конец секции
        
        # --- Стиль общения ---
        with st.container():
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><span>💬</span> Стиль общения</div>', unsafe_allow_html=True)
            
            styles = ["Дружелюбный", "Флиртующий", "Прямолинейный", "Загадочный", "Интеллектуальный"]
            cols = st.columns(len(styles))
            for i, style in enumerate(styles):
                with cols[i]:
                    if st.button(style, key=f"style_{style}"):
                        st.session_state.char_settings["style"] = style
                        st.rerun()
                    selected = st.session_state.char_settings["style"] == style
                    bg = "linear-gradient(145deg, #6a11cb, #2575fc)" if selected else "rgba(106, 17, 203, 0.15)"
                    st.markdown(f"""
                        <div class="tag {'selected' if selected else ''}" 
                             style="background: {bg}; {'color: white;' if selected else 'color: #6a11cb;'}">
                            {style}
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)  # конец секции
        
        # --- Интересы ---
        with st.container():
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><span>🎯</span> Мне интересно</div>', unsafe_allow_html=True)
            
            # Хобби
            st.markdown('<div class="slider-header"><span>🎨</span> Хобби</div>', unsafe_allow_html=True)
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
                    bg = "linear-gradient(145deg, #2196F3, #0D47A1)" if selected else "rgba(33, 150, 243, 0.15)"
                    st.markdown(f"""
                        <div class="tag {'selected' if selected else ''}" 
                             style="background: {bg}; {'color: white;' if selected else 'color: #0D47A1;'}">
                            {hobby}
                        </div>
                    """, unsafe_allow_html=True)
            
            # Музыка
            st.markdown('<div class="slider-header"><span>🎵</span> Музыкальные предпочтения</div>', unsafe_allow_html=True)
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
                    bg = "linear-gradient(145deg, #FF9800, #EF6C00)" if selected else "rgba(255, 152, 0, 0.15)"
                    st.markdown(f"""
                        <div class="tag {'selected' if selected else ''}" 
                             style="background: {bg}; {'color: white;' if selected else 'color: #E65100;'}">
                            {music}
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)  # конец секции
        
        # --- Внешний вайб ---
        with st.container():
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><span>👗</span> Внешний вайб</div>', unsafe_allow_html=True)
            
            # Стиль одежды
            st.markdown('<div class="slider-header"><span>👕</span> Стиль одежды</div>', unsafe_allow_html=True)
            fashion_options = ["Casual", "Спорт-шик", "Elegant", "Dark-academia", "Soft-girl", "Бохо", "Минимализм"]
            cols = st.columns(4)
            for i, fashion in enumerate(fashion_options):
                with cols[i % 4]:
                    if st.button(fashion, key=f"fashion_{fashion}"):
                        st.session_state.char_settings["fashion"] = fashion
                        st.rerun()
                    selected = fashion == st.session_state.char_settings["fashion"]
                    bg = "linear-gradient(145deg, #4CAF50, #2E7D32)" if selected else "rgba(76, 175, 80, 0.15)"
                    st.markdown(f"""
                        <div class="tag {'selected' if selected else ''}" 
                             style="background: {bg}; {'color: white;' if selected else 'color: #1B5E20;'}">
                            {fashion}
                        </div>
                    """, unsafe_allow_html=True)
            
            # Визуальный вайб
            st.markdown('<div class="slider-header"><span>🌟</span> Визуальный вайб</div>', unsafe_allow_html=True)
            vibe_options = ["Солнечный", "Таинственный", "Гик", "Арт-бохо", "Романтичный", "Брутальный", "Утонченный"]
            cols = st.columns(4)
            for i, vibe in enumerate(vibe_options):
                with cols[i % 4]:
                    if st.button(vibe, key=f"vibe_{vibe}"):
                        st.session_state.char_settings["vibe"] = vibe
                        st.rerun()
                    selected = vibe == st.session_state.char_settings["vibe"]
                    bg = "linear-gradient(145deg, #9C27B0, #6A1B9A)" if selected else "rgba(156, 39, 176, 0.15)"
                    st.markdown(f"""
                        <div class="tag {'selected' if selected else ''}" 
                             style="background: {bg}; {'color: white;' if selected else 'color: #6A1B9A;'}">
                            {vibe}
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)  # конец секции
        
        # --- Черты характера ---
        with st.container():
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><span>😊</span> Черты характера</div>', unsafe_allow_html=True)
            
            # Черты характера
            st.markdown('<div class="slider-header"><span>💫</span> Основные черты</div>', unsafe_allow_html=True)
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
                    bg = "linear-gradient(145deg, #9C27B0, #6A1B9A)" if selected else "rgba(156, 39, 176, 0.15)"
                    st.markdown(f"""
                        <div class="tag {'selected' if selected else ''}" 
                             style="background: {bg}; {'color: white;' if selected else 'color: #6A1B9A;'}">
                            {trait}
                        </div>
                    """, unsafe_allow_html=True)
            
            # Темперамент
            st.markdown('<div class="slider-header"><span>🔥</span> Темперамент</div>', unsafe_allow_html=True)
            temper_options = ["Спокойный", "Энергичный", "Сбалансированный", "Импульсивный", "Флегматичный"]
            cols = st.columns(5)
            for i, temper in enumerate(temper_options):
                with cols[i % 5]:
                    if st.button(temper, key=f"temper_{temper}"):
                        st.session_state.char_settings["temper"] = temper
                        st.rerun()
                    selected = temper == st.session_state.char_settings["temper"]
                    bg = "linear-gradient(145deg, #2196F3, #0D47A1)" if selected else "rgba(33, 150, 243, 0.15)"
                    st.markdown(f"""
                        <div class="tag {'selected' if selected else ''}" 
                             style="background: {bg}; {'color: white;' if selected else 'color: #0D47A1;'}">
                            {temper}
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)  # конец секции
        
        # --- Красные флаги ---
        with st.container():
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><span>🚩</span> Что вам не нравится?</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="slider-header"><span>⛔</span> Личные антипатии</div>', unsafe_allow_html=True)
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
                    bg = "linear-gradient(145deg, #F44336, #C62828)" if selected else "rgba(244, 67, 54, 0.15)"
                    st.markdown(f"""
                        <div class="tag {'selected' if selected else ''}" 
                             style="background: {bg}; {'color: white;' if selected else 'color: #B71C1C;'}">
                            {dislike}
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)  # конец секции
        
        # Кнопка сохранения
        if st.button("💾 Сохранить персонажа", key="save_character", 
                    use_container_width=True, type="primary", 
                    help="Сохранить все настройки персонажа и начать диалог"):
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
            color = "linear-gradient(145deg, #2196F3, #0D47A1)"
            desc = "Энергичный экстраверт, любит спорт и активный отдых"
            tags = ["Экстраверт", "Спорт", "Энергичный"]
        elif st.session_state.character_type == "premade_2":
            avatar = "🌹"
            name = "Анна"
            color = "linear-gradient(145deg, #9C27B0, #6A1B9A)"
            desc = "Романтичная интровертка, ценит искусство и глубокие разговоры"
            tags = ["Романтик", "Искусство", "Интроверт"]
        elif st.session_state.character_type == "premade_3":
            avatar = "🎨"
            name = "Макс"
            color = "linear-gradient(145deg, #FF9800, #EF6C00)"
            desc = "Творческая личность с необычным взглядом на мир"
            tags = ["Творческий", "Необычный", "Сюрпризы"]
        else:
            gender = st.session_state.char_settings["gender"]
            if gender == "Девушка":
                avatar = "👩"
                name = "София"
                color = "linear-gradient(145deg, #9C27B0, #6A1B9A)"
            elif gender == "Парень":
                avatar = "👨"
                name = "Марк"
                color = "linear-gradient(145deg, #2196F3, #0D47A1)"
            else:
                avatar = "👤"
                name = "Тейлор"
                color = "linear-gradient(145deg, #4CAF50, #2E7D32)"
            
            desc = f"{st.session_state.char_settings['age']} лет, {st.session_state.char_settings['city']}"
            tags = []
            if st.session_state.char_settings["traits"]:
                tags.extend(st.session_state.char_settings["traits"][:2])
            if st.session_state.char_settings["hobbies"]:
                tags.append(st.session_state.char_settings["hobbies"][0])
            if st.session_state.char_settings["temper"]:
                tags.append(st.session_state.char_settings["temper"])
        
        st.markdown(f'<div class="character-avatar" style="background: {color};">{avatar}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="character-name">{name}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="character-desc">{desc}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="character-tags">', unsafe_allow_html=True)
        for tag in tags[:3]:
            st.markdown(f'<div class="character-tag">{tag}</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)
    
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
    user_input = st.chat_input(f"Напишите {name} сообщение...")
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
                <div class="message-container">
                    <div class="message-name">Вы</div>
                    <div class="user-message">{m["content"].split(':', 1)[1].strip()}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="message-container">
                    <div class="message-name">{name}</div>
                    <div class="bot-message">{m["content"]}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Feedback ---
    if st.button("📝 Получить фидбек о моём стиле общения", key="feedback_btn", 
                use_container_width=True, help="Анализ вашего стиля общения и рекомендации"):
        user_dialog = "\n".join(
            [m["content"] for m in st.session_state.msgs if m["role"] == "user"]
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
                st.subheader("📝 Фидбек от эксперта по общению:")
                st.markdown(fb.choices[0].message.content)
        except Exception as e:
            st.error(f"Groq feedback error: {e}")

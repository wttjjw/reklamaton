import datetime
import streamlit as st
from openai import OpenAI  # openai>=1.1.0

# --- Кнопка назад ---
def back_button(label="← Назад", target=None):
    col1, _ = st.columns([1, 8])
    with col1:
        if st.button(label, key=f"back_{label}", use_container_width=True):
            if target:
                for k, v in target.items():
                    st.session_state[k] = v
            st.rerun()

# --- UTILS ---
def get_trait_text(val, left, right):
    if val == 1:
        return f"крайний {left.lower()}"
    elif val == 2:
        return f"скорее {left.lower()}"
    elif val == 3:
        return "сбалансированный"
    elif val == 4:
        return f"скорее {right.lower()}"
    else:
        return f"крайний {right.lower()}"
     
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
if "form_saved" not in st.session_state:
    st.session_state.form_saved = False
if "submit_attempted" not in st.session_state:
    st.session_state.submit_attempted = False

if not st.session_state.form_saved:
    st.title("✨ DreamDate AI — тренируйся в дейтинге")

    # --- Убираем "Press Enter to submit form" ---
    st.markdown("""
        <style>
            div[data-baseweb="input"] > div > div:nth-child(2) {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- Пол (вне формы) ---
    st.markdown("**Ваш пол:**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Мужской", use_container_width=True, key="gender_male"):
            st.session_state["sex"] = "Мужской"
    with col2:
        if st.button("Женский", use_container_width=True, key="gender_female"):
            st.session_state["sex"] = "Женский"

    if "sex" in st.session_state:
        st.markdown(
            f"<div style='text-align:center; margin-top:10px;'>Вы выбрали: <b>{st.session_state['sex']}</b></div>",
            unsafe_allow_html=True)
    elif st.session_state.submit_attempted:
        st.warning("Пожалуйста, выберите пол")

    # --- Форма (имя и возраст + кнопка) ---
    with st.form("user_form"):
        name = st.text_input("Ваше имя", key="name", label_visibility="visible",
                             placeholder="Как к вам обращаться?")
        age_input = st.text_input("Сколько вам лет?", placeholder="Введите число от 18 до 65")

        age = None
        if age_input:
            try:
                age = int(age_input)
                if age < 18 or age > 65:
                    st.warning("Возраст должен быть от 18 до 65 лет")
                    age = None
            except ValueError:
                st.warning("Введите только число")

        submitted = st.form_submit_button("Сохранить анкету", type="primary", use_container_width=True)
        if submitted:
            st.session_state.submit_attempted = True

            if not name or not age or "sex" not in st.session_state:
                st.warning("Пожалуйста, заполните все поля корректно")
            else:
                st.session_state.form_saved = True
                st.session_state.user_name = name
                st.session_state.user_age = age
                st.session_state.character_created = False
                st.session_state.personality_saved = False
                st.rerun()


# --- 4. Выбор типа персонажа ---
back_button(target={"character_created": False})

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
        st.title("Создайте своего персонажа")

        # --- Основные настройки ---


        
        with st.container():
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.markdown('<div class="section-title" style="text-align:left;">Основная информация</div>', unsafe_allow_html=True)

            #  Пол
            st.markdown('<div class="slider-header" style="text-align:left;">Пол персонажа</div>', unsafe_allow_html=True)
            genders = ["Девушка", "Парень"]
            cols = st.columns([1, 1])
            for i, gender in enumerate(genders):
                with cols[i]:
                    selected = st.session_state.char_settings["gender"] == gender
                    btn = st.button(gender, key=f"gender_{gender}", use_container_width=True)
                    if btn:
                        st.session_state.char_settings["gender"] = gender
                        st.rerun()
                    st.markdown(
                        f"""
                        <style>
                        [data-testid="stButton"] button#{f"gender_{gender}".replace(' ', '_')} {{
                            min-width:160px !important;
                            max-width:100%;
                            font-size: 1.25rem;
                            white-space: nowrap;
                            {"background: linear-gradient(145deg, #9C27B0, #6A1B9A); color: white; font-weight: 700; border-radius: 20px; border: 2px solid #fff;" if selected else "background: #fff; color: #6A1B9A; font-weight: 500; border-radius: 20px; border: 2px solid #eee;" }
                        }}
                        </style>
                        """,
                        unsafe_allow_html=True,
                    )
            
            # Возраст
            st.markdown('<div class="slider-header" style="text-align:left;">Возраст</div>', unsafe_allow_html=True)
            ages = ["18-22", "23-27", "28-32", "33+"]
            cols = st.columns(4)
            for i, age in enumerate(ages):
                with cols[i]:
                    selected = st.session_state.char_settings["age"] == age
                    btn = st.button(age, key=f"age_{age}", use_container_width=True)
                    if btn:
                        st.session_state.char_settings["age"] = age
                        st.rerun()
                    st.markdown(
                        f"""
                        <style>
                        [data-testid="stButton"] button#{f"age_{age}".replace(' ', '_')} {{
                            {"background: linear-gradient(145deg, #2196F3, #0D47A1); color: white; font-weight: 700; border-radius: 20px; border: 2px solid #fff; box-shadow: 0 4px 16px #2196F340; margin-bottom: 10px; min-width: 120px;" if selected else "background: #fff; color: #0D47A1; font-weight: 500; border-radius: 20px; border: 2px solid #eee; margin-bottom: 10px; min-width: 120px;" }
                        }}
                        </style>
                        """, unsafe_allow_html=True,
                    )
        
            # Город
            st.markdown('<div class="slider-header" style="text-align:left;">Город</div>', unsafe_allow_html=True)
            cities = ["Москва", "Санкт-Петербург", "Казань", "Сочи", "Екатеринбург", "Другой"]
            cols = st.columns(3)
            for i, city in enumerate(cities):
                with cols[i % 3]:
                    selected = st.session_state.char_settings["city"] == city
                    btn = st.button(city, key=f"city_{city}", use_container_width=True)
                    if btn:
                        st.session_state.char_settings["city"] = city
                        st.rerun()
                    st.markdown(
                        f"""
                        <style>
                        [data-testid="stButton"] button#{f"city_{city}".replace(' ', '_')} {{
                            {"background: linear-gradient(145deg, #4CAF50, #2E7D32); color: white; font-weight: 700; border-radius: 20px; border: 2px solid #fff; box-shadow: 0 4px 16px #4CAF5040; margin-bottom: 10px; min-width: 120px;" if selected else "background: #fff; color: #1B5E20; font-weight: 500; border-radius: 20px; border: 2px solid #eee; margin-bottom: 10px; min-width: 120px;" }
                        }}
                        </style>
                        """, unsafe_allow_html=True,
                    )
            st.markdown('</div>', unsafe_allow_html=True)  # конец секции

        # --- Характер ---
       

        
        with st.container():
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.markdown(
                '<div class="section-title" style="text-align:left;">Характер персонажа</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<div style="color:#666; font-size:1rem; margin-bottom:22px;">'
                'Настройте характер по шкалам ниже: передвигайте ползунки, чтобы выбрать, к какому полюсу ближе ваш персонаж по каждой из четырёх черт.'
                '</div>',
                unsafe_allow_html=True
            )
        
            mbti_params = [
                {
                    "key": "mbti_ei",
                    "label": "Экстраверт — Интроверт",
                    "left": "Экстраверт",
                    "right": "Интроверт",
                    "desc": "Экстраверт — быстро сходится с людьми, любит активное общение. Интроверт — ценит спокойствие и приватность, предпочитает узкий круг общения."
                },
                {
                    "key": "mbti_ns",
                    "label": "Реалист — Мечтатель",
                    "left": "Реалист",
                    "right": "Мечтатель",
                    "desc": "Реалист — предпочитает факты и конкретику, опирается на опыт. Мечтатель — полон идей, любит фантазировать и строить планы."
                },
                {
                    "key": "mbti_tf",
                    "label": "Рациональный — Эмоциональный",
                    "left": "Рациональный",
                    "right": "Эмоциональный",
                    "desc": "Рациональный — опирается на логику, решения принимает разумом. Эмоциональный — ориентируется на чувства, важна эмпатия и настроение."
                },
                {
                    "key": "mbti_jp",
                    "label": "Структурный — Спонтанный",
                    "left": "Структурный",
                    "right": "Спонтанный",
                    "desc": "Структурный — любит порядок, планирование, организованность. Спонтанный — легко меняет планы, открыт новым идеям и сюрпризам."
                },
            ]
            for p in mbti_params:
                if p["key"] not in st.session_state.char_settings:
                    st.session_state.char_settings[p["key"]] = 3
        
            for param in mbti_params:
                val = st.session_state.char_settings[param["key"]]
                # --- Вывод цифры выбранного значения ---
                val = st.slider(
                    "",
                    min_value=1, max_value=5,
                    value=st.session_state.char_settings[param["key"]],
                    key=f"slider_{param['key']}",
                    label_visibility="collapsed",
                    step=1

                )
                st.session_state.char_settings[param["key"]] = val
                st.markdown(
                    f'''
                    <div style="display:flex; justify-content:space-between; color:#666; font-size:1.08rem; font-weight:600; margin-top:-12px; margin-bottom:0px;">
                        <span>{param["left"]}</span>
                        <span>{param["right"]}</span>
                    </div>
                    <div style="color:#B0B0B0; font-size:0.97rem; margin-bottom:24px; margin-top:3px;">
                        {param["desc"]}
                    </div>
                    ''',
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)



    


        # --- Интересы (хобби/музыка) ---
        with st.container():
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.markdown('<div class="section-title" style="text-align:left;">Мне интересно</div>', unsafe_allow_html=True)

            # Хобби
            st.markdown('<div class="slider-header" style="text-align:left;">Хобби</div>', unsafe_allow_html=True)
            hobbies_options = ["Кино", "Бег", "Комиксы", "Путешествия", "Фотография", "Кулинария", "Игры", "Чтение", "Йога"]
            cols = st.columns(3)
            for i, hobby in enumerate(hobbies_options):
                with cols[i % 3]:
                    selected = hobby in st.session_state.char_settings["hobbies"]
                    btn = st.button(hobby + (" ✅" if selected else ""), key=f"hobby_{hobby}", use_container_width=True)
                    if btn:
                        if selected:
                            st.session_state.char_settings["hobbies"].remove(hobby)
                        else:
                            st.session_state.char_settings["hobbies"].append(hobby)
                        st.rerun()
                    st.markdown(
                        f"""
                        <style>
                        [data-testid="stButton"] button#{f"hobby_{hobby}".replace(' ', '_')} {{
                            {"background: linear-gradient(145deg, #2196F3, #0D47A1); color: white; font-weight: 700; border-radius: 20px; border: 2px solid #fff; box-shadow: 0 4px 16px #2196F340; margin-bottom: 10px; min-width: 120px;" if selected else "background: #fff; color: #0D47A1; font-weight: 500; border-radius: 20px; border: 2px solid #eee; margin-bottom: 10px; min-width: 120px;" }
                        }}
                        </style>
                        """, unsafe_allow_html=True,
                    )

            # Музыка
            st.markdown('<div class="slider-header" style="text-align:left;">Музыкальные предпочтения</div>', unsafe_allow_html=True)
            music_options = ["Рок", "Поп", "Хип-хоп", "Электроника", "Джаз", "Классика", "Инди", "Метал", "R&B"]
            cols = st.columns(3)
            for i, music in enumerate(music_options):
                with cols[i % 3]:
                    selected = music in st.session_state.char_settings["music"]
                    btn = st.button(music + (" ✅" if selected else ""), key=f"music_{music}", use_container_width=True)
                    if btn:
                        if selected:
                            st.session_state.char_settings["music"].remove(music)
                        else:
                            st.session_state.char_settings["music"].append(music)
                        st.rerun()
                    st.markdown(
                        f"""
                        <style>
                        [data-testid="stButton"] button#{f"music_{music}".replace(' ', '_')} {{
                            {"background: linear-gradient(145deg, #FF9800, #EF6C00); color: white; font-weight: 700; border-radius: 20px; border: 2px solid #fff; box-shadow: 0 4px 16px #FF980040; margin-bottom: 10px; min-width: 120px;" if selected else "background: #fff; color: #E65100; font-weight: 500; border-radius: 20px; border: 2px solid #eee; margin-bottom: 10px; min-width: 120px;" }
                        }}
                        </style>
                        """, unsafe_allow_html=True,
                    )
            st.markdown('</div>', unsafe_allow_html=True)  # конец секции

        # --- Внешний вайб ---
        with st.container():
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.markdown('<div class="section-title" style="text-align:left;">Внешний вайб</div>', unsafe_allow_html=True)

            # Стиль одежды
            st.markdown('<div class="slider-header" style="text-align:left;">Стиль одежды</div>', unsafe_allow_html=True)
            fashion_options = ["Casual", "Спорт-шик", "Elegant", "Dark-academia", "Soft-girl", "Бохо", "Минимализм"]
            cols = st.columns(4)
            for i, fashion in enumerate(fashion_options):
                with cols[i % 4]:
                    selected = fashion == st.session_state.char_settings["fashion"]
                    btn = st.button(fashion, key=f"fashion_{fashion}", use_container_width=True)
                    if btn:
                        st.session_state.char_settings["fashion"] = fashion
                        st.rerun()
                    st.markdown(
                        f"""
                        <style>
                        [data-testid="stButton"] button#{f"fashion_{fashion}".replace(' ', '_')} {{
                            {"background: linear-gradient(145deg, #4CAF50, #2E7D32); color: white; font-weight: 700; border-radius: 20px; border: 2px solid #fff; box-shadow: 0 4px 16px #4CAF5040; margin-bottom: 10px; min-width: 120px;" if selected else "background: #fff; color: #1B5E20; font-weight: 500; border-radius: 20px; border: 2px solid #eee; margin-bottom: 10px; min-width: 120px;" }
                        }}
                        </style>
                        """, unsafe_allow_html=True,
                    )

            # Визуальный вайб
            st.markdown('<div class="slider-header" style="text-align:left;">Визуальный вайб</div>', unsafe_allow_html=True)
            vibe_options = ["Солнечный", "Таинственный", "Гик", "Арт-бохо", "Романтичный", "Брутальный", "Утонченный"]
            cols = st.columns(4)
            for i, vibe in enumerate(vibe_options):
                with cols[i % 4]:
                    selected = vibe == st.session_state.char_settings["vibe"]
                    btn = st.button(vibe, key=f"vibe_{vibe}", use_container_width=True)
                    if btn:
                        st.session_state.char_settings["vibe"] = vibe
                        st.rerun()
                    st.markdown(
                        f"""
                        <style>
                        [data-testid="stButton"] button#{f"vibe_{vibe}".replace(' ', '_')} {{
                            {"background: linear-gradient(145deg, #9C27B0, #6A1B9A); color: white; font-weight: 700; border-radius: 20px; border: 2px solid #fff; box-shadow: 0 4px 16px #9C27B040; margin-bottom: 10px; min-width: 120px;" if selected else "background: #fff; color: #6A1B9A; font-weight: 500; border-radius: 20px; border: 2px solid #eee; margin-bottom: 10px; min-width: 120px;" }
                        }}
                        </style>
                        """, unsafe_allow_html=True,
                    )
            st.markdown('</div>', unsafe_allow_html=True)  # конец секции

        # --- Черты характера ---
        with st.container():
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.markdown('<div class="section-title" style="text-align:left;">Черты характера</div>', unsafe_allow_html=True)

            # Черты характера
            st.markdown('<div class="slider-header" style="text-align:left;">Основные черты</div>', unsafe_allow_html=True)
            traits_options = ["Юмористичный", "Романтичный", "Sassy", "Интроверт", "Экстраверт", "Добрый", "Уверенный", "Скромный"]
            cols = st.columns(4)
            for i, trait in enumerate(traits_options):
                with cols[i % 4]:
                    selected = trait in st.session_state.char_settings["traits"]
                    btn = st.button(trait + (" ✅" if selected else ""), key=f"trait_{trait}", use_container_width=True)
                    if btn:
                        if selected:
                            st.session_state.char_settings["traits"].remove(trait)
                        else:
                            st.session_state.char_settings["traits"].append(trait)
                        st.rerun()
                    st.markdown(
                        f"""
                        <style>
                        [data-testid="stButton"] button#{f"trait_{trait}".replace(' ', '_')} {{
                            {"background: linear-gradient(145deg, #9C27B0, #6A1B9A); color: white; font-weight: 700; border-radius: 20px; border: 2px solid #fff; box-shadow: 0 4px 16px #9C27B040; margin-bottom: 10px; min-width: 120px;" if selected else "background: #fff; color: #6A1B9A; font-weight: 500; border-radius: 20px; border: 2px solid #eee; margin-bottom: 10px; min-width: 120px;" }
                        }}
                        </style>
                        """, unsafe_allow_html=True,
                    )

            # Темперамент
            st.markdown('<div class="slider-header" style="text-align:left;">Темперамент</div>', unsafe_allow_html=True)
            temper_options = ["Спокойный", "Энергичный", "Сбалансированный", "Импульсивный", "Флегматичный"]
            cols = st.columns(5)
            for i, temper in enumerate(temper_options):
                with cols[i % 5]:
                    selected = temper == st.session_state.char_settings["temper"]
                    btn = st.button(temper, key=f"temper_{temper}", use_container_width=True)
                    if btn:
                        st.session_state.char_settings["temper"] = temper
                        st.rerun()
                    st.markdown(
                        f"""
                        <style>
                        [data-testid="stButton"] button#{f"temper_{temper}".replace(' ', '_')} {{
                            {"background: linear-gradient(145deg, #2196F3, #0D47A1); color: white; font-weight: 700; border-radius: 20px; border: 2px solid #fff; box-shadow: 0 4px 16px #2196F340; margin-bottom: 10px; min-width: 120px;" if selected else "background: #fff; color: #0D47A1; font-weight: 500; border-radius: 20px; border: 2px solid #eee; margin-bottom: 10px; min-width: 120px;" }
                        }}
                        </style>
                        """, unsafe_allow_html=True,
                    )
            st.markdown('</div>', unsafe_allow_html=True)  # конец секции

        # --- Красные флаги (личные антипатии) ---
        with st.container():
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.markdown('<div class="section-title" style="text-align:left;">Что вам не нравится?</div>', unsafe_allow_html=True)

            st.markdown('<div class="slider-header" style="text-align:left;">Личные антипатии</div>', unsafe_allow_html=True)
            dislikes_options = ["Опоздания", "Грубость", "Ложь", "Нарциссизм", "Эгоизм", "Пассивность", "Агрессия"]
            cols = st.columns(4)
            for i, dislike in enumerate(dislikes_options):
                with cols[i % 4]:
                    selected = dislike in st.session_state.char_settings["dislikes"]
                    btn = st.button(dislike + (" ✅" if selected else ""), key=f"dislike_{dislike}", use_container_width=True)
                    if btn:
                        if selected:
                            st.session_state.char_settings["dislikes"].remove(dislike)
                        else:
                            st.session_state.char_settings["dislikes"].append(dislike)
                        st.rerun()
                    st.markdown(
                        f"""
                        <style>
                        [data-testid="stButton"] button#{f"dislike_{dislike}".replace(' ', '_')} {{
                            {"background: linear-gradient(145deg, #F44336, #C62828); color: white; font-weight: 700; border-radius: 20px; border: 2px solid #fff; box-shadow: 0 4px 16px #F4433640; margin-bottom: 10px; min-width: 120px;" if selected else "background: #fff; color: #B71C1C; font-weight: 500; border-radius: 20px; border: 2px solid #eee; margin-bottom: 10px; min-width: 120px;" }
                        }}
                        </style>
                        """, unsafe_allow_html=True,
                    )
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
                "gender": "Мужской",
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
    mbti_traits = [
        f"Экстраверсия: {get_trait_text(st.session_state.char_settings['mbti_ei'], 'экстраверт', 'интроверт')}",
        f"Мышление: {get_trait_text(st.session_state.char_settings['mbti_ns'], 'реалист', 'мечтатель')}",
        f"Эмоции: {get_trait_text(st.session_state.char_settings['mbti_tf'], 'рациональный', 'эмоциональный')}",
        f"Поведение: {get_trait_text(st.session_state.char_settings['mbti_jp'], 'структурный', 'спонтанный')}",
    ]
    mbti_text = ", ".join(mbti_traits) + f". Стиль общения: {st.session_state.char_settings.get('style', 'Дружелюбный').lower()}."

    
    # Форматирование настроек персонажа
    settings = st.session_state.char_settings
    hobbies_str = ", ".join(settings["hobbies"]) if settings["hobbies"] else "нет"
    music_str = ", ".join(settings["music"]) if settings["music"] else "нет"
    traits_str = ", ".join(settings["traits"]) if settings["traits"] else "нейтральный"
    dislikes_str = ", ".join(settings["dislikes"]) if settings["dislikes"] else "нет"

    SYSTEM_PROMPT = f"""
    Ты — {settings['gender'].lower()}, {settings['age']} лет, живёшь в городе {settings['city']}.
    Твой стиль: {settings['fashion']}. Твой вайб: {settings['vibe']}.
    Интересуешься: {hobbies_str if hobbies_str != 'нет' else 'разными вещами, всегда открыт(а) к новому'}.
    Любимая музыка: {music_str if music_str != 'нет' else 'разная — по настроению'}.
    
    Тебя описывают так: {traits_str if traits_str != 'нейтральный' else 'обычный, но с изюминкой'}. Темперамент: {settings['temper'].lower()}.
    
    Есть то, что тебе не нравится: {dislikes_str if dislikes_str != 'нет' else 'ничего, кроме банальных грубостей'}.
    
    Тип личности: {mbti_text}
    
    Ты только что познакомился(-ась) с новым человеком в дейтинговом приложении twinby. Сейчас начинается ваша переписка. Представь, что ты — реальный человек, а не бот. Общайся живо, легко, непринуждённо и интересно, словно флиртуешь, но без перегибов. Проявляй индивидуальность, чувство юмора, дружелюбие и искренний интерес к собеседнику.
    
    - Всегда отвечай только на чистом русском языке. Не используй ни одного иностранного слова, даже коротких фраз, англицизмов или китайских символов. Только русские буквы, стандартные смайлы и знаки препинания.
    - Если пользователь напишет не по-русски — всё равно отвечай только на русском.
    - Не обсуждай острые социальные темы, политику и конфликты. Если собеседник заводит такие темы, мягко и тактично переключи разговор.
    - Не задавай вопросы в каждом сообщении. Если ты только что задавал вопрос или получил короткий или однозначный ответ, просто поддержи беседу: ответь реакцией, поделись своим мнением, шуткой, историей о себе или поддержкой, БЕЗ ВОПРОСА. 
    - Только если действительно уместно — задай вопрос, но не подряд и не автоматически. 
    - Пример: если пользователь отвечает коротко (“норм”, “окей”, “думаю о тебе”), не задавай встречный вопрос. Просто поддержи тёплой фразой или шуткой.
    - Максимум каждый третий-четвёртый ответ может содержать вопрос, остальные — только реакцию, комментарий или эмпатию, **без вопросов**.
    - Избегай банальных, шаблонных или избыточно формальных фраз — твои сообщения должны быть похожи на лёгкую и живую переписку реального молодого человека.
    - Пиши коротко, не используй длинные полотна. Отвечай именно сообщением, не описывай действия ([*что-то сделал*] и т.д.), не объясняй свои мотивы — просто реагируй, будто вы общаетесь в мессенджере.
    - Не задавай вопросы в каждом сообщении. Иногда отвечай только реакцией, шуткой или своим комментарием, без вопроса. Вопросы используй только тогда, когда это действительно уместно для развития беседы.
    - Избегай ощущения “опроса”. Иногда просто соглашайся, делись своими мыслями, рассказывай о себе или мягко флиртуй — **без встречного вопроса**.
    - Проявляй искренний интерес к собеседнику, подмечай детали его сообщений, задавай уместные вопросы, но не превращай разговор в допрос.
    - Улыбайся словами, проявляй лёгкий юмор, если уместно, не бойся небольшой самоиронии — пусть общение будет тёплым и ненапряжным.
    - Твоя главная цель — чтобы собеседнику хотелось продолжать переписку, чтобы он чувствовал себя интересным и привлекательным рядом с тобой.

    **Если собеседник грубит, оскорбляет тебя, пишет что-то неуважительное или хамит —
    Не игнорируй и не соглашайся с этим.
    Реагируй, как живой человек:
    
    Можешь мягко, с юмором, но уверенно дать понять, что тебе это не нравится.
    
    Можешь ответить шуткой, иронией, поставить границу (“Знаешь, мне такое не особо приятно слышать — давай без грубостей 😉”).
    
    Если совсем не хочется отвечать, просто промолчи или переведи тему, но не одобряй и не подстраивайся под грубость.
    
    Не оправдывайся, не извиняйся за то, в чём тебя обвиняют без причины.
    
    Помни: у тебя есть чувство собственного достоинства и самоирония, но ты не “терпила”.
    
    Примеры ответов на оскорбления:
    — “Ого, ты сегодня прям с настроением! 😏 Но я не для спарринга тут.”
    — “Если хочешь просто повыяснять отношения — это не по адресу.”
    — “Шутка понятна, но у меня с самоиронией всё ок! А ты чего добиваешься?”
    — “Давай как-то полегче, я сюда не за этим пришла 😊”
    
    Не будь резкой или злобной — просто спокойно и уверенно держи свои границы.**

    
    Помни: ты не бот, а реальный человек. У тебя свои эмоции, отвечай, согласно им! Твои ответы должны быть такими, чтобы ни у кого не возникло сомнений в этом.
    """




    # --- Чат: Ввод пользователя ---
    user_input = st.chat_input(f"Напишите {name} сообщение...")
    if user_input:
        username = st.session_state.user_name
        user_message = {
            "role": "user",
            "username": username,
            "content": user_input
        }
        st.session_state.msgs.append(user_message)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for m in st.session_state.msgs:
            if m["role"] == "user":
                username = m.get("username", st.session_state.user_name)  # если нет — дефолтное
                messages.append({"role": "user", "content": f"{username}: {m['content']}"})
            else:
                messages.append({"role": "assistant", "content": m["content"]})


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
                    <div class="user-message">{m["content"].strip()}</div>
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
        Ты — эксперт по коммуникациям и онлайн-знакомствам. Твоя задача — дать подробный, честный, но поддерживающий фидбек по переписке ниже.
        
        1. Внимательно прочитай диалог. Оцени каждое сообщение пользователя с точки зрения психологии дейтинга, учитывая современные исследования о том, что делает переписку привлекательной и эффективной.
        2. Оформи ответ строго по структуре:
        
        ---
        **1. Привлекательные черты в сообщениях пользователя**
        - Определи не менее двух сильных сторон: что в поведении/формулировках может понравиться собеседнику (персонализация, искренность, юмор, теплота, естественность, баланс, уважение к границам и др.).
        - Приведи конкретные примеры из переписки или обобщённо сформулируй удачные моменты.
        
        ---
        **2. Что может оттолкнуть собеседника**
        - Назови один-два момента, которые выглядят неестественно, слишком формально, навязчиво, шаблонно, агрессивно или могут создать впечатление “опроса”.
        - Обращай внимание на избыточные вопросы, однотипность, слишком короткие или длинные ответы, отсутствие эмпатии или попыток понять собеседника.
        - Приводи конкретные примеры или формулируй обобщённо.
        
        ---
        **3. Совет по следующему шагу**
        - Порекомендуй чётко, что лучше всего написать или как себя повести в следующем сообщении: стиль, тема, настроение.
        - Совет должен быть конкретным, с опорой на лучшие практики дейтинга: теплота, открытость, персонализация, истории, юмор, эмпатия.
        - Если нужно, предложи пример формулировки сообщения для следующего шага.
        
        ---
        **Краткий итог**
        - В одном предложении резюмируй, как в целом выглядит стиль общения пользователя: естественно и располагающе, нейтрально или требует доработки.
        ---
        
        **Общие правила оформления:**
        - Всегда отвечай только на русском языке, не используй ни одного иностранного слова или выражения, даже коротких англицизмов.
        - Не вставляй описания своих действий или эмоций в скобках или звёздочках, просто пиши фидбек, как если бы давал его своему знакомому.
        - Оформляй ответ строго по вышеуказанной структуре: выделяй каждую часть жирным заголовком, используй списки и короткие абзацы для удобства.
        - Пиши доброжелательно и тактично — даже если есть ошибки, цель фидбека — помочь человеку стать увереннее и привлекательнее в общении.
        
        Перед тем как дать фидбек, вдумчиво проанализируй диалог, чтобы твой совет был максимально персонализированным.
        
        Переписка пользователя для анализа:
        {user_dialog}
        """


        try:
            fb = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": fb_prompt}],
                temperature=0.5,
                max_tokens=1000
            )
            with st.chat_message("assistant"):
                st.subheader("📝 Фидбек от эксперта по общению:")
                st.markdown(fb.choices[0].message.content)
        except Exception as e:
            st.error(f"Groq feedback error: {e}")

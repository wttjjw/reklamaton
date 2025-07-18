"""
PersonaVerse ‑ Streamlit MVP
• Конструктор личности (Archetype DNA) + карточка сцены‑стресс‑теста
• Быстрый чат на Groq (LLM‑эндпоинт совместим с OpenAI)
• Кнопка «Обратная связь» — LLM анализирует ответы пользователя
"""

import os
import streamlit as st
from openai import OpenAI   # pip install openai>=1.1.0

# ---------- 1.  Настройка Groq  ----------
client = OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],                       # в Settings → Secrets
    base_url="https://api.groq.com/openai/v1"                 # меняем базовый URL
)

MODEL_NAME = "llama3-70b-8192"  # быстрая большая модель на Groq

# ---------- 2.  UI: конструктор DNA ----------
st.title("🧩 PersonaVerse — собери своего ИИ‑собеседника")

with st.sidebar:
    st.header("🎭 Архетип‑DNA")
    archetype  = st.selectbox("Архетип", [
        "Мудрец", "Герой", "Трикстер", "Правитель", "Любовник", "Исследователь"
    ])
    core_drive = st.selectbox("Главная мотивация (Core Drive)", [
        "Власть", "Признание", "Саморазвитие", "Приключение", "Стабильность"
    ])
    tone       = st.selectbox("Тон общения", [
        "Дружелюбный", "Саркастичный", "Холодный", "Вдохновляющий"
    ])
    mask       = st.selectbox("Внешняя маска (Mask)", [
        "Уверенный", "Робкий", "Высокомерный", "Спокойный"
    ])
    flaw       = st.selectbox("Слабое место (Flaw)", [
        "Перфекционист", "Нетерпеливый", "Нерешительный", "Нарциссичный"
    ])

    st.markdown("---")
    st.header("🃏 Сцена‑стресс‑теста")
    scenario = st.radio(
        "Выбери ситуацию",
        ["🗂️ Переговоры о зарплате",
         "🎤 Питч‑инвестору (30 сек)",
         "🍸 Small‑talk на нетворкинге",
         "🛒 Возражения клиента‑скептика",
         "🔥 Конфликт в команде"]
    )

# ---------- 3.  System‑prompt на основе DNA ----------
SYSTEM_PROMPT = f"""
Ты — персонаж‑{archetype}.
Твой Core‑Drive: {core_drive}.
Тон общения: {tone}.
Внешняя маска: {mask}.
Твоя внутренняя слабость: {flaw}.

Сцена: {scenario}.
Веди реалистичный диалог с пользователем, погружая его в ситуацию.
После каждого ответа пользователя реагируй в соответствии со своими установками,
старайся удерживать ситуацию в рамках сцены.
"""

# ---------- 4.  Хранилище истории в сессии ----------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------- 5.  Чат‑интерфейс ----------
user_msg = st.chat_input("🗨️ Введите реплику …")
if user_msg:
    st.session_state.history.append({"role": "user", "content": user_msg})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.history

    try:
        groq_response = client.chat.completions.create(
            model   = MODEL_NAME,
            messages=messages,
            temperature=0.8,
            max_tokens=256
        )
        bot_reply = groq_response.choices[0].message.content.strip()
        st.session_state.history.append({"role": "assistant", "content": bot_reply})
    except Exception as e:
        st.error(f"Groq API error: {e}")

# выводим всё
for m in st.session_state.history:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ---------- 6.  Кнопка «Обратная связь» ----------
st.markdown("---")
if st.button("🧑‍🏫 Получить обратную связь"):
    # Берём только пользовательские реплики
    user_only = "\n".join([x["content"] for x in st.session_state.history if x["role"]=="user"])
    feedback_prompt = f"""
    Ты — опытный ментор по soft‑skills. Прочитай ответы пользователя
    в стресс‑тесте ({scenario}) и дай 3 сильные стороны + 3 зоны улучшения
    в формате маркированного списка. Вот ответы:\n\n{user_only}
    """
    try:
        fb = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": feedback_prompt}
            ],
            temperature=0.5,
            max_tokens=300
        )
        with st.chat_message("assistant"):
            st.subheader("🎯 Обратная связь:")
            st.markdown(fb.choices[0].message.content)
    except Exception as e:
        st.error(f"Groq feedback error: {e}")

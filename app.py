import streamlit as st
from openai import OpenAI
import os

# Получаем API-ключ из секретов
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🧠 Фабрика AI-персонажей")

# Сайдбар с параметрами
st.sidebar.header("🎭 Настрой персонажа")
archetype = st.sidebar.selectbox("Архетип", ["Мудрец", "Герой", "Трикстер", "Правитель"])
personality = st.sidebar.text_input("Характер", "ироничный и спокойный")
bio = st.sidebar.text_area("Биография", "Живёт в башне, изучает магию...")

# Генерация system prompt
system_prompt = f"""
Ты — персонаж с архетипом {archetype}.
Твой характер: {personality}.
Биография: {bio}.
Общайся с пользователем, придерживаясь этих установок.
"""

# История чата
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Ввод от пользователя
user_input = st.chat_input("Спроси что-нибудь у персонажа")
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Подготовка всех сообщений
    messages = [{"role": "system", "content": system_prompt}] + st.session_state.chat_history

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        reply = response.choices[0].message.content.strip()
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
    except Exception as e:
        st.error(f"Ошибка OpenAI: {e}")

# Отображение диалога
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

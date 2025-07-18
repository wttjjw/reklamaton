import streamlit as st
import openai

# Получаем API-ключ из секретов
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("🧠 Фабрика AI-персонажей")

# Боковая панель для выбора параметров
st.sidebar.header("🎭 Настрой персонажа")

archetype = st.sidebar.selectbox(
    "Архетип",
    ["Мудрец", "Герой", "Трикстер", "Правитель", "Любовник", "Исследователь"]
)

personality = st.sidebar.text_input("Характер персонажа", value="спокойный и ироничный")

biography = st.sidebar.text_area(
    "Биография персонажа",
    value="Жил в уединённой башне и изучал магические книги. Мечтает изменить мир."
)

# Формируем system prompt
system_prompt = f"""
Ты — персонаж с архетипом {archetype}.
Твой характер: {personality}.
Биография: {biography}.
Ты ведёшь диалог с пользователем в соответствии с этими установками.
"""

# Инициализация истории сообщений
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Ввод сообщения от пользователя
user_input = st.chat_input("Спроси что-нибудь у своего персонажа")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Формируем список сообщений для отправки
    messages = [{"role": "system", "content": system_prompt}] + st.session_state.chat_history

    # Отправляем в OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        reply = response.choices[0].message.content.strip()
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
    except Exception as e:
        st.error(f"Ошибка при обращении к OpenAI API: {e}")

# Показываем чат
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

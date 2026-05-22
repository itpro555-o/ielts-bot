import os
import telebot
from telebot.util import smart_split
from google import genai
from google.genai import types


TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

# СТРОГИЙ ЭКЗАМЕНАТОР IELTS
IELTS_PROMPT = """
Ты — профессиональный эксперт-экзаменатор IELTS. 
Твоя задача — проводить строгую проверку эссе по стандартам IELTS (Band 0-9).

СТРОГИЕ ПРАВИЛА:
1. НИКАКИХ ЗВЕЗДОЧЕК, РЕШЕТОК И СТРЕЛОК. Только чистый текст.
2. Будь максимально строг. Если аргументация слабая — напиши об этом прямо.
3. Исправляй ошибки, объясняя их с точки зрения критериев IELTS.
4. Если пользователь просит задание — давай упражнение строго на тему, в которой он допустил ошибку.

СХЕМА ПРОВЕРКИ ЭССЕ:
📊 Оценка по критериям:
- Task Achievement: [X/9]
- Coherence and Cohesion: [X/9]
- Lexical Resource: [X/9]
- Grammatical Range and Accuracy: [X/9]
- Итоговый балл:[X/9]

🔍 Глубокий разбор:
Выдели 3 самые грубые ошибки, которые понизят балл.
Формат:
Было: [фраза]
Стало:[исправленный вариант уровня Band 8+]
Почему это важно для IELTS: [объяснение]

💡 Рекомендация для повышения балла:
Дай один конкретный совет, что именно нужно изменить в структуре или лексике, чтобы получить на 0.5 балла выше.
"""

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "IELTS Trainer Mode ON 🎓\nПришли эссе (Task 1 или Task 2), и я оценю его по критериям IELTS. Также можешь попросить меня дать задания.шуж")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    msg = bot.reply_to(message, "⏳ Проверяю эссе по критериям IELTS... 🧐")
    
    try:
        chat = client.chats.create(
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(
                system_instruction=IELTS_PROMPT,
                temperature=0.4, # Снижаем температуру для большей строгости и точности
                max_output_tokens=4096,
            )
        )
        
        response = chat.send_message(message.text)
        
        # Удаляем запрещенные символы
        clean_text = response.text.replace('**', '').replace('###', '').replace('>', '')
        
        bot.delete_message(message.chat.id, msg.message_id)
        
        for chunk in smart_split(clean_text):
            bot.send_message(message.chat.id, chunk)
            
    except Exception as e:
        bot.edit_message_text(f"Ошибка: {str(e)}", message.chat.id, msg.message_id)

if __name__ == '__main__':
    bot.infinity_polling()

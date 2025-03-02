import asyncio
import logging
import random
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.utils.markdown import hitalic
from pathlib import Path
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile
import aiofiles
from dotenv import load_dotenv
import os
import openai
import aiohttp



# Настроим логирование
logging.basicConfig(level=logging.INFO)

load_dotenv()  # Загружаем переменные окружения
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Не найден токен бота! Проверь .env файл.")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Не найден API-ключ OpenAI! Проверь .env файл.")

openai.api_key = OPENAI_API_KEY


# Создаем экземпляр бота и диспетчера
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# Пути к папке с изображениями
IMAGES_PATH = Path("images")

async def load_json(filename):
    async with aiofiles.open(filename, mode="r", encoding="utf-8") as file:
        content = await file.read()
        return json.loads(content)

async def load_data():
    global anxiety_tips, instructions_from
    messages_data = await load_json("messages.json")
    instructions_data = await load_json("instructions.json")
    anxiety_tips = messages_data.get("anxiety_tips", [])
    instructions_from = instructions_data.get("instructions_from", [])

# Функция для имитации "печатает..."
async def typing_effect(message: types.Message, delay: int = 2):
    await bot.send_chat_action(message.chat.id, "typing")
    await asyncio.sleep(delay)

# Клавиатуры
start_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Привет")]], resize_keyboard=True)
hello_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Рад(а) знакомству")]], resize_keyboard=True)
meet_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Хорошо")]], resize_keyboard=True)
feel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Немного дискомфортно")],
        [KeyboardButton(text="Поток мыслей набирает обороты")],
        [KeyboardButton(text="Тяжело...")],
        [KeyboardButton(text="Нормально")],
    ],
    resize_keyboard=True,
)

unknown_responses = [
    "Я пока не знаю такой команды 🧐",
    "Прости, но я ещё учусь 📚",
    "Я тебя не понимаю, но очень стараюсь! 💡"
]

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await typing_effect(message)
    await message.answer("Привет, друг!", reply_markup=start_kb)

@dp.message(lambda msg: msg.text == "Привет")
async def hello_reply(message: types.Message):
    await typing_effect(message)
    await message.answer("Меня зовут Иса, я - твой новый виртуальный друг!", reply_markup=hello_kb)

@dp.message(lambda msg: msg.text == "Рад(а) знакомству")
async def meet_reply(message: types.Message):
    await typing_effect(message)
    await message.answer("Я создана помочь тебе и быть рядом в моменты, когда ты испытываешь чувство тревоги.", reply_markup=meet_kb)

@dp.message(lambda msg: msg.text == "Хорошо")
async def ok_reply(message: types.Message):
    await typing_effect(message, 1)
    await message.answer("Как ты себя чувствуешь сейчас?", reply_markup=feel_kb)

@dp.message(lambda msg: msg.text == "Немного дискомфортно")
async def slight_discomfort_reply(message: types.Message):
    await typing_effect(message)
    await message.answer("Ты испытываешь лёгкую тревогу")

    await typing_effect(message, 3)
    img_path = random.choice(list(IMAGES_PATH.glob("*.jpg")))  # Выбираем случайное изображение
    photo = FSInputFile(img_path)  # Создаем объект FSInputFile
    await bot.send_photo(message.chat.id, photo=photo, caption="Не беспокойся, просто следуй этапам")

    await typing_effect(message, 3)
    await message.answer("Если это поможет тебе, будет просто замечательно. Но я всегда тут и готов тебе помочь.", reply_markup=feel_kb)

@dp.message(lambda msg: msg.text == "Поток мыслей набирает обороты")
async def its_becoming_hot_in_head(message: types.Message):
    await typing_effect(message)
    await message.answer("Ты испытываешь средней степени тяжести тревогу")

    await typing_effect(message, 1)
    await message.answer("Не беспокойся, просто следуй этапам")

    await typing_effect(message, 3)
    random_tip = random.choice(anxiety_tips)
    await message.answer(random_tip)

    await typing_effect(message, 3)
    await message.answer("Если это поможет тебе, будет просто замечательно. Но я всегда тут и готов тебе помочь.", reply_markup=feel_kb)

@dp.message(lambda msg: msg.text == "Тяжело...")
async def its_hard(message: types.Message):
    await typing_effect(message)
    await message.answer("Ты испытываешь тяжёлую степень тревоги")

    await typing_effect(message, 1)
    await message.answer("Я рядом")

    await typing_effect(message)
    await message.answer("Но меня может быть недостаточно")

    await typing_effect(message, 1)
    await message.answer("Мы с тобой попробуем")

    await typing_effect(message, 1)
    await message.answer("Но постарайся не оставаться сегодня наедине")

    await typing_effect(message, 8)
    random_inst = random.choice(instructions_from)
    await message.answer(random_inst)

    await typing_effect(message, 3)
    await message.answer("Если это поможет тебе, будет просто замечательно. Но я всегда тут и готов тебе помочь.", reply_markup=feel_kb)

@dp.message(lambda msg: msg.text == "Нормально")
async def its_hard(message: types.Message):
    await typing_effect(message)
    await message.answer("О, это очень хорошо!")

    await typing_effect(message)
    await message.answer("Я рада за тебя, лови :)")

    await typing_effect(message, 3)
    await message.answer("Совет:\n\nПосмотри мои рекомендации для разных состояний (их ты увидишь на кнопочках ниже)\n\nМеня может не быть рядом в нужный момент")

async def ask_chatgpt(prompt: str) -> str:
    url = "https://api.proxyapi.ru/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Тебя зовут ИСА. Ты — доброжелательный и понимающий виртуальный психолог, который помогает человеку "
                    "в трудные и лёгкие моменты жизни. Ты всегда поддерживаешь, говоришь тёплыми словами "
                    "и предлагаешь **практичные советы**, упражнения для снижения тревожности, осознанности и саморазвития. "
                    "Избегай пустых фраз и давай рекомендации, которые реально можно применить. "
                    "**Отвечай кратко и по делу. Максимум 2-3 предложения. Если требуется совет — дай его в короткой форме.** Используй текстовые смайлики иногда в ответах"
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }


    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    logging.error(f"Ошибка {response.status}: {await response.text()}")
                    return "Прости, я сейчас не могу ответить. Попробуй позже!"
    except Exception as e:
        logging.error(f"Ошибка при обращении к Proxy API: {e}")
        return "Прости, я сейчас не могу ответить. Попробуй позже!"


@dp.message()
async def handle_message(message: types.Message):
    # Если сообщение есть в предопределенных кнопках, не отправляем его в ChatGPT
    predefined_buttons = {
        "Привет", "Рад(а) знакомству", "Хорошо",
        "Немного дискомфортно", "Поток мыслей набирает обороты",
        "Тяжело...", "Нормально"
    }

    if message.text in predefined_buttons:
        return  # Игнорируем, так как это кнопка

    logging.info(f"Пользователь {message.from_user.id}: {message.text}")

    await typing_effect(message)  # Имитация набора текста
    gpt_response = await ask_chatgpt(message.text)  # Запрос к ChatGPT
    await message.answer(gpt_response)  # Отправка ответа пользователю


# @dp.message()
# async def unknown_message(message: types.Message):
#     await typing_effect(message)
#     await message.answer(random.choice(unknown_responses))

# Запуск бота
async def main():
    await load_data()
    await dp.start_polling(bot)

if __name__ == "__main__":
    import sys
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен вручную.")
        sys.exit(0)

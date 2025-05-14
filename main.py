import os
import random
import logging
import telebot
from telebot import types
from db import UserDatabase
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env (если он существует)
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация базы данных пользователей
db = UserDatabase()

# Значения для ставок
BET_AMOUNTS = [10, 50, 100, 500, 1000]
STARTING_BALANCE = 1000

# Инициализация бота
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    logger.error("Токен бота не найден! Убедитесь, что вы создали файл .env с переменной TELEGRAM_BOT_TOKEN.")
    
bot = telebot.TeleBot(TOKEN if TOKEN else "placeholder_for_error_prevention")

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_first_name = message.from_user.first_name
    
    # Если пользователь новый - добавляем в базу данных
    if not db.user_exists(user_id):
        db.add_user(user_id, STARTING_BALANCE)
    
    # Приветственное сообщение
    welcome_message = (
        f"👋 Привет, {user_first_name}!\n\n"
        "🎮 *Добро пожаловать в игру «Орёл и Решка»*\n\n"
        "🔹 *Правила игры:*\n"
        "- Используйте команду /flip, чтобы подбросить монетку\n"
        "- Делайте ставки на «Орла» или «Решку»\n"
        "- Выигрывайте виртуальные баллы\n\n"
        f"💰 Ваш текущий баланс: *{db.get_balance(user_id)}* баллов\n\n"
        "🎯 *Команды:*\n"
        "/flip - подбросить монетку и сделать ставку\n"
        "/balance - проверить баланс\n"
        "/help - показать справку"
    )
    
    bot.send_message(user_id, welcome_message, parse_mode="Markdown")

# Обработчик команды /help
@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = message.from_user.id
    
    help_text = (
        "🎮 *Игра «Орёл и Решка»* - Справка\n\n"
        "🔹 *Основные команды:*\n"
        "/flip - подбросить монетку и сделать ставку\n"
        "/balance - проверить баланс\n"
        "/help - показать эту справку\n\n"
        "🔹 *Как делать ставки:*\n"
        "1. Введите команду /flip\n"
        "2. Выберите сторону монеты (Орёл или Решка)\n"
        "3. Выберите сумму ставки\n"
        "4. Дождитесь результата!\n\n"
        "💰 Если ваша ставка сыграет, вы получите в два раза больше поставленной суммы.\n"
        "❗ Если проиграете - потеряете свою ставку.\n\n"
        "Удачи в игре! 🍀"
    )
    
    bot.send_message(user_id, help_text, parse_mode="Markdown")

# Обработчик команды /balance
@bot.message_handler(commands=['balance'])
def balance(message):
    user_id = message.from_user.id
    
    if not db.user_exists(user_id):
        db.add_user(user_id, STARTING_BALANCE)
    
    balance = db.get_balance(user_id)
    
    bot.send_message(
        user_id,
        f"💰 Ваш текущий баланс: *{balance}* баллов",
        parse_mode="Markdown"
    )

# Обработчик команды /flip
@bot.message_handler(commands=['flip'])
def flip(message):
    user_id = message.from_user.id
    
    if not db.user_exists(user_id):
        db.add_user(user_id, STARTING_BALANCE)
    
    balance = db.get_balance(user_id)
    
    if balance <= 0:
        bot.send_message(
            user_id,
            "❌ У вас закончились баллы! Используйте команду /start, чтобы получить новые баллы."
        )
        db.update_balance(user_id, STARTING_BALANCE)
        return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    button_heads = types.InlineKeyboardButton("🦅 Орёл", callback_data="choice_heads")
    button_tails = types.InlineKeyboardButton("👑 Решка", callback_data="choice_tails")
    markup.add(button_heads, button_tails)
    
    bot.send_message(
        user_id,
        "🔄 *Выберите сторону монеты:*",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# Обработчик всех callback-запросов
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
    if call.data.startswith("choice_"):
        # Обработка выбора стороны монеты
        handle_choice(call)
    elif call.data.startswith("bet_"):
        # Обработка выбора ставки
        handle_bet(call)

# Функция для обработки выбора стороны монеты
def handle_choice(call):
    user_id = call.from_user.id
    user_choice = call.data.split("_")[1]  # heads или tails
    
    # Создаем клавиатуру для выбора суммы ставки
    markup = types.InlineKeyboardMarkup(row_width=3)
    
    balance = db.get_balance(user_id)
    buttons = []
    
    # Добавляем только те ставки, которые пользователь может себе позволить
    for amount in BET_AMOUNTS:
        if amount <= balance:
            buttons.append(types.InlineKeyboardButton(
                f"{amount}", 
                callback_data=f"bet_{user_choice}_{amount}"
            ))
    
    # Если у пользователя мало баллов, предложим все что есть
    if not buttons:
        buttons = [types.InlineKeyboardButton(
            f"{balance}", 
            callback_data=f"bet_{user_choice}_{balance}"
        )]
    
    markup.add(*buttons)
    
    choice_text = "🦅 Орёл" if user_choice == "heads" else "👑 Решка"
    
    bot.edit_message_text(
        chat_id=user_id,
        message_id=call.message.message_id,
        text=f"Вы выбрали: *{choice_text}*\n\n💰 Выберите сумму ставки:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# Функция для обработки выбора ставки и подбрасывания монетки
def handle_bet(call):
    user_id = call.from_user.id
    data_parts = call.data.split("_")
    user_choice = data_parts[1]  # heads или tails
    bet_amount = int(data_parts[2])
    
    # Проверяем баланс пользователя
    balance = db.get_balance(user_id)
    
    if bet_amount > balance:
        bot.edit_message_text(
            chat_id=user_id,
            message_id=call.message.message_id,
            text="❌ У вас недостаточно баллов для этой ставки!"
        )
        return
    
    # Подбрасываем монетку
    result = random.choice(["heads", "tails"])
    result_text = "🦅 Орёл" if result == "heads" else "👑 Решка"
    choice_text = "🦅 Орёл" if user_choice == "heads" else "👑 Решка"
    
    # Определяем выигрыш или проигрыш
    if result == user_choice:
        # Выигрыш
        win_amount = bet_amount
        new_balance = balance + win_amount
        db.update_balance(user_id, new_balance)
        
        bot.edit_message_text(
            chat_id=user_id,
            message_id=call.message.message_id,
            text=(
                f"🎲 *Результат:* {result_text}\n\n"
                f"🎯 Ваш выбор: {choice_text}\n"
                f"💰 Ставка: {bet_amount}\n\n"
                f"🎉 *Поздравляем! Вы выиграли {win_amount} баллов!*\n\n"
                f"💰 Ваш новый баланс: *{new_balance}* баллов\n\n"
                f"Сыграть ещё раз? Введите /flip"
            ),
            parse_mode="Markdown"
        )
    else:
        # Проигрыш
        new_balance = balance - bet_amount
        db.update_balance(user_id, new_balance)
        
        bot.edit_message_text(
            chat_id=user_id,
            message_id=call.message.message_id,
            text=(
                f"🎲 *Результат:* {result_text}\n\n"
                f"🎯 Ваш выбор: {choice_text}\n"
                f"💰 Ставка: {bet_amount}\n\n"
                f"😔 *Увы, вы проиграли {bet_amount} баллов*\n\n"
                f"💰 Ваш новый баланс: *{new_balance}* баллов\n\n"
                f"Попробуйте еще раз! Введите /flip"
            ),
            parse_mode="Markdown"
        )

# Обработчик неизвестных команд и сообщений
@bot.message_handler(func=lambda message: True)
def unknown(message):
    bot.reply_to(
        message,
        "🤔 Не понимаю эту команду. Используйте /help для получения списка доступных команд."
    )

def main() -> None:
    # Проверяем наличие токена
    if not TOKEN:
        logger.error("Токен бота не найден! Убедитесь, что вы установили переменную окружения TELEGRAM_BOT_TOKEN.")
        return
    
    # Запускаем бота
    logger.info("Бот запущен!")
    bot.infinity_polling()

if __name__ == "__main__":
    main()

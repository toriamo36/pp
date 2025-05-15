# Отчет по созданию телеграм-бота "Орёл и Решка"
## Исследование предметной области
1. Изучение Telegram Bot API

Telegram Bot API предоставляет интерфейс для программного взаимодействия с платформой Telegram. Боты могут обрабатывать сообщения, команды и отвечать пользователям, выполняя различные функции.

 2. Выбор инструментов разработки
 
После изучения вариантов был выбран стек технологий:
	- Язык программирования: Python 3.11
	- Библиотека для работы с Telegram API: pyTelegramBotAPI (telebot)
	- Управление конфигурацией: python-dotenv
	- Хранение данных: In-memory хранилище (для MVP)

3. Планирование функциональности
 
Был определен следующий набор функций:
	- Подбрасывание виртуальной монетки
	- Система ставок с виртуальными баллами
	- Отслеживание баланса пользователей
	- Начисление/списание баллов за правильные/неправильные ставки
## Техническое руководство по созданию Telegram-бота "Орёл и Решка"
### Шаг 1: Подготовка среды разработки
1. Создание виртуального окружения
```python
blockquotepython3 -m venv venv
```
2. Активация виртуального окружения
```python
Для Windows: venv\Scripts\activate
Для macOS/Linux: source venv/bin/activate
```
3. Установка необходимых библиотек
```python
pip install pyTelegramBotAPI python-dotenv
```
### Шаг 2: Получение токена для Telegram-бота
> Откройте Telegram и найдите бота @BotFather
Отправьте команду /newbot
Следуйте инструкциям BotFather:
Укажите отображаемое имя бота (например, "Орёл и Решка")
Укажите уникальное имя пользователя (например, "orel_reshka_bot")
BotFather вернет токен вида 123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
Сохраните этот токен в файле .env:
TELEGRAM_BOT_TOKEN=ваш_токен_здесь

### Шаг 3: Создание базового модуля для хранения данных
Создайте файл db.py для управления данными пользователей:

	class UserDatabase:
      """
      Класс для управления данными пользователей.
      В текущей реализации данные хранятся в памяти (для MVP).
      """

      def __init__(self):
          """
          Инициализирует пустую базу данных пользователей.
          """
          # Словарь для хранения данных о пользователях
          # user_id: { balance: int }
          self.users = {}

      def user_exists(self, user_id):
          """
          Проверяет, существует ли пользователь в базе данных.

          Args:
              user_id: Уникальный идентификатор пользователя

          Returns:
              bool: True, если пользователь существует, иначе False
          """
          return user_id in self.users

      def add_user(self, user_id, initial_balance=1000):
          """
          Добавляет нового пользователя в базу данных.

          Args:
              user_id: Уникальный идентификатор пользователя
              initial_balance: Начальный баланс пользователя (по умолчанию 1000)
          """
          if not self.user_exists(user_id):
              self.users[user_id] = {
                  "balance": initial_balance
              }

      def get_balance(self, user_id):
          """
          Получает текущий баланс пользователя.

          Args:
              user_id: Уникальный идентификатор пользователя

          Returns:
              int: Текущий баланс пользователя или 0, если пользователь не найден
          """
          if self.user_exists(user_id):
              return self.users[user_id]["balance"]
          return 0

      def update_balance(self, user_id, new_balance):
          """
          Обновляет баланс пользователя.

          Args:
              user_id: Уникальный идентификатор пользователя
              new_balance: Новое значение баланса

          Returns:
              bool: True, если обновление выполнено успешно, иначе False
          """
          if self.user_exists(user_id):
              self.users[user_id]["balance"] = new_balance
              return True
          return False

      def add_to_balance(self, user_id, amount):
          """
          Добавляет указанную сумму к балансу пользователя.

          Args:
              user_id: Уникальный идентификатор пользователя
              amount: Сумма для добавления (может быть отрицательной)

          Returns:
              int: Новый баланс пользователя или None, если пользователь не найден
          """
          if self.user_exists(user_id):
              self.users[user_id]["balance"] += amount
              return self.users[user_id]["balance"]
          return None
### Шаг 4: Создание основного файла бота
1. Создайте файл main.py с основной логикой бота:
```python
  import os
  import random
  import logging
  import telebot
  from telebot import types
  from db import UserDatabase
  from dotenv import load_dotenv
```
2. Загрузка переменных окружения из файла .env (если он существует)
```python
load_dotenv()
```
3. Настройка логирования
```python
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
```
4. Инициализация базы данных пользователей
```python
db = UserDatabase()
```
5. Значения для ставок
```python
BET_AMOUNTS = [10, 50, 100, 500, 1000]
STARTING_BALANCE = 1000
```
6. Инициализация бота
```python
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    logger.error("Токен бота не найден! Убедитесь, что вы создали файл .env с переменной TELEGRAM_BOT_TOKEN.")
    
> blockquotebot = telebot.TeleBot(TOKEN if TOKEN else "placeholder_for_error_prevention")
```
7. Обработчик команды /start
```python
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
```
### Шаг 5: Создание примера конфигурационного файла
Создайте файл .env.example с примером настроек:
```python
# Пример файла .env
# Скопируйте этот файл в .env и заполните значения
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```
### Шаг 6: Запуск бота
```python
# Убедитесь, что виртуальное окружение активировано
# и файл .env содержит правильный токен
python main.py
```
## Объяснение работы бота
### Обработка команд
В боте реализованы следующие обработчики команд:
```python
/start - инициализирует пользователя, показывает приветствие и инструкции
/help - отображает справочную информацию
/balance - показывает текущий баланс пользователя
/flip - начинает игру, предлагая выбрать сторону монеты
```
### Процесс игры
> Пользователь вызывает команду /flip
Бот предлагает выбрать сторону монеты (Орёл или Решка)
После выбора стороны, бот предлагает выбрать сумму ставки
Бот "подбрасывает" монетку (делает случайный выбор)
Если прогноз пользователя совпал с результатом:
Пользователь получает выигрыш (100% от ставки)
Баланс увеличивается на сумму выигрыша
Если прогноз не совпал:
Пользователь теряет свою ставку
Баланс уменьшается на сумму ставки
Бот сообщает результат и предлагает сыграть еще раз

### Хранение данных
Данные пользователей (ID и баланс) хранятся в памяти программы в формате словаря:
```python
{
  user_id_1: {"balance": 1000},
  user_id_2: {"balance": 750},
  ...
}
```
Это простой подход для MVP. Для продакшн-версии рекомендуется использовать постоянное хранилище данных (SQLite, PostgreSQL и т.д.).

## Возможные улучшения
### Улучшение хранения данных
Реализовать постоянное хранение данных с использованием базы данных (SQLite, PostgreSQL) для сохранения информации между перезапусками бота.

### Дополнительные функции
Система статистики игр для каждого пользователя
Рейтинг игроков по балансу
Дополнительные игры на основе случайности (кости, рулетка и т.д.)
Система достижений и наград
### Улучшение пользовательского интерфейса
Добавление разнообразных анимаций при подбрасывании монеты
Более красочные и информативные сообщения
Ежедневные бонусы для активных игроков
## Выводы
В рамках проекта был успешно создан интерактивный телеграм-бот "Орёл и Решка", который позволяет пользователям подбрасывать виртуальную монетку и делать ставки на результат. Бот имеет простой и понятный интерфейс, основные игровые механики, систему балансов и обработку различных сценариев взаимодействия.

Созданное решение демонстрирует базовые возможности Telegram Bot API и библиотеки pyTelegramBotAPI, а также показывает, как можно организовать простую игровую логику. Проект может быть использован как основа для более сложных игровых ботов или как учебный пример для изучения разработки телеграм-ботов.
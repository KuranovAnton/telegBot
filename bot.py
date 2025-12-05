import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    ContextTypes
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    print("ОШИБКА: Токен не найден! Установите BOT_TOKEN в переменных окружения")
    exit(1)

# Данные с ссылками
LINKS_DATA = {
    'main': {
        'text': '🏠 *Основные ссылки:*',
        'links': [
            {'name': '📚 Документация', 'url': 'https://docs.example.com'},
            {'name': '🌐 Официальный сайт', 'url': 'https://example.com'},
            {'name': '💬 Техподдержка', 'url': 'https://t.me/support_chat'},
        ]
    },
    'social': {
        'text': '📱 *Социальные сети:*',
        'links': [
            {'name': '📺 YouTube', 'url': 'https://youtube.com/example'},
            {'name': '📷 Instagram', 'url': 'https://instagram.com/example'},
            {'name': '🐦 Twitter/X', 'url': 'https://twitter.com/example'},
            {'name': '💼 LinkedIn', 'url': 'https://linkedin.com/company/example'},
        ]
    },
    'resources': {
        'text': '🛠 *Ресурсы:*',
        'links': [
            {'name': '🐙 GitHub', 'url': 'https://github.com/example'},
            {'name': '📦 API Документация', 'url': 'https://api.example.com'},
            {'name': '📄 Блог', 'url': 'https://blog.example.com'},
        ]
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    logger.info(f"Пользователь {user.id} начал диалог")
    
    # Приветственное сообщение
    welcome_text = (
        f"👋 Привет, {user.first_name}!\n\n"
        "Я бот для быстрого доступа к полезным ссылкам. "
        "Выбери категорию ниже:"
    )
    
    # Создаем клавиатуру с кнопками
    keyboard = [
        [
            InlineKeyboardButton("🏠 Основные ссылки", callback_data='category_main'),
            InlineKeyboardButton("📱 Социальные сети", callback_data='category_social')
        ],
        [
            InlineKeyboardButton("🛠 Ресурсы", callback_data='category_resources'),
            InlineKeyboardButton("📋 Все ссылки", callback_data='category_all')
        ],
        [
            InlineKeyboardButton("ℹ️ Помощь", callback_data='help'),
            InlineKeyboardButton("🔗 Поделиться ботом", callback_data='share')
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()  # Убираем "часики" у кнопки
    
    if query.data.startswith('category_'):
        category = query.data.replace('category_', '')
        
        if category == 'all':
            # Отправляем все ссылки
            message = "🔗 *Все доступные ссылки:*\n\n"
            for cat_key, cat_data in LINKS_DATA.items():
                message += f"{cat_data['text']}\n"
                for link in cat_data['links']:
                    message += f"• [{link['name']}]({link['url'].replace('_', r'\_')})\n"
                message += "\n"
            
            keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data='back_to_menu')]]
            
        elif category in LINKS_DATA:
            # Отправляем ссылки конкретной категории
            cat_data = LINKS_DATA[category]
            message = f"{cat_data['text']}\n\n"
            
            for link in cat_data['links']:
                message += f"• [{link['name']}]({link['url'].replace('_', r'\_')})\n"
            
            # Кнопки для этой категории
            keyboard = [
                [InlineKeyboardButton("🌐 Открыть все ссылки", callback_data=f'open_all_{category}')],
                [InlineKeyboardButton("⬅️ Назад", callback_data='back_to_menu')]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    
    elif query.data.startswith('open_all_'):
        # Открываем все ссылки категории отдельными сообщениями
        category = query.data.replace('open_all_', '')
        cat_data = LINKS_DATA[category]
        
        # Сначала редактируем текущее сообщение
        await query.edit_message_text(
            text=f"📤 Открываю ссылки категории...",
            parse_mode='Markdown'
        )
        
        # Затем отправляем ссылки по отдельности
        for link in cat_data['links']:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"[{link['name']}]({link['url']})",
                parse_mode='Markdown'
            )
        
        # Возвращаем меню
        keyboard = [[InlineKeyboardButton("⬅️ Назад в меню", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Все ссылки отправлены! Что дальше?",
            reply_markup=reply_markup
        )
    
    elif query.data == 'back_to_menu':
        # Возвращаемся в главное меню
        user = query.from_user
        if user.username:
            user_display = f"@{user.username}"
        elif user.first_name:
            user_display = user.first_name
        else:
            user_display = f"пользователь {user.id}"
        
        welcome_text = (
            f"👋 Снова привет, {user_display}!\n"
            f"🆔 ID: {user.id}\n\n"
            "Выбери категорию:"
        )
        welcome_text = f"👋 Снова привет, {user.first_name}!\nВыбери категорию:"
        
        keyboard = [
            [
                InlineKeyboardButton("🏠 Основные ссылки", callback_data='category_main'),
                InlineKeyboardButton("📱 Социальные сети", callback_data='category_social')
            ],
            [
                InlineKeyboardButton("🛠 Ресурсы", callback_data='category_resources'),
                InlineKeyboardButton("📋 Все ссылки", callback_data='category_all')
            ],
            [
                InlineKeyboardButton("ℹ️ Помощь", callback_data='help'),
                InlineKeyboardButton("🔗 Поделиться ботом", callback_data='share')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=welcome_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    elif query.data == 'help':
        help_text = (
            "❓ *Помощь по использованию бота:*\n\n"
            "1. Выберите категорию ссылок\n"
            "2. Нажмите на кнопку с нужной категорией\n"
            "3. Получите список ссылок\n"
            "4. Используйте кнопку 'Открыть все ссылки' для быстрого доступа\n\n"
            "*Команды:*\n"
            "/start - Перезапустить бота\n"
            "/links - Получить все ссылки сразу\n"
            "/help - Показать это сообщение\n"
            "/share - Получить ссылку для приглашения друзей"
        )
        
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=help_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif query.data == 'share':
        bot_username = context.bot.username
        share_text = (
            "🔗 *Пригласите друзей!*\n\n"
            f"*Ссылка на бота:* https://t.me/{bot_username}\n\n"
            "Просто отправьте эту ссылку друзьям!"
        )
        
        keyboard = [
            [InlineKeyboardButton("📲 Поделиться ссылкой", 
                                 url=f"https://t.me/share/url?url=https://t.me/{bot_username}&text=Классный бот с полезными ссылками!")],
            [InlineKeyboardButton("⬅️ Назад", callback_data='back_to_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=share_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def links_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /links для получения всех ссылок сразу"""
    message = "🔗 *Все доступные ссылки:*\n\n"
    
    for cat_key, cat_data in LINKS_DATA.items():
        message += f"{cat_data['text']}\n"
        for link in cat_data['links']:
            message += f"• [{link['name']}]({link['url'].replace('_', r'\_')})\n"
        message += "\n"
    
    keyboard = [[InlineKeyboardButton("🎛 Открыть меню", callback_data='back_to_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    help_text = (
        "🤖 *Бот для полезных ссылок*\n\n"
        "*Доступные команды:*\n"
        "/start - Запустить бота и открыть меню\n"
        "/links - Получить все ссылки сразу\n"
        "/help - Показать справку\n"
        "/share - Получить ссылку для приглашения\n\n"
        "Просто нажмите /start для начала работы!"
    )
    
    await update.message.reply_text(
        text=help_text,
        parse_mode='Markdown'
    )

async def share_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /share для получения ссылки на бота"""
    bot_username = context.bot.username
    share_message = (
        f"Приглашайте друзей в бота! 🚀\n\n"
        f"🔗 Ссылка: https://t.me/{bot_username}\n\n"
        "Просто отправьте эту ссылку или нажмите кнопку ниже для быстрого распространения:"
    )
    
    keyboard = [[
        InlineKeyboardButton("📲 Поделиться в Telegram", 
                           url=f"https://t.me/share/url?url=https://t.me/{bot_username}&text=Отличный бот с полезными ссылками!")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text=share_message,
        reply_markup=reply_markup
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "😕 Произошла ошибка. Попробуйте еще раз или используйте /start"
        )

def main():
    """Основная функция запуска бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("links", links_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("share", share_command))
    
    # Добавляем обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    logger.info("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
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
    'social': {
        'text': '📱 *Наши социальные сети:*',
        'links': [
            {'name': '🌐 ВКонтакте', 'url': 'https://vk.com/hotspareparts'},
            {'name': '📢 Telegram канал', 'url': 'https://t.me/+St3ks8NOuZI4NTRi'},
        ]
    },
    'contacts': {
        'text': '📞 *Контакты для связи:*\n\n*Телефоны:*',
        'links': [
            {'name': '📱 +7 (XXX) XXX-XX-XX', 'url': 'tel:+7XXXXXXXXXX'},  # ВАШ ПЕРВЫЙ НОМЕР
            {'name': '🌐 Профиль ВКонтакте', 'url': 'https://vk.com/offiser'},  # ВАШ ПРОФИЛЬ ВК
            {'name': '📱 +7 (901) 140-87-60', 'url': 'tel:+79011408760'},  # ВАШ ВТОРОЙ НОМЕР
            {'name': '🌐 Профиль ВКонтакте', 'url': 'https://vk.com/offiser'},  # ВАШ ПРОФИЛЬ ВК
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
        "Я бот для связи с нами. "
        "Выбери нужный раздел ниже:"
    )
    
    # Создаем клавиатуру с кнопками
    keyboard = [
        [
            InlineKeyboardButton("📱 Наши соц. сети", callback_data='category_social'),
            InlineKeyboardButton("📞 Контакты", callback_data='category_contacts')
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
                    message += f"• [{link['name']}]({link['url']})\n"
                message += "\n"
            
            keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data='back_to_menu')]]
            
        elif category in LINKS_DATA:
            # Отправляем ссылки конкретной категории
            cat_data = LINKS_DATA[category]
            message = f"{cat_data['text']}\n\n"
            
            for link in cat_data['links']:
                message += f"• [{link['name']}]({link['url']})\n"
            
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
            text=f"📤 Открываю ссылки...",
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
        welcome_text = f"👋 Снова привет, {user.first_name}!\nВыбери раздел:"
        
        keyboard = [
            [
                InlineKeyboardButton("📱 Наши соц. сети", callback_data='category_social'),
                InlineKeyboardButton("📞 Контакты", callback_data='category_contacts')
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
            "*Основные разделы:*\n"
            "• *Наши соц. сети* - ссылки на наши сообщества\n"
            "• *Контакты* - телефоны и профили для связи\n\n"
            "*Команды:*\n"
            "/start - Перезапустить бота\n"
            "/contacts - Получить контактную информацию\n"
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
                                 url=f"https://t.me/share/url?url=https://t.me/{bot_username}&text=Бот для связи с нами!")],
            [InlineKeyboardButton("⬅️ Назад", callback_data='back_to_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=share_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def contacts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /contacts для получения контактной информации"""
    message = LINKS_DATA['contacts']['text'] + "\n\n"
    
    for link in LINKS_DATA['contacts']['links']:
        message += f"• [{link['name']}]({link['url']})\n"
    
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
        "🤖 *Бот для связи с нами*\n\n"
        "*Доступные команды:*\n"
        "/start - Запустить бота и открыть меню\n"
        "/contacts - Получить контактную информацию\n"
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
                           url=f"https://t.me/share/url?url=https://t.me/{bot_username}&text=Бот для связи с нами!")
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
    application.add_handler(CommandHandler("contacts", contacts_command))
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
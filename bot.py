import logging
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler
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
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')  # Ваш ID для получения уведомлений о заказах

if not BOT_TOKEN:
    print("ОШИБКА: Токен не найден! Установите BOT_TOKEN в переменных окружения")
    exit(1)

# Константы для ConversationHandler
FULL_NAME, PHONE, PRODUCT = range(3)

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
        'text': '📞 *Контакт для связи:*\n\n*Телефоны:*',
        'links': [
            {'name': '📱 +7 (901) 140-87-60', 'url': 'tel:+79011408760'},
            {'name': '🌐 Данил', 'url': 'https://vk.com/offiser'},
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
        "Я бот для связи с нами и оформления заказов. "
        "Выбери нужный раздел ниже:"
    )
    
    # Создаем клавиатуру с кнопками
    keyboard = [
        [
            InlineKeyboardButton("📱 Наши соц. сети", callback_data='category_social'),
            InlineKeyboardButton("📞 Контакты", callback_data='category_contacts')
        ],
        [
            InlineKeyboardButton("🛒 Оформить заказ", callback_data='new_order')
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
        
        if category in LINKS_DATA:
            # Отправляем ссылки конкретной категории
            cat_data = LINKS_DATA[category]
            message = f"{cat_data['text']}\n\n"
            
            for link in cat_data['links']:
                message += f"• [{link['name']}]({link['url']})\n"
            
            # Кнопка для возврата в меню
            keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data='back_to_menu')]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode='Markdown',
            disable_web_page_preview=True
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
                InlineKeyboardButton("🛒 Оформить заказ", callback_data='new_order')
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
    
    elif query.data == 'new_order':
        # Начинаем оформление заказа
        await query.edit_message_text(
            text="🛒 *Оформление заказа*\n\n"
                 "Для оформления заказа мне нужна следующая информация:\n\n"
                 "1. Ваше ФИО (полностью)\n"
                 "2. Номер телефона для связи\n"
                 "3. Товар, который вы хотите заказать\n\n"
                 "Давайте начнем! Введите ваше ФИО:",
            parse_mode='Markdown'
        )
        
        # Устанавливаем состояние разговора
        return FULL_NAME
    
    elif query.data == 'help':
        help_text = (
            "❓ *Помощь по использованию бота:*\n\n"
            "*Основные разделы:*\n"
            "• *Наши соц. сети* - ссылки на наши сообщества\n"
            "• *Контакты* - телефоны и профили для связи\n"
            "• *Оформить заказ* - создать новый заказ\n\n"
            "*Команды:*\n"
            "/start - Перезапустить бота\n"
            "/contacts - Получить контактную информацию\n"
            "/help - Показать это сообщение\n"
            "/share - Получить ссылку для приглашения друзей\n"
            "/order - Оформить новый заказ"
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
                                 url=f"https://t.me/share/url?url=https://t.me/{bot_username}&text=Бот для оформления заказов!")],
            [InlineKeyboardButton("⬅️ Назад", callback_data='back_to_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=share_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало оформления заказа через команду /order"""
    await update.message.reply_text(
        "🛒 *Оформление заказа*\n\n"
        "Для оформления заказа мне нужна следующая информация:\n\n"
        "1. Ваше ФИО (полностью)\n"
        "2. Номер телефона для связи\n"
        "3. Товар, который вы хотите заказать\n\n"
        "Давайте начнем! Введите ваше ФИО:",
        parse_mode='Markdown'
    )
    
    return FULL_NAME

async def get_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение ФИО от пользователя"""
    context.user_data['full_name'] = update.message.text
    await update.message.reply_text(
        "✅ ФИО получено!\n\n"
        "Теперь введите ваш номер телефона (в любом формате):"
    )
    
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение номера телефона от пользователя"""
    context.user_data['phone'] = update.message.text
    await update.message.reply_text(
        "✅ Номер телефона получен!\n\n"
        "Теперь опишите товар, который вы хотите заказать:\n"
        "(можно указать название, артикул, количество и другие детали)"
    )
    
    return PRODUCT

async def get_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение информации о товаре и завершение оформления заказа"""
    context.user_data['product'] = update.message.text
    user_data = context.user_data
    
    # Генерируем номер заказа
    order_number = random.randint(10000, 99999)
    
    # Отправляем подтверждение пользователю
    await update.message.reply_text(
        f"✅ *Спасибо! Заказ успешно оформлен.*\n\n"
        f"*Номер вашего заказа:* {order_number}\n"
        f"*Ваше ФИО:* {user_data['full_name']}\n"
        f"*Телефон:* {user_data['phone']}\n"
        f"*Товар:* {user_data['product']}\n\n"
        f"📞 В ближайшее время с вами свяжется наш менеджер для подтверждения заказа!",
        parse_mode='Markdown'
    )
    
    # Отправляем уведомление администратору
    if ADMIN_CHAT_ID:
        try:
            admin_message = (
                f"🚨 *ПОСТУПИЛ НОВЫЙ ЗАКАЗ*\n\n"
                f"*НОМЕР ЗАКАЗА:* {order_number}\n"
                f"*Покупатель:* {user_data['full_name']}\n"
                f"*Телефон:* {user_data['phone']}\n"
                f"*Товар:* {user_data['product']}\n\n"
                f"*Дата:* {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
                f"*ID пользователя:* {update.effective_user.id}\n"
                f"*Username:* @{update.effective_user.username if update.effective_user.username else 'не указан'}"
            )
            
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=admin_message,
                parse_mode='Markdown'
            )
            logger.info(f"Заказ #{order_number} отправлен администратору")
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления администратору: {e}")
    
    # Очищаем данные пользователя
    context.user_data.clear()
    
    # Показываем кнопку возврата в меню
    keyboard = [[InlineKeyboardButton("🏠 Вернуться в меню", callback_data='back_to_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Что бы вы хотели сделать дальше?",
        reply_markup=reply_markup
    )
    
    return ConversationHandler.END

async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена оформления заказа"""
    await update.message.reply_text(
        "❌ Оформление заказа отменено.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Вернуться в меню", callback_data='back_to_menu')]])
    )
    
    context.user_data.clear()
    return ConversationHandler.END

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
        "🤖 *Бот для оформления заказов*\n\n"
        "*Доступные команды:*\n"
        "/start - Запустить бота и открыть меню\n"
        "/order - Оформить новый заказ\n"
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
                           url=f"https://t.me/share/url?url=https://t.me/{bot_username}&text=Бот для оформления заказов!")
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
    
    # Создаем ConversationHandler для оформления заказа
    order_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('order', start_order),
            CallbackQueryHandler(start_order, pattern='^new_order$')
        ],
        states={
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_full_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_product)],
        },
        fallbacks=[CommandHandler('cancel', cancel_order)],
    )
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("contacts", contacts_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("share", share_command))
    
    # Добавляем ConversationHandler
    application.add_handler(order_conv_handler)
    
    # Добавляем обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    logger.info("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
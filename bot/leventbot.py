from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ChatMemberHandler, MessageHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
import json
import random
from datetime import datetime

TOKEN = "7639282714:AAGSd5y4-J7gDSIFuunO5eWu4BBdYNyG5EI"

# Soruları JSON dosyasından yükle
def load_questions():
    try:
        with open('questions.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print("questions.json dosyası bulunamadı!")
        return {}

QUESTIONS_DB = load_questions()

# Kullanıcıların gördüğü soruları takip etmek için
user_used_questions = {}

# Kullanıcıların yarışma durumunu kalıcı olarak takip etmek için
user_quiz_status = {}  # Kullanıcının yarışma geçmişini saklar

def get_random_question(user_id):
    # Kullanıcının daha önce gördüğü soruları al
    if user_id not in user_used_questions:
        user_used_questions[user_id] = set()
    
    # Tüm kategorileri al
    categories = list(QUESTIONS_DB.keys())
    
    # Kullanıcının görmediği soruları bul
    available_questions = []
    for category in categories:
        for question in QUESTIONS_DB[category]:
            question_key = f"{category}_{question['soru']}"
            if question_key not in user_used_questions[user_id]:
                available_questions.append((category, question))
    
    # Eğer kullanıcı tüm soruları görmüşse, soru havuzunu sıfırla
    if not available_questions:
        user_used_questions[user_id].clear()
        for category in categories:
            for question in QUESTIONS_DB[category]:
                available_questions.append((category, question))
    
    # Rastgele bir soru seç
    category, question = random.choice(available_questions)
    
    # Seçilen soruyu kullanıcının gördüğü sorular listesine ekle
    question_key = f"{category}_{question['soru']}"
    user_used_questions[user_id].add(question_key)
    
    return question["soru"], question["secenekler"], question["dogru_cevap"]

user_states = {}

async def start(update, context):
    user_id = update.effective_user.id
    
    # Eğer kullanıcı daha önce yarışmışsa, engelle
    if user_id in user_quiz_status and user_quiz_status[user_id]["has_played"]:
        await update.message.reply_text(
            "🚫 *Yarışma Hakkınız Doldu!*\n\n"
            "Bu yarışmaya daha önce katıldınız. Her kullanıcı sadece 1 kez yarışabilir.\n\n"
            f"Yarışma sonucunuz: {user_quiz_status[user_id]['final_score']} puan\n"
            f"Yarışma tarihi: {user_quiz_status[user_id]['completion_date']}\n\n"
            "Yeni yarışmalar için grubu takip etmeye devam edin! 🎉",
            parse_mode='Markdown'
        )
        return
    
    # Eğer kullanıcı zaten yarışmada ise, uyarı ver
    if user_id in user_states and user_states[user_id]["is_playing"]:
        await update.message.reply_text(
            "⚠️ *Yarışma Devam Ediyor!*\n\n"
            "Şu anda aktif bir yarışmanız var. Mevcut yarışmanızı bitirmeniz gerekiyor.\n\n"
            "Yarışmayı bitirmek için '🏃 Yarışmayı Bitir' butonunu kullanın.",
            parse_mode='Markdown'
        )
        return
    
    # Eğer kullanıcı cüzdan adresi bekliyorsa, uyarı ver
    if user_id in user_states and user_states[user_id]["waiting_for_wallet"]:
        await update.message.reply_text(
            "💰 *Cüzdan Adresi Bekleniyor!*\n\n"
            "Ödülünüzü alabilmek için Telegram cüzdan adresinizi göndermeniz gerekiyor.",
            parse_mode='Markdown'
        )
        return
    
    # Yeni yarışma başlat
    user_states[user_id] = {"current_question": 0, "is_playing": True, "score": 0, "waiting_for_wallet": False}
    
    welcome_message = (
        "🎮 *Bilgi Yarışmasına Hoş Geldin!* 🎮\n\n"
        "Bu yarışmada seni 10 farklı soru bekliyor. Sorular genel kültür alanında ve kolaydan zora doğru ilerliyor.\n\n"
        "📝 *Yarışma Kuralları:*\n"
        "• Her soru için 25 saniye süren var ⏰\n"
        "• Her doğru cevap 10 puan değerinde 🏆\n"
        "• Yanlış cevap verirsen yarışma sona erer ❌\n"
        "• Süre dolduğunda yarışma sona erer ⏰\n"
        "• Tüm soruları doğru cevaplarsan büyük ödülü kazanırsın! 🎉\n"
        "• **Her kullanıcı sadece 1 kez yarışabilir!** ⚠️\n\n"
        "🎯 *Ödüller:*\n"
        "• Her doğru cevap: 10 puan\n"
        "• Tüm soruları doğru cevaplama: Büyük ödül + 100 puan\n"
        "• Ayrıca İstediğin zaman yarışmadan ayrılabilirsin! \n\n"
        "Hazırsan yarışmaya başlayalım! 🚀"
    )
    
    keyboard = [
        [InlineKeyboardButton("Yarışmaya Başla! 🎯", callback_data='start_quiz')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')

async def new_member(update, context):
    # Yeni üye gruba katıldığında
    for member in update.message.new_chat_members:
        if not member.is_bot:  # Bot değilse
            user_id = member.id
            user_states[user_id] = {"current_question": 0, "is_playing": True, "score": 0, "waiting_for_wallet": False}
            
            welcome_message = (
                f"🎮 *{member.first_name} Bilgi Yarışmasına Hoş Geldin!* 🎮\n\n"
                "Bu yarışmada seni 10 farklı soru bekliyor. Sorular genel kültür alanında ve kolaydan zora doğru ilerliyor.\n\n"
                "📝 *Yarışma Kuralları:*\n"
                "• Her soru için 25 saniye süren var ⏰\n"
                "• Her doğru cevap 10 puan değerinde 🏆\n"
                "• Yanlış cevap verirsen yarışma sona erer ❌\n"
                "• Süre dolduğunda yarışma sona erer ⏰\n"
                "• Tüm soruları doğru cevaplarsan büyük ödülü kazanırsın! 🎉\n"
                "• **Her kullanıcı sadece 1 kez yarışabilir!** ⚠️\n\n"
                "🎯 *Ödüller:*\n"
                "• Her doğru cevap: 10 puan\n"
                "• Tüm soruları doğru cevaplama: Büyük ödül + 100 puan\n"
                "• Ayrıca İstediğin zaman yarışmadan ayrılabilirsin! \n\n"
                "Hazırsan yarışmaya başlayalım! 🚀"
            )
            
            keyboard = [
                [InlineKeyboardButton("Yarışmaya Başla! 🎯", callback_data='start_quiz')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')

async def timer_task(update, context, user_id, question_number):
    await asyncio.sleep(15)
    if user_id in user_states and user_states[user_id]["is_playing"] and user_states[user_id]["current_question"] == question_number:
        user_states[user_id]["is_playing"] = False
        score = user_states[user_id]["score"]
        
        # Kullanıcının yarışma durumunu kalıcı olarak kaydet
        user_quiz_status[user_id] = {
            "has_played": True,
            "final_score": score,
            "completion_date": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "result": "süre_doldu"
        }
        
        await update.callback_query.message.reply_text(
            f"Malesef yarışma sona erdi ⏰\n"
            f"Kazandığın puan: {score}\n\n"
            "🚫 Bu yarışmaya tekrar katılamazsınız. Her kullanıcı sadece 1 kez yarışabilir."
        )
        
        # Kullanıcının aktif durumunu sıfırla
        if user_id in user_states:
            del user_states[user_id]

async def ask_question(update, context, user_id):
    if user_id not in user_states or not user_states[user_id]["is_playing"]:
        return

    current_q = user_states[user_id]["current_question"]
    if current_q >= 10:  # 10 soru limiti
        score = user_states[user_id]["score"]
        user_states[user_id]["waiting_for_wallet"] = True
        await update.callback_query.message.reply_text(
            f"Tebrikler! Tüm soruları doğru cevaplayarak büyük ödülü kazandın!! 🎉\n"
            f"Toplam puanın: {score}\n\n"
            "Ödülünü alabilmen için Telegram cüzdan adresini gönder:"
        )
        return

    question, options, correct_answer = get_random_question(user_id)
    # Doğru cevabı kullanıcının durumuna kaydet
    user_states[user_id]["current_correct_answer"] = correct_answer
    
    keyboard = []
    for i, option in enumerate(options):
        keyboard.append([InlineKeyboardButton(option, callback_data=f'answer_{i}')])
    
    # Yarışmayı bitir butonu ekle
    keyboard.append([InlineKeyboardButton("🏃 Yarışmayı Bitir", callback_data='quit_quiz')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text(
        f"Soru {current_q + 1}/10:\n\n{question}",
        reply_markup=reply_markup
    )
    
    # Her soru için yeni bir zamanlayıcı başlat
    asyncio.create_task(timer_task(update, context, user_id, current_q))

async def handle_wallet_address(update, context):
    user_id = update.effective_user.id
    
    # Eğer kullanıcı cüzdan adresi bekliyorsa, mesajı kabul et
    if user_id in user_states and user_states[user_id]["waiting_for_wallet"]:
        wallet_address = update.message.text
        user_states[user_id]["waiting_for_wallet"] = False
        
        # Kullanıcının yarışma durumunu kalıcı olarak kaydet (büyük ödül kazandı)
        score = user_states[user_id]["score"]
        user_quiz_status[user_id] = {
            "has_played": True,
            "final_score": score,
            "completion_date": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "result": "büyük_ödül_kazandı",
            "wallet_address": wallet_address
        }
        
        await update.message.reply_text(
            f"Telegram cüzdan adresin kaydedildi: {wallet_address}\n"
            "Ödülün en kısa sürede hesabına gönderilecek! 🎁\n\n"
            "🚫 Bu yarışmaya tekrar katılamazsınız. Her kullanıcı sadece 1 kez yarışabilir."
        )
        
        # Kullanıcının aktif durumunu sıfırla
        if user_id in user_states:
            del user_states[user_id]
        return
    
    # Eğer kullanıcı yarışmada ise, mesajı görmezden gel ve uyarı ver
    if user_id in user_states and user_states[user_id]["is_playing"]:
        await update.message.reply_text(
            "⚠️ *Yarışma Devam Ediyor!*\n\n"
            "Şu anda aktif bir yarışmanız var. Lütfen cevap seçeneklerinden birini seçin.",
            parse_mode='Markdown'
        )
        return
    
    # Eğer kullanıcı daha önce yarışmışsa, tekrar katılamayacağını belirt
    if user_id in user_quiz_status and user_quiz_status[user_id]["has_played"]:
        await update.message.reply_text(
            "🚫 *Yarışmaya Tekrar Katılamazsınız!*\n\n"
            "Bu yarışmaya daha önce katıldınız. Her kullanıcı sadece 1 kez yarışabilir.\n\n"
            f"Yarışma sonucunuz: {user_quiz_status[user_id]['final_score']} puan\n"
            f"Yarışma tarihi: {user_quiz_status[user_id]['completion_date']}",
            parse_mode='Markdown'
        )
        return
    
    # Eğer kullanıcının aktif yarışması yoksa ve daha önce yarışmamışsa, yeni yarışma başlat
    if user_id not in user_states or not user_states[user_id]["is_playing"]:
        await update.message.reply_text(
            "🎮 *Yeni Yarışma Başlatmak İçin:*\n\n"
            "Lütfen `/start` komutunu kullanın veya 'Yarışmaya Başla!' butonuna tıklayın.",
            parse_mode='Markdown'
        )
        return

async def button_callback(update, context):
    query = update.callback_query
    user_id = update.effective_user.id
    await query.answer()

    if query.data == 'start_quiz':
        if user_id not in user_states:
            user_states[user_id] = {"current_question": 0, "is_playing": True, "score": 0, "waiting_for_wallet": False}
        await ask_question(update, context, user_id)
    
    elif query.data == 'quit_quiz':
        if user_id in user_states and user_states[user_id]["is_playing"]:
            score = user_states[user_id]["score"]
            user_states[user_id]["is_playing"] = False
            
            # Kullanıcının yarışma durumunu kalıcı olarak kaydet
            user_quiz_status[user_id] = {
                "has_played": True,
                "final_score": score,
                "completion_date": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "result": "manuel_bitirme"
            }
            
            await query.message.reply_text(
                f"Yarışmayı bitirdin! 🏁\n"
                f"Kazandığın toplam puan: {score}\n\n"
                "🚫 Bu yarışmaya tekrar katılamazsınız. Her kullanıcı sadece 1 kez yarışabilir."
            )
            
            # Kullanıcının aktif durumunu sıfırla
            if user_id in user_states:
                del user_states[user_id]
    
    elif query.data.startswith('answer_'):
        if user_id not in user_states or not user_states[user_id]["is_playing"]:
            return

        current_q = user_states[user_id]["current_question"]
        answer_index = int(query.data.split('_')[1])
        correct_index = user_states[user_id]["current_correct_answer"]

        if answer_index == correct_index:
            user_states[user_id]["current_question"] += 1
            user_states[user_id]["score"] += 10
            keyboard = [[InlineKeyboardButton("Devam Et ➡️", callback_data='start_quiz')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(f"Harika cevap! 🎉\nHarikasın 10 puan kazandın! Toplam puanın: {user_states[user_id]['score']}", reply_markup=reply_markup)
        else:
            score = user_states[user_id]["score"]
            user_states[user_id]["is_playing"] = False
            
            # Doğru cevabı bul
            question_text = query.message.text.split('\n\n')[1]  # Soru metnini al
            correct_answer = query.message.reply_markup.inline_keyboard[correct_index][0].text
            
            # Kullanıcının yarışma durumunu kalıcı olarak kaydet
            user_quiz_status[user_id] = {
                "has_played": True,
                "final_score": score,
                "completion_date": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "result": "yanlış_cevap",
                "correct_answer": correct_answer
            }
            
            await query.message.reply_text(
                f"Malesef yarışma sona erdi ❌\n"
                f"Kazandığın puan: {score}\n\n"
                f"Yanlış cevap verdin. Doğru cevap: {correct_answer}\n\n"
                "🚫 Bu yarışmaya tekrar katılamazsınız. Her kullanıcı sadece 1 kez yarışabilir."
            )
            
            # Kullanıcının aktif durumunu sıfırla
            if user_id in user_states:
                del user_states[user_id]

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(ChatMemberHandler(new_member, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet_address))
    app.run_polling()

if __name__ == "__main__":
    main()
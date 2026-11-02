import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from pathlib import Path

# ===================== НАСТРОЙКИ =====================
BOT_TOKEN = "9101492286:AAFIzzllDKGx6V7kWDGXmMVSkqoL7_ev4lg"   # токен бота, например "123456:ABC..."
OWNER_ID = "5307702348"
# =====================================================


# ===================== ТЕКСТЫ (донат без стикеров) =====================

WELCOME = "Привет! Это бот сервера Trinity Mine.\n\nВыбери раздел:"

DONATE_MENU = "Донат\n\nВыбери раздел:"

PREFIXES = """ПРЕФИКСЫ

Vip - 19₽ или 15 зв
Про - 29₽ или 25 зв
Рыцарь - 39₽ или 30 зв
Сталкер - 49₽ или 45 зв
Принц - 59₽ или 50 зв
Сигма - 69₽ или 65 зв
Элита - 79₽ или 75 зв
Авторитет - 89₽ или 80 зв
Читер - 99₽ или 95 зв
Король - 109₽ или 100 зв

Купить можно у @Werdinantt"""

KITS_TITLE = "ДОНАТ КИТЫ"

# каждый кит отдельным блоком; блоки склеиваются в сообщения не длиннее лимита Telegram
KITS = [
"""⚔️━━━ КИТ 1 ━━━⚔️

💰 Цены
▫️ 1 месяц — 30₽ / 25 зв
▫️ 3 месяца — 70₽ / 50 зв
▫️ Навсегда — 110₽ / 100 зв

🎒 Состав
🪖 Медный шлем — з1, нер3
🛡 Медный нагрудник — з1, нер1
👖 Медные поножи — з1, нерз1
👢 Медные ботинки — з1, нер2
🗡 Железный меч — ост1, нерз3
⛏ Железная кирка — нерз2, удача1, эф1
🪓 Железный топор — эф1, нер2
🥩 Стейк ×16
🪣 Ведро воды и лавы по 1 шт.
🛡 Щит — нерз1, починка
🎣 Удочка — починка
🪵 Дерево ×128
🪨 Камень ×128""",
"""🔩━━━ КИТ 2 ━━━🔩
⚙️ ВСЁ ЖЕЛЕЗНОЕ

💰 Цены
▫️ 1 месяц — 60₽ / 50 зв
▫️ 3 месяца — 100₽ / 100 зв
▫️ Навсегда — 150₽ / 150 зв

🎒 Состав
🛡 Броня — защ2, неразруш3
🗡 Меч — острота3, облик огня1, неразруш1
⛏ Кирка — неразруш2, удача1, эфф3
🪓 Топор — неразруш3, эфф2
🏹 Лук — воспламенение, мощь2
🎣 Удочка — приманка2
🏹 Стрелы ×64
🪵 Дерево ×64
🪨 Камень ×128
🥩 Стейк ×32
🧿 Тотем ×1""",
"""💎━━━ КИТ 3 ━━━💎
✨ ВСЁ АЛМАЗНОЕ

💰 Цены
▫️ 1 месяц — 100₽ / 100 зв
▫️ 3 месяца — 140₽ / 125 зв
▫️ Навсегда — 200₽ / 200 зв

🎒 Состав
🛡 Броня — защита3, шипы2, неразруш3
🗡 Меч — острота4, облик огня1, неразруш2, добыча1, отбрас1
🪓 Топор — неразруш3, эфф4
⛏ Кирка — неразруш3, удача2, эфф4
🏹 Арбалет — неразруш3, залп, быстр. перезарядка1
🎣 Удочка — неразруш3, приманка2
🛡 Щит ×1
🏹 Стрелы ×128
🥩 Стейк ×64
🧿 Тотем ×2
🪵 Дерево ×128
🪨 Камень ×192
🥚 Яйцо призыва жителя ×1""",
"""🔥━━━ КИТ 4 ━━━🔥
🟣 ВСЁ НЕЗЕРИТОВОЕ

💰 Цены
▫️ 1 месяц — 149₽ / 150 зв
▫️ 3 месяца — 179₽ / 175 зв
▫️ Навсегда — 279₽ / 250 зв

🎒 Состав
🛡 Броня — защита4, шипы2, неразруш3
🗡 Меч — острота4, облик огня2, неразруш3, добыча2, отбрас1
⛏ Кирка — неразруш3, удача3, эфф5
🪓 Топор — неразруш3, эфф5
🎣 Удочка — морская удача3, неразруш3, приманка2
🏹 Арбалет — неразруш3, залп, быстрая перезарядка2
🔨 Булава — без чар
🏹 Стрелы ×192
🧿 Тотем ×3
🪨 Камень ×192
🪵 Дерево ×256
🥩 Стейк ×64
🍎 Геплы ×16
✨ Чар. яблоко ×1""",
"""🌾━━━ ПВЕ 1 ━━━🌾
⚙️ Железная броня + алмазные инструменты

💰 Цены
▫️ 1 месяц — 80₽ / 75 зв
▫️ 3 месяца — 120₽ / 115 зв
▫️ Навсегда — 170₽ / 150 зв

🎒 Состав
🪖 Шлем — з2, шип1, родство с водой
🛡 Нагрудник — з3, шип1
👖 Штаны — з2, шип1
👢 Ботинки — з2, шип1
🗡 Меч — о2, починка
⛏ Кирка — удача1, эф2, починка
🪏 Лопата — эф2, починка
🌿 Мотыга — эф2, починка
🧿 Тотем ×1
🌱 Зёрна 4 вида по 16 шт.
🎃 Два вида тыкв по 2 шт.
🟫 Земля ×128
🪵 Дерево ×128
🪨 Камень ×128
🪣 Ведро воды и лавы
🥩 Стейк ×32
🦴 Костная мука ×16""",
"""🌾━━━ ПВЕ 2 ━━━🌾
💎 ВСЁ АЛМАЗНОЕ

💰 Цены
▫️ 1 месяц — 120₽ / 100 зв
▫️ 3 месяца — 160₽ / 150 зв
▫️ Навсегда — 220₽ / 200 зв

🎒 Состав
🪖 Шлем — з3, шип2, нерз2, родство с водой, починка
🛡 Нагрудник — з3, шип2, нерз2, починка
👖 Штаны — з3, шип2, нерз2, починка
👢 Ботинки — з3, шип2, нерз2, починка, мороз. ходок
🗡 Меч — острота3, облик1, починка
⛏ Кирка — эфф4, удача2, починка
🪏 Лопата — эфф4, починка
🌿 Мотыга — эфф4, починка
🎣 Удочка — починка
🧿 Тотем ×1
🟫 Земля ×128
🪣 Ведро воды и лавы
🪵 Дерево ×192
🪨 Камень ×192
🥩 Стейк ×64
🌱 Семена 4 вида по 32 шт.
🦴 Костная мука ×32""",
"""🌾━━━ ПВЕ 3 ━━━🌾
🟣 ВСЁ НЕЗЕРИТОВОЕ

💰 Цены
▫️ 1 месяц — 159₽ / 200 зв
▫️ 3 месяца — 199₽ / 250 зв
▫️ Навсегда — 259₽ / 300 зв

🎒 Состав
🪖 Шлем — родство с водой, шип3, з4, нерз3, починка
🛡 Нагрудник — шип3, нерз3, починка, з4
👖 Штаны — шип3, нерз3, починка, з4
👢 Ботинки — шип3, нерз3, починка, з4, мороз. ходок3
🗡 Меч — ост3, облик2, нерз3, починка, добыча3
⛏ Кирка — удача3, нерз3, починка, эф5
🌿 Мотыга — эф5, нерз3, починка
🪏 Лопата — нерз3, починка, эф5
🎣 Удочка — морская удача3, починка
🟫 Земля ×192
🪵 Дерево ×192
🪨 Камень ×192
🎃 Два вида тыкв по 10 шт.
🌱 Семена 4 вида по 64 шт.
🪣 Ведро воды и лавы""",
]


COMPLAINT_INFO = """Как оформить жалобу

1) напиши свой ник
2) ник нарушителя
3) опиши ситуацию
4) по возможности предъяви фото-видео доказательства о нарушении

Отправь всё это следующим сообщением (можно несколькими)."""

SUPPORT_INFO = """Поддержка

Опиши свою ситуацию одним или несколькими сообщениями, и мы ответим тебе в этом чате."""

SENT_OK = "Отправлено. Ответ придёт в этот чат.\nМожно дополнить: просто напиши ещё сообщение. /start - вернуться в меню."
TOO_MANY = "Слишком много сообщений за короткое время. Подожди немного и попробуй снова."
NOT_READY = "Бот ещё не настроен: администратор не указал свой Telegram id."
PRIVATE_ONLY = "Напиши мне в личные сообщения: /start"


# ===================== БОТ =====================

API_URL = "https://api.telegram.org/bot{token}/{method}"
MAX_TICKETS = 3000
MODE_TTL = 30 * 60          # сколько режим «жалоба/поддержка» остаётся включённым
RATE_COUNT, RATE_WINDOW = 15, 600
ACK_GAP = 60
MAX_TEXT = 3800


def split_chunks(blocks, limit=3900, sep="\n\n"):
    """Склеивает блоки в сообщения не длиннее limit (каждый блок целиком)."""
    out, cur = [], ""
    for block in blocks:
        if not cur:
            cur = block
        elif len(cur) + len(sep) + len(block) <= limit:
            cur += sep + block
        else:
            out.append(cur)
            cur = block
    if cur:
        out.append(cur)
    return out


def kb(rows):
    return {"inline_keyboard": [[{"text": t, "callback_data": d} for t, d in row] for row in rows]}


MENU_KB = kb([[("Донат", "donate")], [("Поддержка", "support")], [("Жалобы", "complaint")]])
DONATE_KB = kb([[("Префиксы", "prefixes")], [("Кит старты", "kits")], [("Назад", "menu")]])
BACK_DONATE_KB = kb([[("Назад", "donate")]])
CANCEL_KB = kb([[("Отмена", "menu")]])


class TelegramBot:
    def __init__(self, token, owner_id, data_dir=".", log=print, api=None):
        self.token = str(token).strip()
        self.owner_id = int(owner_id) if str(owner_id).strip().lstrip("-").isdigit() else None
        self.log = log
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.tickets_file = self.data_dir / "tickets.json"
        self.tickets = {}      # id сообщения у владельца -> {"chat": id, "kind": str}
        self.modes = {}        # id пользователя -> {"kind": str, "t": float, "ack": float}
        self.rates = {}        # id пользователя -> deque времён
        self.running = False
        self._api = api or self._http_api
        self._load()

    # ---------- хранилище ----------

    def _load(self):
        try:
            if self.tickets_file.exists():
                self.tickets = json.loads(self.tickets_file.read_text(encoding="utf-8"))
        except Exception as ex:
            self.log(f"Не удалось прочитать tickets.json: {ex}")

    def _save(self):
        try:
            while len(self.tickets) > MAX_TICKETS:
                self.tickets.pop(next(iter(self.tickets)))
            self.tickets_file.write_text(json.dumps(self.tickets, ensure_ascii=False), encoding="utf-8")
        except Exception as ex:
            self.log(f"Не удалось сохранить tickets.json: {ex}")

    # ---------- Telegram API ----------

    def _http_api(self, method, params=None, timeout=35):
        url = API_URL.format(token=self.token, method=method)
        data = urllib.parse.urlencode(
            {k: (json.dumps(v) if isinstance(v, (dict, list)) else v) for k, v in (params or {}).items()}
        ).encode()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as ex:
            try:
                return json.loads(ex.read().decode("utf-8"))
            except Exception:
                return {"ok": False, "error_code": ex.code, "description": str(ex)}

    def call(self, method, **params):
        try:
            res = self._api(method, params)
        except Exception as ex:
            self.log(f"Telegram {method}: {ex}")
            return {}
        if not res.get("ok"):
            self.log(f"Telegram {method}: {res.get('error_code')} {res.get('description')}")
            return {}
        return res.get("result") or {}

    def send(self, chat, text, markup=None):
        params = {"chat_id": chat, "text": text[:4096]}
        if markup:
            params["reply_markup"] = markup
        return self.call("sendMessage", **params)

    def show(self, cb, text, markup=None):
        """Меняет сообщение с кнопкой; если не вышло, отправляет новое."""
        msg = cb.get("message") or {}
        params = {"chat_id": msg.get("chat", {}).get("id"), "message_id": msg.get("message_id"), "text": text[:4096]}
        if markup:
            params["reply_markup"] = markup
        if not (params["chat_id"] and params["message_id"] and self.call("editMessageText", **params)):
            self.send(params["chat_id"] or cb["from"]["id"], text, markup)

    # ---------- цикл ----------

    def run(self):
        self.running = True
        self.call("deleteWebhook")
        self.call("setMyCommands", commands=[{"command": "start", "description": "Открыть меню"}])
        offset = 0
        conflict_logged = False
        while self.running:
            try:
                res = self._api(
                    "getUpdates",
                    {"offset": offset, "timeout": 25, "allowed_updates": ["message", "callback_query"]},
                    45,
                )
            except Exception as ex:
                self.log(f"Telegram недоступен: {ex}")
                time.sleep(5)
                continue
            if not res.get("ok"):
                if res.get("error_code") == 409 and not conflict_logged:
                    conflict_logged = True
                    self.log("Конфликт 409: этот токен уже используется другим запущенным ботом. Остановите его.")
                elif res.get("error_code") == 401:
                    self.log("Неверный токен бота (401). Проверьте token в config.toml.")
                    time.sleep(30)
                time.sleep(5)
                continue
            conflict_logged = False
            for upd in res.get("result", []):
                offset = upd["update_id"] + 1
                try:
                    self.handle_update(upd)
                except Exception as ex:
                    self.log(f"Ошибка обработки обновления: {ex}")

    def stop(self):
        self.running = False

    # ---------- обработка ----------

    def handle_update(self, upd):
        if "callback_query" in upd:
            self.on_callback(upd["callback_query"])
        elif "message" in upd:
            self.on_message(upd["message"])

    def _is_owner(self, user_id):
        return self.owner_id is not None and user_id == self.owner_id

    def on_callback(self, cb):
        self.call("answerCallbackQuery", callback_query_id=cb["id"])
        uid = cb["from"]["id"]
        data = cb.get("data", "")
        if data == "menu":
            self.modes.pop(uid, None)
            self.show(cb, WELCOME, MENU_KB)
        elif data == "donate":
            self.modes.pop(uid, None)
            self.show(cb, DONATE_MENU, DONATE_KB)
        elif data == "prefixes":
            self.show(cb, PREFIXES, BACK_DONATE_KB)
        elif data == "kits":
            chat = cb["message"]["chat"]["id"]
            self.show(cb, KITS_TITLE)
            chunks = split_chunks(KITS)
            for i, chunk in enumerate(chunks):
                self.send(chat, chunk, BACK_DONATE_KB if i == len(chunks) - 1 else None)
        elif data in ("complaint", "support"):
            self.modes[uid] = {"kind": data, "t": time.time(), "ack": 0.0}
            self.show(cb, COMPLAINT_INFO if data == "complaint" else SUPPORT_INFO, CANCEL_KB)

    def on_message(self, msg):
        chat = msg.get("chat", {})
        user = msg.get("from", {})
        uid = user.get("id")
        if uid is None or user.get("is_bot"):
            return
        text = (msg.get("text") or "").strip()
        if text.split("@")[0] == "/id":
            self.send(chat["id"], f"Твой Telegram id: {uid}")
            return
        if chat.get("type") != "private":
            if text.startswith("/"):
                self.send(chat["id"], PRIVATE_ONLY)
            return
        # ответ владельца на жалобу/обращение
        if self._is_owner(uid) and msg.get("reply_to_message"):
            if self.reply_from_owner(msg):
                return
        if text.startswith("/start") or text.startswith("/menu"):
            self.modes.pop(uid, None)
            self.send(chat["id"], WELCOME, MENU_KB)
            return
        mode = self.modes.get(uid)
        if mode and time.time() - mode["t"] > MODE_TTL:
            self.modes.pop(uid, None)
            mode = None
        if mode:
            self.forward_to_owner(msg, user, mode)
        else:
            self.send(chat["id"], WELCOME, MENU_KB)

    # ---------- жалобы и поддержка ----------

    def _rate_ok(self, uid):
        q = self.rates.setdefault(uid, deque())
        now = time.time()
        while q and now - q[0] > RATE_WINDOW:
            q.popleft()
        if len(q) >= RATE_COUNT:
            return False
        q.append(now)
        return True

    @staticmethod
    def _who(user):
        name = " ".join(x for x in (user.get("first_name"), user.get("last_name")) if x) or "без имени"
        tag = f" @{user['username']}" if user.get("username") else ""
        return f"{name}{tag} (id {user['id']})"

    def forward_to_owner(self, msg, user, mode):
        chat = msg["chat"]["id"]
        if self.owner_id is None:
            self.send(chat, NOT_READY)
            return
        if not self._rate_ok(user["id"]):
            self.send(chat, TOO_MANY)
            return
        title = "Жалоба" if mode["kind"] == "complaint" else "Поддержка"
        header = f"{title} от {self._who(user)}"
        sent_ids = []
        body = msg.get("text")
        if body:
            res = self.send(self.owner_id, f"{header}\n\n{body[:MAX_TEXT]}")
            sent_ids.append(res.get("message_id"))
        else:
            res = self.send(self.owner_id, header)
            sent_ids.append(res.get("message_id"))
            copied = self.call("copyMessage", chat_id=self.owner_id, from_chat_id=chat, message_id=msg["message_id"])
            sent_ids.append(copied.get("message_id"))
        for mid in filter(None, sent_ids):
            self.tickets[str(mid)] = {"chat": chat, "kind": mode["kind"]}
        self._save()
        mode["t"] = time.time()
        if time.time() - mode["ack"] > ACK_GAP:
            mode["ack"] = time.time()
            self.send(chat, SENT_OK)

    def reply_from_owner(self, msg):
        ticket = self.tickets.get(str(msg["reply_to_message"].get("message_id")))
        if not ticket:
            return False
        target = ticket["chat"]
        prefix = "Ответ администрации:"
        body = msg.get("text")
        if body:
            self.send(target, f"{prefix}\n\n{body[:MAX_TEXT]}")
        else:
            self.send(target, prefix)
            self.call("copyMessage", chat_id=target, from_chat_id=msg["chat"]["id"], message_id=msg["message_id"])
        self.send(msg["chat"]["id"], "Ответ отправлен.")
        return True


def main():
    token = os.environ.get("BOT_TOKEN") or BOT_TOKEN
    owner = os.environ.get("OWNER_ID") or OWNER_ID
    if ":" not in str(token):
        raise SystemExit("Впиши токен бота в BOT_TOKEN в начале файла bot.py")
    data_dir = os.environ.get("DATA_DIR") or Path(__file__).resolve().parent
    bot = TelegramBot(token, owner, data_dir, log=lambda m: print(time.strftime("%H:%M:%S"), m, flush=True))
    if bot.owner_id is None:
        print("OWNER_ID не задан: напиши боту /id, впиши число в OWNER_ID и перезапусти", flush=True)
    print("Бот запущен", flush=True)
    try:
        bot.run()
    except KeyboardInterrupt:
        bot.stop()


if __name__ == "__main__":
    main()
    

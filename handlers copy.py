# ================== handlers.py ==================
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.ext import ContextTypes, ConversationHandler
from sheet import sheet_handler
from difflib import get_close_matches
import re
import time
import os
from datetime import datetime
from collections import Counter

# Load known brands from external file
with open("brands.txt", "r", encoding="utf-8") as f:
    KNOWN_BRANDS = [line.strip() for line in f if line.strip()]

STORE_LOCATION_URL = "https://maps.app.goo.gl/RiURGuNtMyzSCmyDA"

CHOOSE_CATEGORY, ASK_MODEL = range(2)

inventory_cache = {
    "timestamp": 0,
    "data": None
}

CACHE_DURATION = 300

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

CATEGORY_MAPPING = {
    "LCD": "LCD",
    "Battery": "BATTERIE",
    "Connector": "CC",
    "Glass": "GLASS",
    "COVER": "COVER",
    "SERSOU": "SERSOU"
}

async def log_request(category, model, available):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_DIR, f"{date_str}.log")
    with open(log_file, "a") as f:
        f.write(f"{now.strftime('%H:%M:%S')} - {category} - {model} - {'Available' if available else 'Not available'}\n")

async def get_cached_inventory():
    now = time.time()
    if inventory_cache["data"] is None or now - inventory_cache["timestamp"] > CACHE_DURATION:
        data = await sheet_handler.get_inventory()
        for row in data:
            try:
                qt_raw = str(row.get("QT", "")).strip()
                row["QT"] = float(qt_raw) if qt_raw and float(qt_raw) > 0 else 0
                pu_raw = str(row.get("PU", "")).strip()
                row["PU"] = float(pu_raw) if pu_raw else 0
            except:
                row["QT"] = 0
                row["PU"] = 0
        inventory_cache["data"] = data
        inventory_cache["timestamp"] = now
    return inventory_cache["data"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    buttons = [
        [InlineKeyboardButton("📱 LCD", callback_data="LCD")],
        [InlineKeyboardButton("🔋 Batterie", callback_data="Battery")],
        [InlineKeyboardButton("🔌 Connecteur", callback_data="Connector")],
        [InlineKeyboardButton("🧿 Glass", callback_data="Glass")],
        [InlineKeyboardButton("📦 Cover", callback_data="COVER")],
        [InlineKeyboardButton("🛠 Sersou", callback_data="SERSOU")]
    ]
    markup = InlineKeyboardMarkup(buttons)

    if update.message:
        await update.message.reply_text("Bienvenue ! Choisissez une catégorie :", reply_markup=markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("Bienvenue ! Choisissez une catégorie :", reply_markup=markup)

    return CHOOSE_CATEGORY

async def category_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data

    if category == "restart":
        return await restart_search(update, context)

    context.user_data["category"] = category
    await query.edit_message_text(f"Vous avez choisi la catégorie : {category}\n\nVeuillez maintenant entrer le modèle de téléphone 📱:")
    return ASK_MODEL

async def handle_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip().lower()
    category = context.user_data.get("category")
    if not category:
        await update.message.reply_text("❌ Veuillez d'abord choisir une catégorie avec /start.")
        return ConversationHandler.END

    await update.message.chat.send_action(action=ChatAction.TYPING)

    if not re.match(r"^[a-z0-9\s\-+_.]+$", user_input):
        await update.message.reply_text("❌ Entrée invalide. Veuillez saisir un modèle de téléphone valide.")
        return ASK_MODEL

    input_words = user_input.split()
    possible_brand = input_words[0]
    matched_brand = get_close_matches(possible_brand, [b.lower() for b in KNOWN_BRANDS], n=1, cutoff=0.8)
    if matched_brand:
        corrected_brand = matched_brand[0]
        user_input = user_input.replace(possible_brand, corrected_brand)

    designation_keyword = CATEGORY_MAPPING.get(category, category)
    data = await get_cached_inventory()
    filtered_data = [row for row in data if designation_keyword.lower() in row["Designation1"].lower()]

    potential_matches = []
    for row in filtered_data:
        if user_input in row["Designation1"].lower():
            potential_matches.append(row)

    if not potential_matches:
        all_model_names = [row["Designation1"].lower() for row in filtered_data]
        close = get_close_matches(user_input, all_model_names, n=1, cutoff=0.9)
        if close:
            for row in filtered_data:
                if close[0] == row["Designation1"].lower():
                    return await respond_with_inventory_info(update, context, row, category, user_input)

        await log_request(category, user_input, False)
        await update.message.reply_text(f"❌ {user_input} n'est pas disponible dans notre inventaire. Essayez un autre modèle ou recommencez.")
        return await start(update, context)

    if len(potential_matches) == 1:
        return await respond_with_inventory_info(update, context, potential_matches[0], category, user_input)

    context.user_data['pending_matches'] = potential_matches
    context.user_data['search_query'] = user_input
    buttons = []
    for row in potential_matches:
        label = row['Designation1']
        buttons.append([InlineKeyboardButton(label, callback_data=f"select::{label}")])
    markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("🔍 Plusieurs correspondances trouvées. Veuillez préciser :", reply_markup=markup)
    return ASK_MODEL

async def handle_model_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_model = query.data.split("::")[1]
    category = context.user_data.get("category")
    if not category:
        await query.edit_message_text("❌ La catégorie est introuvable. Veuillez redémarrer avec /start.")
        return ConversationHandler.END

    data = await get_cached_inventory()
    for row in data:
        if row['Designation1'] == selected_model:
            return await respond_with_inventory_info(query, context, row, category, selected_model)

    await query.edit_message_text(f"❌ Impossible de trouver {selected_model} dans la catégorie {category}.")
    return await start(query, context)

async def respond_with_inventory_info(query_or_update, context, row, category, match_part):
    message = query_or_update.message if hasattr(query_or_update, 'message') else query_or_update.effective_message
    phone_model = row["Designation1"]
    available = row.get("QT", 0)
    price = row.get("PU", "-")

    matched_model_name = match_part.title()
    brand_match = next((b for b in KNOWN_BRANDS if b.lower() in phone_model.lower()), "")
    formatted_model = f"{brand_match.upper()} {matched_model_name}".strip()

    buttons = [
        [InlineKeyboardButton("📍 Voir l'emplacement du magasin", url=STORE_LOCATION_URL)],
        [InlineKeyboardButton("🔁 Démarrer une nouvelle recherche", callback_data="restart")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    if isinstance(available, (int, float)) and available > 0:
        await log_request(category, formatted_model, True)
        await message.reply_text(
            f"✅ {category.upper()} pour {formatted_model} est disponible.\n💵 Prix : {price} DA",
            reply_markup=reply_markup
        )
    else:
        await log_request(category, formatted_model, False)
        await message.reply_text(
            f"❌ Désolé, {category.lower()} pour {formatted_model} n'est pas disponible.",
            reply_markup=reply_markup
        )
    return CHOOSE_CATEGORY

async def restart_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    inventory_cache["data"] = None

    await query.message.reply_text("🔁 Nouvelle recherche démarrée.")
    return await start(update, context)

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("🗕 Résumé d'aujourd'hui", callback_data="summary_today")],
        [InlineKeyboardButton("🗖 Résumé du mois", callback_data="summary_month")]
    ]
    markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Choisissez un type de résumé :", reply_markup=markup)

async def handle_summary_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data_type = query.data
    now = datetime.now()

    if data_type == "summary_today":
        date_str = now.strftime("%Y-%m-%d")
        log_file = os.path.join(LOG_DIR, f"{date_str}.log")
        summary = read_detailed_log_summary(log_file)
        await query.edit_message_text(f"🗕 Résumé du {date_str} :\n\n{summary}")

    elif data_type == "summary_month":
        month_str = now.strftime("%Y-%m")
        summaries = []
        for filename in os.listdir(LOG_DIR):
            if filename.startswith(month_str) and filename.endswith(".log"):
                log_file = os.path.join(LOG_DIR, filename)
                summaries.append(f"{filename[:-4]}:\n{read_detailed_log_summary(log_file)}\n")
        if summaries:
            await query.edit_message_text("🗖 Résumé du mois :\n\n" + "\n".join(summaries))
        else:
            await query.edit_message_text("📍 Aucun enregistrement pour ce mois.")

def read_detailed_log_summary(file_path):
    total = 0
    available = 0
    not_available = 0
    model_stats = Counter()
    not_available_models = []

    try:
        with open(file_path, 'r') as f:
            for line in f:
                total += 1
                parts = line.strip().split(" - ")
                if len(parts) < 3:
                    continue
                model = parts[1]
                status = parts[2]
                model_stats[model] += 1
                if "Available" in status:
                    available += 1
                else:
                    not_available += 1
                    not_available_models.append(model)

        top_models = model_stats.most_common(5)
        top_text = "\n".join([f"🔹 {model} ({count} demandes)" for model, count in top_models])
        unavailable_text = "\n".join([f"❌ {model}" for model in sorted(set(not_available_models))])

        return (
            f"🔎 Total: {total}\n"
            f"✅ Disponibles: {available}\n"
            f"❌ Non disponibles: {not_available}\n\n"
            f"📊 Top 5 modèles demandés :\n{top_text or 'Aucune donnée'}\n\n"
            f"🚫 Modèles non disponibles :\n{unavailable_text or 'Aucun'}"
        )
    except FileNotFoundError:
        return "Aucune donnée trouvée pour cette date."

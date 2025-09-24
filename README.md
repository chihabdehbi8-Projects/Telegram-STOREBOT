# 📱 Telegram StoreBot  

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)  

A **Telegram bot** for managing and searching a phone parts store.  
The bot allows users to check part availability, tracks all searches in **Excel reports** with charts, and includes a **whitelist system** for controlling access.  

---

## 🚀 Features  

- 🔎 **Search system**: Users can check if a phone model/display is available.  
- 📊 **Excel logging**: All searches are saved daily into `.xlsx` files.  
  - **Daily reports** (one file per day).  
  - **Weekly reports** (aggregated automatically every Saturday).  
  - Built-in charts:
    - Pie chart → Searches by category.  
    - Bar chart → Availability status (Available vs Not Available).  
    - Line chart → Searches by hour.  
- ✅ **Whitelist authentication**: Only approved users can use the bot.  
  - Add users via a helper script using their Telegram ID or phone number.  
  - Whitelist reloads dynamically without restarting the bot.  
- 📂 **Organized stats**:
```
stats/
daily/
YYYY-MM-DD.xlsx
weekly/
week-YYYY-MM-DD_to_YYYY-MM-DD.xlsx
```
---

## 🛠️ Installation  

1. Clone the repository:  
 ```bash
 git clone https://github.com/chihabdehbi8-Projects/Telegram-STOREBOT.git
 cd Telegram-STOREBOT
Create a virtual environment and install dependencies:
python3 -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows

pip install -r requirements.txt
Add your Telegram bot token and other configs in config.py.
```
---

📋 Usage
- Run the bot
```
 python3 bot.py
```
- Add a user to whitelist
```
  Run the helper script:
  python3 add_to_WhiteList.py
```
- Enter the Telegram phone number (e.g. +213XXXXXXXXX) → the script fetches the user ID and adds it to whitelist.py.
📊 Example Reports
- Daily log: Contains timestamp, category, model, and status (Available / Not Available).
- Category Summary: Counts of searches per category.
- Not Available: Extract of all unavailable searches.
- Charts: Pie, bar, and line charts auto-generated inside Excel.
---
📦 Dependencies
```
python-telegram-bot
openpyxl
Python 3.8+
```
---

🗂️ Project Structure
```bash
📂 STOREBOT/
 ├── bot.py                # Main Telegram bot
 ├── add_to_WhiteList.py   # Script to add users to whitelist
 ├── whitelist.py          # Dynamic whitelist storage
 ├── config.py             # Bot configuration
 ├── stats/                # Daily & weekly Excel reports
 ├── requirements.txt      # Dependencies
 └── README.md             # Project documentation
```
---

📌 Roadmap
```
 Add monthly reports (aggregating weekly logs).
 Add Top searched models sheet.
 Add error logs for failed requests.
 Deploy to cloud hosting (Heroku, Railway, etc.).
```
---
👤 
Chihab – Biomedical Engineer & Software Developer

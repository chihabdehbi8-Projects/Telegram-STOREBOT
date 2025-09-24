# add_to_whitelist.py
import ast

WHITELIST_FILE = "whitelist.py"

def load_whitelist():
    try:
        with open(WHITELIST_FILE, "r") as f:
            data = f.read().strip()
            # Expecting something like: WHITELIST = [123, 456]
            if data.startswith("WHITELIST"):
                wl = ast.literal_eval(data.split("=", 1)[1].strip())
                return wl
    except FileNotFoundError:
        return []
    return []

def save_whitelist(wl):
    with open(WHITELIST_FILE, "w") as f:
        f.write(f"WHITELIST = {wl}\n")

def add_user(user_id: int):
    wl = load_whitelist()
    if user_id not in wl:
        wl.append(user_id)
        save_whitelist(wl)
        print(f"✅ User {user_id} added to whitelist.")
    else:
        print(f"⚠️ User {user_id} is already in whitelist.")

if __name__ == "__main__":
    user_id = int(input("Enter the Telegram user ID: "))
    add_user(user_id)

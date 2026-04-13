import os
import hashlib
import sys
import json

# 設定區塊限制與路徑
STORAGE_PATH = "./storage"
BLOCK_CAPACITY = 5
INIT_FILE = f"{STORAGE_PATH}/init.json"

def get_balances():
    """從 init.json 讀取所有餘額"""
    if os.path.exists(INIT_FILE):
        with open(INIT_FILE, "r") as f:
            return json.load(f)
    return {}

def update_balances(balances):
    """將餘額寫回 init.json"""
    with open(INIT_FILE, "w") as f:
        json.dump(balances, f, indent=4)

def get_file_hash(file_path):
    """計算檔案內容的 SHA256"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_latest_block():
    """尋找目前的 .txt 區塊檔案"""
    if not os.path.exists(STORAGE_PATH):
        os.makedirs(STORAGE_PATH)
    files = [f for f in os.listdir(STORAGE_PATH) if f.endswith(".txt") and f[:-4].isdigit()]
    if not files:
        return None
    latest_file = sorted(files, key=lambda x: int(x[:-4]))[-1]
    return latest_file

def parse_block(file_path):
    """解析自定義 .txt 格式"""
    data = {"prev_hash": "None", "next_block": "None", "transactions": []}
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            # 直接按順序讀取第一和第二行
            line1 = f.readline()
            line2 = f.readline()
            if line1: data["prev_hash"] = line1.split(":")[-1].strip()
            if line2: data["next_block"] = line2.split(":")[-1].strip()
            
            # 指標已在第三行，直接抓取剩下的交易紀錄
            data["transactions"] = [line.strip() for line in f if line.strip()]
    return data

def write_block(file_path, data):
    """寫回自定義 .txt 格式"""
    with open(file_path, "w") as f:
        f.write(f"Sha256 of previous block:{data['prev_hash']}\n")
        f.write(f"Next block:{data['next_block']}\n")
        for tx in data["transactions"]:
            f.write(f"{tx}\n")

def process_transaction(sender, receiver, amount):
    # --- 餘額與使用者處理 ---
    balances = get_balances()

    # 初始化新使用者 (若不在名單內設為 0)
    if sender not in balances: balances[sender] = 0
    if receiver not in balances: balances[receiver] = 0

    # 檢查寄件人錢夠不夠
    if balances[sender] < amount:
        print(f"轉帳失敗: {sender} 餘額不足 (目前餘額: {balances[sender]})")
        update_balances(balances)
        return False

    # 更新金額
    balances[sender] -= amount
    balances[receiver] += amount
    update_balances(balances)
    # -----------------------

    new_tx_line = f"{sender},{receiver},{amount}"
    latest_file = get_latest_block()

    if latest_file is None:
        # 初始化第一份 block
        current__block_num = 1
        file_path = f"{STORAGE_PATH}/{current__block_num}.txt"
        data = {"prev_hash": "0" * 64, "next_block": "None", "transactions": []}
    else:
        # 讀取目前最後一個 block 的內容
        current__block_num = int(latest_file[:-4])
        file_path = f"{STORAGE_PATH}/{latest_file}"
        data = parse_block(file_path)

    # 加入新交易
    data["transactions"].append(new_tx_line)

    # 檢查 block 是否已滿
    if len(data["transactions"]) >= BLOCK_CAPACITY:
        next_num = current__block_num + 1
        data["next_block"] = f"{next_num}.txt"
        write_block(file_path, data)

        # 計算當前區塊 Hash 並預開下一個區塊
        current_hash = get_file_hash(file_path)
        next_file_path = f"{STORAGE_PATH}/{next_num}.txt"
        next_data = {"prev_hash": current_hash, "next_block": "None", "transactions": []}
        write_block(next_file_path, next_data)

        print(f"區塊 {current__block_num}.txt 已滿，已連鎖至 {next_num}.txt")
    else:
        write_block(file_path, data)
        print(f"交易已寫入 {current__block_num}.txt ({len(data['transactions'])}/{BLOCK_CAPACITY})")
    return True

def transaction():
    if len(sys.argv) != 4:
        print("用法: python3 app_transaction.py [寄件人] [收件人] [金額]")
        return

    sender, receiver, amount = sys.argv[1], sys.argv[2], int(sys.argv[3])
    process_transaction(sender, receiver, amount)

if __name__ == "__main__":
    transaction()

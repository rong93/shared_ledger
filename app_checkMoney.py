import sys
from app_transaction import get_balances

def check_money():
    if len(sys.argv) != 2:
        print("用法: python3 app_checkMoney.py [使用者名稱]")
        return

    user_name = sys.argv[1]
    
    # 直接呼叫 app_transaction 裡的函式
    balances = get_balances()

    if user_name in balances:
        print(f"{user_name} 的目前餘額為: {balances[user_name]}")
    else:
        print(f"錯誤: 找不到使用者 '{user_name}'")

if __name__ == "__main__":
    check_money()

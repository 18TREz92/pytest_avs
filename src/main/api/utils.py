# Математические вычисления для тестов

def calculate_balance_after_deposit(balance: float, amount: float) -> float:
    return balance + amount

def calculate_balance_after_transfer(balance: float, amount: float) -> float:
    return balance - amount

def calculate_initial_credit_balance(amount: float) -> float:
    return -amount
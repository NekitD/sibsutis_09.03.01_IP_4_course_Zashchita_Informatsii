import math
import random

from lab1_2 import pow_mod;
from lab1_2 import test_ferma;
        
def diffie_hellman(p, g, Xa, Xb):
    
    if not test_ferma(p):
        raise ValueError(f"p = {p} не является простым числом")
    
    if not (1 < g < p - 1):
        raise ValueError(f"g = {g} вне диапазона (1, {p-1})")
    
    if (p - 1) % 2 != 0:
        raise ValueError("p чётное => p не простое")
    q = (p - 1) // 2
    if not test_ferma(q):
        raise ValueError(f"q = {q} не простое")
    
    if pow_mod(g, q, p) == 1:
        raise ValueError(f"g^q mod p == 1")
    
    Ya = pow_mod(g, Xa, p)
    Yb = pow_mod(g, Xb, p)
    
    Za = pow_mod(Yb, Xa, p)
    Zb = pow_mod(Ya,Xb, p)
    
    return Za, Zb, Ya, Yb
    
def main():
    print("функция Диффи-Хеллмана")
    print("1 - ввести с клавиатуры")
    print("2 - сгенерировать автоматически")
    mode = input("[1/2]: ").strip()

    if mode == "1":
        p  = int(input("Введите простое число p: "))
        g  = int(input("Введите число g: "))
        Xa = int(input("Введите секретный ключ Xa: "))
        Xb = int(input("Введите секретный ключ Xb: "))
    else:
        while True:
            q = random.randint(0, 1000)
            if test_ferma(q) and test_ferma(2*q + 1):
                p = 2*q + 1
                break
        print(f"Сгенерировано простое число: p = {p} (q = {q})")

        while True:
            g = random.randint(2, p - 2)
            if pow_mod(g, q, p) != 1:
                break
        print(f"g = {g}")

        Xa = random.randint(2, p - 2)
        Xb = random.randint(2, p - 2)
        print(f"Секретные ключи: Xa = {Xa}, Xb = {Xb}")

    try:
        Za, Zb, Ya, Yb = diffie_hellman(p, g, Xa, Xb)
    except ValueError as e:
        print(f"Ошибка параметров: {e}")
        return

    print(f"Ya = {Ya}")
    print(f"Yb = {Yb}")
    print(f"A: K = {Za}")
    print(f"B: K = {Zb}")

    if Za == Zb:
        print(f"Общий ключ: Z = {Za}")
    else:
        print("Ошибка: ключи не совпали")


if __name__ == "__main__":
    main()
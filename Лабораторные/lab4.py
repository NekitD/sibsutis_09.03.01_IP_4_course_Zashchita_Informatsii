import math
import random

from lab1_2 import pow_mod;
from lab1_2 import test_ferma;

def Shamir(mes):
    print("Отправленное сообщение:")
    print(mes)
    g = 0
    while(g != 0 and g != 1):
        o = int(input("Ввод с клавиатуры/Генерация (1/2): "))
    if(g == 0):
        p = -1
        while(not test_ferma(p)):
            p = int(input("Введите простое число p: "))
        Ca = int(input("Введите Ca: "))
        Cb = int(input("Введите Cb: "))
    if(g == 1):
        Ca = random.randint(2, p-2)
        print(f'Ca = {Ca}')
        Cb = random.randint(2, p-2)
        print(f'Cb = {Cb}')
    Da = -1
    Db = -1
    while(pow_mod(Ca * Da, 1, p-1) != 1):
        Da = random.randint(2, p-2)
    while(pow_mod(Cb * Db, 1, p-1) != 1):
        Db = random.randint(2, p-2)
    print(f'Da = {Da}')
    print(f'Db = {Db}')
    x1 = pow_mod(mes, Ca, p)
    x2 = pow_mod(x1, Cb, p)
    x3 = pow_mod(x2, Da, p)
    x4 = pow_mod(x3, Db, p)
    print("Пришедшее сообщение:")
    print(x4)
    
def main():
    mes = 2
    Shamir(mes)

if __name__ == "__main__":
    main()
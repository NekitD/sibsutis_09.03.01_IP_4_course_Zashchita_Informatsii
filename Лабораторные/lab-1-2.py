import math
import random

# -----------------------------------------------------------------------
# Lab 1
# -----------------------------------------------------------------------

def pow_mod(a, x, p):
    if p == 0:
        raise ValueError("число p не может быть равным 0")
    
    res = 1
    onestep = a % p #первое действие (0)
    while x > 0: #для всех систем счисления не равно 0
        if x & 1: #если бит равен единице(всегда начинает с правого бита, потом будет идти в лево)
            res = (onestep * res) % p #считаем сразу с модулем, т к при 10^9 общий множитель будет огромным(финальное действие)
        onestep = pow(onestep, 2) % p  #каждый последующий шаг - возводим в степень остаток предыдущего и делим по модулю
        x >>= 1 #сдвигаем число на 1 бит в права(не мы сдвигаемся в лево, а двигаем само число, пока не встретим 0 для конца цикла: 1011 -> 0101 -> 0010 -> 0001)
        
    return res

def test_ferma(n, k=10):
    
    if n <= 1:
        return False #интервал для a = [2, n-2] не будет сходиться(и число 1 не простое)
    if n <= 3:
        return True #(2 и 3 простые числа, и для 2 интервал пустой, а для 3 - a=2)
    if n % 2:
        return False #(из всех четных только 2 - простое)
    
    for i in range(k): #цикл для точности, т к a - рандом на промежутке
        a = random.randint(2, n - 2) #выбираем a на данном интервале
        
        r = pow_mod(a, n-1, n) # - формула r = a^(n-1) mod n
        if r != 1: #число будет простым если формула выше равна 1
            return False
        
    return True

def euclid_gcd(a, b):
    
    u1, v1 = 1, 0
    u2, v2 = 0, 1
    
    while b != 0: #как только найдет 0, то запишет предыдущий результат
        q = a // b # проверка на b>a не нужна, т к он просто выполнит одну операцию, где автоматически поменяется местами
        a, b = b, a % b
        
        u1, u2 = u2, u1 - q*u2
        v1, v2 = v2, v1 - q*v2
    
    return (a, u1, v1)

def generate_prime(a, b):
    while True:
        n = random.randint(a, b)
        if test_ferma(n):
            return n
    

def generate_num_one():
    print("\nВыберите способ ввода чисел a и b:")
    print("1. Ввести с клавиатуры")
    print("2. Сгенерировать случайные числа")
    print("3. Сгенерировать простые числа")
    
    choice = input("Вариант(1-3): ")
    
    if choice == '1':
        try:
            a = int(input("Введите a: "))
            b = int(input("Введите b: "))
            return (a, b)
        except ValueError:
            print("вводите целые числа")
            return generate_num_one()
    
    elif choice == '2':
        a = random.randint(1, 1000)
        b = random.randint(1, 1000)
        print(f"Сгенерированные числа: a = {a}, b = {b}")
        return (a, b)
    
    elif choice == '3':
        a = generate_prime(1, 1000)
        b = generate_prime(1, 1000)
        print(f"Сгенерированные простые числа: a = {a}, b = {b}")
        return (a, b)
    
    else:
        print("Неверный выбор")
        return generate_num_one()
    
# -----------------------------------------------------------------------
# Lab 2
# -----------------------------------------------------------------------

def generate_num_two():
    print("\nВыберите способ ввода чисел a, y, p:")
    print("1. Ввести с клавиатуры")
    print("2. Сгенерировать случайные числа")
    choice = input("Вариант(1-2): ")
    if choice == '1':
        try:
            a = int(input("Введите a: "))
            y = int(input("Введите y: "))
            p = int(input("Введите p: "))
            if not p > y:
                print("Не выполнено условие: p > y")
                return generate_num_two()
            return a, y, p
        except ValueError:
            print("вводите целые числа")
            return generate_num_two()
    elif choice == '2':
        a = random.randint(1, 1000)
        y = random.randint(1, 999)
        p = random.randint(y, 1000)
        print(f"Сгенерированные числа: a = {a}, y = {y}, p = {p}")
        return a, y, p
    else:
        print("Неверный выбор")
        return generate_num_two()

def baby_giant_step():
    print()
    print("Шаг младенца, шаг великана")
    print("Общий вид задачи: y = a^x mod p, x - ?")
    a, y, p = generate_num_two()
    print(f'Итоговый вид задачи: {y} = {a}^x mod {p}, x - ?')
    m = 2
    k = p // m + 1
    m_res = []
    k_res = []
    print()
    print(f'Шаги младенца (0 - {m}): (y * a^j) % p')
    for j in range(0, m):
        step_res = [j, (y * (a**j)) % p] # [номер, результат]
        print(f'Шаг №{j}: ({y} * {a}^{j}) % {p} = {step_res[1]}')
        m_res.append(step_res)
    print()
    print(f'Шаги великана (0 - {k}): a^(i*m) % p')
    for i in range(1, k+1):
        step_res = [i, (a**(i*m)) % p] # [номер, результат]
        print(f'Шаг №{i}: {a}^({i}*{m}) % {p} = {step_res[1]}')
        k_res.append(step_res)

    x_list = []
    x_count = 0
    print()
    print("Поиск совпавших шагов и подсчёт X: x = i * m - j")
    print()
    for baby in m_res:
        for giant in k_res:
            if baby[1] == giant[1]: # сравниваем результаты
                x_val = giant[0] * m - baby[0]
                print(f'Шаг младенца №{baby[0]} = {baby[1]}')
                print(f'Шаг великана №{giant[0]} = {giant[1]}')
                print(f'x = {giant[0]} * {m} - {baby[0]} = {x}')
                x_count += 1
                x_list.append(x_count, x_val)
                print()
    print("Ответ: ")
    for x in x_list:
        print(f'x{x[0]} = {x[1]}')


# ====================================================================================

def lab1():
    
    print("\nвозведение числа в степень по модулю:")
    a = 7
    x = 19
    p = 100
    result = pow_mod(a, x, p)
    print(f"{a}^{x} mod {p} = {result}")
    
    print("\nтест ферма:")
    num = 16
    status = test_ferma(num, 5)
    print(f"{num}: {status}")
    
    print("\nтест ферма:")
    num = 3
    status = test_ferma(num, 5)
    print(f"{num}: {status}")
    
    print("\nгенеарция чисел:")
    a, b = generate_num_one()
    
    print("\nобобщенный алгоритм евклида:")
    gcd, x, y = euclid_gcd(a, b)
    
    print(f"  НОД({a}, {b}) = {gcd}")
    print(f"\n  Уравнение: {a} * {x} + {b} * {y} = {gcd}")
    print(f"  Проверка:  {a} * ({x}) + {b} * ({y}) = {a*x + b*y} = {gcd}")
    
    if a*x + b*y == gcd:
        print("верно!")
    else:
        print("ошибка!")

def lab2():
    print("Вычисление дискретного логарифма при помощи алгоритма «Шаг младенца, шаг великана»")
    baby_giant_step()
        
if __name__ == "__main__":
    while(True):
        l = int(input("Введите номер лабораторной (1 - 2) или 0 для выхода: "))
        if l == 1:
            lab1()
        elif l == 2:
            lab2()
        elif l == 0:
            print("Завершение работы!")
            break
        else:
            print("Такой лабораторной нет!")
    
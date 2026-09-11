import math
import random

def pow_mod(a, x, p):
    if p == 0:
        raise ValueError("число p не может быть равным 0")
    
    res = 1
    onestep = a % p
    while x > 0:
        if x & 1:
            res = (onestep * res) % p
        onestep = pow(onestep, 2) % p
        x >>= 1
        
    return res

def test_ferma(n, k=100):
    
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False
    
    for i in range(k):
        a = random.randint(2, n - 2)
        
        r = pow_mod(a, n-1, n) # - формула r = a^(n-1) mod n
        if r != 1:
            return False
        
    return True

def euclid_gcd(a, b):
    
    u1, v1 = 1, 0
    u2, v2 = 0, 1
    
    while b != 0:
        q = a // b
        a, b = b, a % b
        
        u1, u2 = u2, u1 - q*u2
        v1, v2 = v2, v1 - q*v2
    
    return (a, u1, v1)

def baby_giant_step():
    print()
    print("Шаг младенца, шаг великана")
    print("Общий вид задачи: y = a^x mod p, x - ?")
    a, y, p = generate_num_two()
    print(f'Итоговый вид задачи: {y} = {a}^x mod {p}, x - ?')
    m = 2
    k = p // m + 1
    while k // m > 2:
        m *= 2
        k = p // m + 1
    m_res = []
    k_res = []
    print()
    print(f'm = {m} k = {k}')
    print()
    print(f'Шаги младенца (0 - {m}): (y * a^j) % p')
    for j in range(0, m):
        step_res = [j, (y * (a**j)) % p] # [номер, результат]
        print(f'Шаг №{j}: ({y} * {a}^{j}) % {p} = {step_res[1]}')
        m_res.append(step_res)
    print()
    print(f'Шаги великана (1): a^(i*m) % p')
    step_res = [1, pow_mod(a, 1*m, p)] # [номер, результат]
    print(f'Шаг №{1}: {a}^({1}*{m}) % {p} = {step_res[1]}')
    k_res.append(step_res)
    print(f'Шаги великана (2-{k}): k[i-1] * (a^(m) % p) % p')
    for i in range(2, k+1):
        prev = step_res[1]
        step_res = [i, prev * pow_mod(a, m, p) % p]
        # step_res = [i, pow_mod(a, i*m, p)]
        print(f'Шаг №{i}: {prev} * ({a}^({m}) % {p}) % {p} = {step_res[1]}')
        # print(f'Шаг №{i}: {a}^({i}*{m}) % {p} = {step_res[1]}')
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
                print(f'x = {giant[0]} * {m} - {baby[0]} = {x_val}')
                x_count += 1
                x_list.append([x_count, x_val])
                print()
    print("Ответ: ")
    if len(x_list) < 1:
        print("нет решения")
    elif len(x_list) > 1:
        for x in x_list:
            print(f'x{x[0]} = {x[1]}')
    else:
        print(f'x = {x_list[0][1]}')
        
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
import os
import hashlib
import random

from lab1_2 import pow_mod, euclid_gcd, generate_prime, test_ferma

FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')



def mod_inverse(a, m):
    g, u, v = euclid_gcd(a, m)
    if g != 1:
        return None
    return u % m


def file_hash(path, name='sha256'):
    with open(path, 'rb') as f:
        return hashlib.new(name, f.read()).digest()



def generate_keys_gost():

    while True:
        #(255, 1000] 
        q = generate_prime(257, 1000)

        # 2. b — чётное, чтобы p = b·q + 1 было нечётным
        b = random.randrange(2, 1000, 2)

        #(4.11): p = b·q + 1, не 1024 бита, иначе это безумие с 308 знаками, что в 300 раз больше 10^9, причем, если делать цельный q=256 бит как в методичке, 
        # то было бы идеально, т к sha256 дает тоже 256 бит которые идеально влезают за раз. НО, мы всеравно дробим эту дуру и шифруем каждый байт отдельно, уменьшая числа,
        # перебирать число p в 300 знаков через самописный pow_mod - это можно, НО НЕ ЧЕРЕЗ ГРЕБАНЫЙ ПИТОН, ведь изначально функция на C, для которого это все писалось
        # еще в советское время обычно считает это в 50 раз быстрее.
        p = b * q + 1

        if not test_ferma(p):
            continue

        #(4.12) a > 1, a^q mod p == 1 - опять же медленно(успех 1 к 1000) поэтому a^q = (g^b)^q
        g = random.randint(2, p - 2)
        a = pow_mod(g, b, p)
        if a <= 1:
            continue

        #Секретный ключ x: 0 < x < q
        x = random.randint(1, q - 1)

        #(4.13) Открытый ключ y = a^x mod p
        y = pow_mod(a, x, p)

        return p, q, a, x, y




def sign_file_gost(in_path, sig_path, p, q, a, x):
    h_m = file_hash(in_path)
    block_q = (q.bit_length() + 7) // 8

    signature = bytearray()

    for h in h_m:
        if h == 0:
            h = 1# условие 0 < h < q: 0 недопустим


        while True: #пока r и s не станут != 0
            #шаг 2
            k = random.randint(1, q - 1)
            #шаг 3
            r = pow_mod(a, k, p) % q
            if r == 0:
                continue
            #шаг 4
            s = (k * h + x * r) % q
            if s == 0:
                continue

            break

        #<m; r, s>
        signature += r.to_bytes(block_q, 'big')
        signature += s.to_bytes(block_q, 'big')

    with open(sig_path, 'wb') as f:
        f.write(signature)

    print(f"Файл подписан (ГОСТ Р 34.10-94). Хеш: {h_m.hex()}")
    print(f"Подпись сохранена в: {sig_path}")




def verify_file_gost(in_path, sig_path, p, q, a, y):
    with open(sig_path, 'rb') as f:
        sig_data = f.read()

    block_q = (q.bit_length() + 7) // 8
    expected_len = 32 * 2 * block_q

    if len(sig_data) != expected_len:
        print("Ошибка! Неверный размер файла подписи.")
        return False

    h_m = file_hash(in_path)

    for i, h in enumerate(h_m):
        if h == 0:
            h = 1


        start = i * 2 * block_q
        r = int.from_bytes(sig_data[start:start + block_q], 'big')
        s = int.from_bytes(sig_data[start + block_q:start + 2 * block_q], 'big')

        # Шаг 2: проверяем 0 < r < q и 0 < s < q
        if not (0 < r < q and 0 < s < q):
            print(f"Ошибка! Нарушено 0 < r, s < q на байте {i}.")
            return False

        # Шаг 3: u1 = s·h^{-1} mod q, u2 = -r·h^{-1} mod q
        h_inv = mod_inverse(h, q)
        if h_inv is None:
            print(f"Ошибка! НОД(h, q) != 1 на байте {i}.")
            return False

        u1 = (s * h_inv) % q
        u2 = (-r * h_inv) % q

        # Шаг 4: v = ((a^u1 * y^u2 mod p) mod q)
        v = (pow_mod(a, u1, p) * pow_mod(y, u2, p)) % p
        v = v % q

        # Шаг 5: v == r
        if v != r:
            print(f"Ошибка проверки! v ≠ r на байте {i}.")
            return False

    print(f"Хеш файла: {h_m.hex()}")
    print("Все байты прошли проверку по ГОСТ Р 34.10-94.")
    return True




def main():
    print("Электронная подпись ГОСТ Р 34.10-94")

    print("Генерация ключей...")
    p, q, a, x, y = generate_keys_gost()
    print(f"Общие параметры: p = {p}")
    print(f"Общие параметры: q = {q}")
    print(f"Общие параметры: a = {a}")
    print(f"Открытый ключ: y = {y}")
    print(f"Секретный ключ: x = {x}")

    if not os.path.exists(FILES_DIR):
        os.makedirs(FILES_DIR)

    while True:
        print("\n   Меню    ")
        print("1. Подписать файл")
        print("2. Проверить подпись")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == '0':
            break
        elif choice not in ('1', '2'):
            continue

        in_filename = input("Имя исходного файла: ").strip()
        in_path = os.path.join(FILES_DIR, in_filename)

        if not os.path.exists(in_path):
            print(f"Ошибка! Файл {in_path} не найден.")
            continue

        if choice == '1':
            sig_filename = input("Имя файла подписи: ").strip()
            sig_path = os.path.join(FILES_DIR, sig_filename)
            sign_file_gost(in_path, sig_path, p, q, a, x)
        elif choice == '2':
            sig_filename = input("Имя файла подписи: ").strip()
            sig_path = os.path.join(FILES_DIR, sig_filename)
            if not os.path.exists(sig_path):
                print("Файл подписи не найден.")
                continue
            is_valid = verify_file_gost(in_path, sig_path, p, q, a, y)
            if is_valid:
                print("ПОДПИСЬ ВЕРНА (True)")
            else:
                print("ПОДПИСЬ НЕВЕРНА (False)")


if __name__ == "__main__":
    main()
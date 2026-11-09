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
        data = f.read()
    return hashlib.new(name, data).digest()



def generate_keys_gost():

    q = generate_prime(2**255, 2**256 - 1)


    while True:
        b = random.randint(2**767, 2**768 - 1)
        b = b | 1
        b += 1
        p = b * q + 1
        
        if not test_ferma(p):
            continue

        # a = g^b mod p
        while True:
            g = random.randint(2, p - 2)
            a = pow_mod(g, b, p)
            if a > 1:
                break

        x = random.randint(1, q - 1)
        y = pow_mod(a, x, p)

        return p, q, a, x, y



def file_hash_int(path):
    return int.from_bytes(file_hash(path), 'big')



def sign_file_gost(in_path, sig_path, p, q, a, x):
    h = file_hash_int(in_path)

    if h >= q:
        h = h % q
    if h == 0:
        h = 1

    while True:
        k = random.randint(1, q - 1)
        r = pow_mod(a, k, p) % q
        if r == 0:
            continue
        s = (k * h + x * r) % q
        if s == 0:
            continue
        break

    signature = r.to_bytes(32, 'big') + s.to_bytes(32, 'big')

    with open(sig_path, 'wb') as f:
        f.write(signature)

    print(f"Файл подписан. Хеш: {h:064x}")
    print(f"Подпись сохранена в: {sig_path}")



def verify_file_gost(in_path, sig_path, p, q, a, y):
    with open(sig_path, 'rb') as f:
        sig_data = f.read()

    if len(sig_data) != 64:
        print("Ошибка! Неверный размер файла подписи.")
        return False

    r = int.from_bytes(sig_data[:32], 'big')
    s = int.from_bytes(sig_data[32:], 'big')

    h = file_hash_int(in_path)
    if h >= q:
        h = h % q
    if h == 0:
        h = 1

    if not (0 < r < q and 0 < s < q):
        print("Ошибка! Нарушено 0 < r, s < q.")
        return False

    h_inv = mod_inverse(h, q)
    if h_inv is None:
        print("Ошибка! НОД(h, q) ≠ 1.")
        return False

    u1 = (s * h_inv) % q
    u2 = (-r * h_inv) % q

    v = (pow_mod(a, u1, p) * pow_mod(y, u2, p)) % p
    v = v % q

    if v != r:
        print("Ошибка проверки! v ≠ r.")
        return False

    print(f"Хеш: {h:064x}")
    print("Подпись верна.")
    return True



def main():
    print("ГОСТ Р 34.10-94")
    
    p, q, a, x, y = generate_keys_gost()
    print(f"\np = {p}")
    print(f"q = {q}")
    print(f"a = {a}")
    print(f"Открытый ключ y = {y}")
    print(f"Секретный ключ x = {x}")

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
            ok = verify_file_gost(in_path, sig_path, p, q, a, y)
            print("ПОДПИСЬ ВЕРНА" if ok else "ПОДПИСЬ НЕВЕРНА")


if __name__ == "__main__":
    main()
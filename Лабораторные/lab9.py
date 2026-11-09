import os
import hashlib
import random

from lab1_2 import pow_mod, euclid_gcd, generate_prime

FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')

def find_mod_inverse(a, m):
    g, u, v = euclid_gcd(a, m)
    if g != 1:
        return None
    return u % m

def file_hash(path, name='sha256'):
    with open(path, 'rb') as f:
        data = f.read()
    return hashlib.new(name, data).digest()


def generate_keys_elgamal():

    lo = 2 ** 31
    hi = 2 ** 32 - 1
    p = generate_prime(lo, hi)

    g = random.randint(2, p - 2)

    x = random.randint(2, p - 2)

    #(4.4): y = g^x mod p
    y = pow_mod(g, x, p)

    return p, g, y, x



def sign_file_elgamal(in_path, sig_path, p, g, x):
    h_m = file_hash(in_path)

    signature = bytearray()
    block_size = (p.bit_length() + 7) // 8

    for h in h_m:
        while True:
            k = random.randint(2, p - 2)
            if euclid_gcd(k, p - 1)[0] == 1:
                break

        #(4.5): r = g^k mod p
        r = pow_mod(g, k, p)

        #(4.6): u = (h - x*r) mod (p - 1)
        u = (h - x * r) % (p - 1)

        #(4.8): k^-1
        k_inv = find_mod_inverse(k, p - 1)

        #(4.7): s = k^-1 * u mod (p - 1)
        s = (k_inv * u) % (p - 1)

        #<m, r, s>
        signature += r.to_bytes(block_size, 'big')
        signature += s.to_bytes(block_size, 'big')

    with open(sig_path, 'wb') as f:
        f.write(signature)

    print(f"Файл подписан. Хеш h: {h_m.hex()}")
    print(f"Подпись сохранена в: {sig_path}")


def verify_file_elgamal(in_path, sig_path, p, g, y):
    with open(sig_path, 'rb') as f:
        sig_data = f.read()

    block_size = (p.bit_length() + 7) // 8

    expected_len = 32 * 2 * block_size

    if len(sig_data) != expected_len:
        print("Ошибка! Неверный размер файла подписи.")
        return False

    h_m = file_hash(in_path)

    for i in range(32):
        h = h_m[i]


        start = i * 2 * block_size
        r = int.from_bytes(sig_data[start:start + block_size], 'big')
        s = int.from_bytes(sig_data[start + block_size:start + 2 * block_size], 'big')

        #(4.10): y^r * r^s = g^h mod p
        left = (pow_mod(y, r, p) * pow_mod(r, s, p)) % p
        right = pow_mod(g, h, p)

        if left != right:
            print(f"Ошибка проверки! Байт {i} не прошел.")
            return False

    print(f"Хеш файла h(m): {h_m.hex()}")
    return True


def main():
    print("Электронная подпись Эль-Гамаля")

    p, g, y, x = generate_keys_elgamal()
    print(f"Открытый ключ: p = {p}")
    print(f"Открытый ключ: g = {g}")
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

        in_filename = input("Введите имя исходного файла: ").strip()
        in_path = os.path.join(FILES_DIR, in_filename)

        if not os.path.exists(in_path):
            print(f"Ошибка! Файл {in_path} не найден.")
            continue

        if choice == '1':
            sig_filename = input("Имя файла для подписи: ").strip()
            sig_path = os.path.join(FILES_DIR, sig_filename)
            sign_file_elgamal(in_path, sig_path, p, g, x)
        elif choice == '2':
            sig_filename = input("Имя файла подписи: ").strip()
            sig_path = os.path.join(FILES_DIR, sig_filename)
            if not os.path.exists(sig_path):
                print("Файл подписи не найден.")
                continue

            is_valid = verify_file_elgamal(in_path, sig_path, p, g, y)
            if is_valid:
                print("ПОДПИСЬ ВЕРНА (True)")
            else:
                print("ПОДПИСЬ НЕВЕРНА (False)")

if __name__ == "__main__":
    main()
import random
import os

from lab1_2 import pow_mod, test_ferma, euclid_gcd, generate_prime
FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')



def mod_inverse(a, m):
    g, u, v = euclid_gcd(a, m)
    if g != 1:
        return None
    return u % m


def generate_params():
    lo = 2 ** 31
    hi = 2 ** 32 - 1

    while True:
        p = generate_prime(lo, hi)
        q = generate_prime(lo, hi)
        if p == q:
            continue

        N_B = p * q
        phi = (p - 1) * (q - 1)

        d_B = None
        for c in (65537, 17, 5, 3):
            if 1 < c < phi and euclid_gcd(c, phi)[0] == 1:
                d_B = c
                break
        if d_B is None:
            while True:
                d_B = random.randint(2, phi - 1)
                if euclid_gcd(d_B, phi)[0] == 1:
                    break

        c_B = mod_inverse(d_B, phi)
        if c_B is None:
            continue

        print(f"p   = {p}")
        print(f"q   = {q}")
        print(f"N_B = {N_B}")
        print(f"φ   = {phi}")
        print(f"d_B = {d_B}")
        print(f"c_B = {c_B}")

        return p, q, N_B, d_B, c_B

def rsa_encrypt_block(m, d_B, N_B):
    
    e = pow_mod(m, d_B, N_B)
    return e

def rsa_decrypt_block(e, c_B, N_B):
    
    m_prime = pow_mod(e, c_B, N_B)
    return m_prime



def process_file(in_path, out_path, N_B, d_B, c_B, decrypt=False):
    with open(in_path, 'rb') as f:
        raw = f.read()


    read_block_size = (N_B.bit_length() - 1) // 8
    if read_block_size < 1:
        read_block_size = 1
        
    num_block_size = (N_B.bit_length() + 7) // 8

    write_block_size = num_block_size

    if decrypt:
        orig_len = int.from_bytes(raw[:8], 'big')
        data = raw[8:]
        in_block_size = write_block_size
        out_block_size = read_block_size
    else:
        orig_len = len(raw)
        data = raw
        in_block_size = read_block_size
        out_block_size = write_block_size

    pad = (-len(data)) % in_block_size
    data += b'\x00' * pad

    out = bytearray()

    for i in range(0, len(data), in_block_size):
        chunk = data[i:i + in_block_size]

        if decrypt:
            e = int.from_bytes(chunk, 'big')
            m_prime = rsa_decrypt_block(e, c_B, N_B)
            out.extend(m_prime.to_bytes(out_block_size, 'big'))
        else:
            m = int.from_bytes(chunk, 'big')
            e = rsa_encrypt_block(m, d_B, N_B)
            out.extend(e.to_bytes(num_block_size, 'big'))

    if decrypt:
        out = out[:orig_len]
    else:
        header = orig_len.to_bytes(8, 'big')
        out = header + out

    with open(out_path, 'wb') as f:
        f.write(out)


def input_params():
    while True:
        try:
            p = int(input("Введите простое число p: "))
            if p > 2 and test_ferma(p):
                break
            print("p должно быть простым и > 2.")
        except ValueError:
            print("Некорректное число.")

    while True:
        try:
            q = int(input("Введите простое число q (q != p): "))
            if q <= 2:
                print("q должно быть > 2.")
                continue
            if q == p:
                print("q должно отличаться от p.")
                continue
            if not test_ferma(q):
                print("q должно быть простым.")
                continue
            break
        except ValueError:
            print("Некорректное число.")

    N_B = p * q
    phi = (p - 1) * (q - 1)
    print(f"N_B = {N_B}")
    print(f"φ(N_B) = {phi}")

    while True:
        try:
            d_B = int(input("Введите d_B (1 < d_B < φ(N_B), gcd(d_B, φ(N_B)) = 1): "))
            if not (1 < d_B < phi):
                print(f"d_B должно быть в диапазоне (1, {phi}).")
                continue
            if euclid_gcd(d_B, phi)[0] != 1:
                print("gcd(d_B, φ(N_B)) должен быть равен 1.")
                continue
            break
        except ValueError:
            print("Некорректное число.")

    c_B = mod_inverse(d_B, phi)
    if c_B is None:
        print("Не удалось вычислить c_B.")
        return input_params()

    print(f"c_B = {c_B}")
    return p, q, N_B, d_B, c_B


def main():
    print("=== Шифр RSA ===")

    while True:
        try:
            mode = int(input("Ввод с клавиатуры (1) / Генерация (2): "))
            if mode in (1, 2):
                break
        except ValueError:
            pass
        print("Введите 1 или 2.")

    if mode == 1:
        p, q, N_B, d_B, c_B = input_params()
    else:
        p, q, N_B, d_B, c_B = generate_params()

    while True:
        try:
            action = int(input("\nШифровать (1) / Расшифровать (2) / Выход (0): "))
        except ValueError:
            print("Введите 1, 2 или 0.")
            continue

        if action == 0:
            print("Выход.")
            break

        if action not in (1, 2):
            print("Введите 1, 2 или 0.")
            continue

        in_filename = input("Входной файл: ").strip()
        out_filename = input("Выходной файл: ").strip()
        in_path = os.path.join(FILES_DIR, in_filename)
        out_path = os.path.join(FILES_DIR, out_filename)

        if not os.path.exists(in_path):
            print("Файл не найден.")
            continue

        try:
            process_file(in_path, out_path, N_B, d_B, c_B, decrypt=(action == 2))
            print("Обработка завершена!")
        except Exception as ex:
            print(f"Ошибка при обработке файла: {ex}")


if __name__ == "__main__":
    main()


import random
import os

from lab1_2 import pow_mod, test_ferma, euclid_gcd, generate_prime

FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')

def prime_factors(n):
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors

def is_primitive_root(g, p, factors):
    if g <= 1 or g >= p:
        return False

    for q in factors:
        if pow_mod(g, (p - 1) // q, p) == 1:
            return False
    return True

def find_primitive_root(p):
    factors = prime_factors(p - 1)
    while True:
        g = random.randint(2, p - 2)
        if is_primitive_root(g, p, factors):
            return g

def generate_params():
    p = generate_prime(2 ** 31, 2 ** 32 - 1)
    g = find_primitive_root(p)

    while True:
        Cb = random.randint(2, p - 2) # 1 < Cb < p-1
        if euclid_gcd(Cb, p - 1)[0] == 1:
            break

    Db = pow_mod(g, Cb, p)

    print(f"p  = {p}")
    print(f"g  = {g}")
    print(f"Cb = {Cb}  (закрытый ключ)")
    print(f"Db = {Db}  (открытый ключ)")

    return p, g, Cb, Db

def elgamal_encrypt_block(m, p, g, Db):
    k = random.randint(1, p - 2)
    r = pow_mod(g, k, p)
    e = (m * pow_mod(Db, k, p)) % p
    return r, e

def elgamal_decrypt_block(r, e, p, Cb):

    return (e * pow_mod(r, p - 1 - Cb, p)) % p



def process_file(in_path, out_path, p, g, Cb, Db, decrypt=False):
    with open(in_path, 'rb') as f:
        raw = f.read()


    read_block_size = (p.bit_length() - 1) // 8
    if read_block_size < 1:
        read_block_size = 1
        
    num_block_size = (p.bit_length() + 7) // 8

    write_block_size = 2 * num_block_size #т к пара чисел

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
            a = int.from_bytes(chunk[:num_block_size], 'big')
            b = int.from_bytes(chunk[num_block_size:], 'big')
            m = elgamal_decrypt_block(a, b, p, Cb)
            out.extend(m.to_bytes(out_block_size, 'big'))
        else:
            m = int.from_bytes(chunk, 'big')
            a, b = elgamal_encrypt_block(m, p, g, Db)
            out.extend(a.to_bytes(num_block_size, 'big'))
            out.extend(b.to_bytes(num_block_size, 'big'))

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

    factors = prime_factors(p - 1)

    while True:
        try:
            g = int(input("Введите g (1 < g < p): "))
            if not (1 < g < p):
                print("g должно быть в диапазоне (1, p).")
                continue
            if not is_primitive_root(g, p, factors):
                print("Внимание: g не является первообразным корнем по модулю p.")
                ans = input("Продолжить с этим g? (y/n): ").strip().lower()
                if ans != 'y':
                    continue
            break
        except ValueError:
            print("Некорректное число.")

    while True:
        try:
            Cb = int(input("Введите Cb (1 < Cb < p-1, gcd(Cb, p-1)=1): "))
            if not (1 < Cb < p - 1):
                print("Cb должно быть в диапазоне (1, p-1).")
                continue
            if euclid_gcd(Cb, p - 1)[0] != 1:
                print("gcd(Cb, p-1) должен быть равен 1.")
                continue
            break
        except ValueError:
            print("Некорректное число.")

    Db = pow_mod(g, Cb, p)
    print(f"Db = {Db}  (открытый ключ)")

    return p, g, Cb, Db


def main():
    print("=== Шифр Эль-Гамаля ===")

    while True:
        try:
            mode = int(input("Ввод с клавиатуры (1) / Генерация (2): "))
            if mode in (1, 2):
                break
        except ValueError:
            pass
        print("Введите 1 или 2.")

    if mode == 1:
        p, g, Cb, Db = input_params()
    else:
        p, g, Cb, Db = generate_params()

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
            process_file(in_path, out_path, p, g, Cb, Db, decrypt=(action == 2))
            print("Обработка завершена!")
        except Exception as e:
            print(f"Ошибка при обработке файла: {e}")


if __name__ == "__main__":
    main()
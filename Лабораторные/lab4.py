import random
import os

from lab1_2 import pow_mod, test_ferma, euclid_gcd, generate_prime

FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')

def modinv(a, m):
    g, u, v = euclid_gcd(a, m)
    if g != 1:
        return None
    return u % m

def generate_CD(p):
    while True:
        C = random.randint(2, p - 2)
        g, _, _ = euclid_gcd(C, p - 1)
        if g != 1:
            continue
        D = modinv(C, p - 1)
        if D is None or D < 2:
            continue
        return C, D

def Shamir_encrypt(m, p, Ca, Cb, Da, Db):
    x1 = pow_mod(m, Ca, p)
    x2 = pow_mod(x1, Cb, p)
    return x2

def Shamir_decrypt(m, p, Ca, Cb, Da, Db):
    x1 = pow_mod(m, Da, p)
    x2 = pow_mod(x1, Db, p)
    return x2

def process_file(in_path, out_path, p, Ca, Cb, Da, Db, decrypt=False):
    with open(in_path, 'rb') as f:
        raw = f.read()


    read_block_size = (p.bit_length() - 1) // 8
    if read_block_size < 1:
        read_block_size = 1
        
    write_block_size = (p.bit_length() + 7) // 8

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

    blocks = []
    for i in range(0, len(data), in_block_size):
        chunk = data[i:i + in_block_size]
        m = int.from_bytes(chunk, 'big')
        blocks.append(m)

    out_blocks = []
    for m in blocks:
        if decrypt:
            out_blocks.append(Shamir_decrypt(m, p, Ca, Cb, Da, Db))
        else:
            out_blocks.append(Shamir_encrypt(m, p, Ca, Cb, Da, Db))

    out = bytearray()
    for b in out_blocks:
        out.extend(b.to_bytes(out_block_size, 'big'))

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
            Ca = int(input(f"Введите Ca (gcd(Ca, p-1)=1, 2<=Ca<={p-2}): "))
            Cb = int(input(f"Введите Cb (gcd(Cb, p-1)=1, 2<=Cb<={p-2}): "))

            if not (2 <= Ca <= p - 2) or not (2 <= Cb <= p - 2):
                print("Ca и Cb должны быть в диапазоне [2, p-2].")
                continue

            g1, _, _ = euclid_gcd(Ca, p - 1)
            g2, _, _ = euclid_gcd(Cb, p - 1)
            if g1 != 1 or g2 != 1:
                print("gcd(Ca, p-1) и gcd(Cb, p-1) должны быть равны 1.")
                continue
            break
        except ValueError:
            print("Некорректное число.")

    Da = modinv(Ca, p - 1)
    Db = modinv(Cb, p - 1)

    print(f"Da = {Da}")
    print(f"Db = {Db}")

    return p, Ca, Cb, Da, Db


def generate_params():

    p = generate_prime(2 ** 31, 2 ** 32 - 1)

    Ca, Da = generate_CD(p)
    Cb, Db = generate_CD(p)

    print(f"p  = {p}")
    print(f"Ca = {Ca}, Da = {Da}")
    print(f"Cb = {Cb}, Db = {Db}")

    return p, Ca, Cb, Da, Db



def main():
    print("=== Шифр Шамира ===")

    while True:
        mode = int(input("Ввод с клавиатуры (1) / Генерация (2): "))
        if mode in (1, 2):
            break

    if mode == 1:
        p, Ca, Cb, Da, Db = input_params()
    else:
        p, Ca, Cb, Da, Db = generate_params()

    while True:
        action = int(input("\nШифровать (1) / Расшифровать (2) / Выход (0): "))

        if action == 0:
            print("Выход.")
            break

        if action not in (1, 2):
            print("Введите 1, 2 или 0.")
            continue

        in_filename = input("Входной файл: ").strip()
        out_filename = input("Выходной файл: ").strip()
        in_path = f'{FILES_DIR}\{in_filename}'
        out_path = f'{FILES_DIR}\{out_filename}'

        if not os.path.exists(in_path):
            print("Файл не найден.")
            continue

        process_file(in_path, out_path, p, Ca, Cb, Da, Db, decrypt=(action == 2))
        print("Обработка завершена!")


if __name__ == "__main__":
    main()
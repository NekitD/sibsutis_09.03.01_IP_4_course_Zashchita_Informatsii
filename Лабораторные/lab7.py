import random
import os
import hashlib

from lab1_2 import pow_mod, test_ferma, euclid_gcd, generate_prime
FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')


#основа это (X xor Y) xor Y = X

def diffie_hellman(p, g, Xa, Xb):
    if not test_ferma(p):
        raise ValueError(f"p = {p} не является простым числом")

    if not (1 < g < p - 1):
        raise ValueError(f"g = {g} вне диапазона (1, {p - 1})")

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
    Zb = pow_mod(Ya, Xb, p)

    return Za, Zb, Ya, Yb


def generate_dh_params():
    lo = 2 ** 31
    hi = 2 ** 32 - 1

    while True:
        p = generate_prime(lo, hi)
        q = (p - 1) // 2
        if test_ferma(q):
            break

    while True:
        g = random.randint(2, p - 2)
        if pow_mod(g, 2, p) != 1 and pow_mod(g, q, p) != 1:
            break

    print(f"p = {p}")
    print(f"g = {g}")
    return p, g


def derive_key_from_secret(secret, key_len_bytes):

    if secret <= 0:
        raise ValueError("Отрицательный секрет.")

    key = b'' #байтовая строка
    counter = 0 #для разнообразия генерации
    secret_bytes = secret.to_bytes((secret.bit_length() + 7) // 8, 'big')

    while len(key) < key_len_bytes:
        h = hashlib.sha256(secret_bytes + counter.to_bytes(4, 'big')).digest()
        key += h #доб.в строку
        counter += 1 #снова задаем смещения чтобы блоки не повторялись

    return key[:key_len_bytes]


def vernam_crypt(data: bytes, key: bytes):
    result = bytearray()
    for i in range(len(data)):
        result.append(data[i] ^ key[i])
    return bytes(result)


def process_file(in_path, out_path, key, decrypt=False):

    with open(in_path, 'rb') as f:
        raw = f.read()

    if decrypt:
        orig_len = int.from_bytes(raw[:8], 'big')
        data = raw[8:]

        if len(key) < len(data):
            raise ValueError("Ключ короче зашифрованных данных. Расшифрование невозможно.")

        out = vernam_crypt(data, key[:len(data)])
        out = out[:orig_len]
    else:
        if len(key) < len(raw):
            raise ValueError("Ключ короче исходных данных. Шифрование невозможно")

        out = vernam_crypt(raw, key[:len(raw)]) #обрезаем ключ, чтобы не был меньше или больше файла
        out = len(raw).to_bytes(8, 'big') + out

    with open(out_path, 'wb') as f:
        f.write(out)
        
def input_dh_params():
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
            g = int(input("Введите первообразный корень g (1 < g < p-1): "))
            if 1 < g < p - 1:
                break
            print("g должно быть в диапазоне (1, p-1).")
        except ValueError:
            print("Некорректное число.")

    return p, g


def input_secret(p, name="A"):
    while True:
        try:
            x = int(input(f"Введите секретный ключ X{name} (2 <= X{name} <= {p-2}): "))
            if 2 <= x <= p - 2:
                return x
            print("Некорректное значение.")
        except ValueError:
            print("Некорректное число.")

def main():
    print("=== Шифр Вернама ===")

    while True:
        try:
            mode = int(input("Ввод параметров вручную (1) / Генерация (2): "))
            if mode in (1, 2):
                break
        except ValueError:
            pass
        print("Введите 1 или 2.")

    if mode == 1:
        p, g = input_dh_params()
    else:
        p, g = generate_dh_params()

    if mode == 1:
        Xa = input_secret(p, "A")
        Xb = input_secret(p, "B")
    else:
        Xa = random.randint(2, p - 2)
        Xb = random.randint(2, p - 2)
        print(f"Xa = {Xa}")
        print(f"Xb = {Xb}")

    try:
        Za, Zb, Ya, Yb = diffie_hellman(p, g, Xa, Xb)
    except ValueError as ex:
        print(f"Ошибка Диффи-Хеллмана: {ex}")
        return

    print(f"Ya = {Ya}")
    print(f"Yb = {Yb}")
    print(f"Za = {Za}")
    print(f"Zb = {Zb}")

    if Za != Zb:
        print("Ошибка: общие секреты не совпадают!")
        return

    shared = Za
    print(f"Общий секрет = {shared}")

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

        file_size = os.path.getsize(in_path)
        key_len = file_size if action == 1 else max(1, file_size - 8)

        key = derive_key_from_secret(shared, key_len) #генерируем двоичное число из Z по размеру файла

        try:
            process_file(in_path, out_path, key, decrypt=(action == 2))
            print("Обработка завершена!")
        except Exception as ex:
            print(f"Ошибка при обработке файла: {ex}")


if __name__ == "__main__":
    main()

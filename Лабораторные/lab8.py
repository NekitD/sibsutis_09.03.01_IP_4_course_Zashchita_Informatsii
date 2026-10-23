import os
import hashlib
import random

#хеш всегда меньше N - иначе проверка упадет(хеш обрежется)
#поэтому предлагают его резать на куски: т к sha-256 это 256 бит(32байта), а число N = p·q (p,q ≈ 2³²) = ~63бита

from lab1_2 import pow_mod, euclid_gcd, generate_prime

FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')

def find_mod_inverse(a, m): #cd mod phi = 1
    g, u, v = euclid_gcd(a, m)
    if g != 1:
        return None
    return u % m

def generate_keys():
    
    a = 2 ** 31
    b = 2 ** 32 - 1

    while True:
        P = generate_prime(a, b)
        Q = generate_prime(a, b)
        if P == Q:
            continue
        
        N = P * Q #2.28
        
        phi = (P - 1) * (Q - 1) 

        a_d = 2 ** 16 + 1 #берем поменьше d < phi
        b_d = min(2 ** 20, phi - 1)

        if a_d >= b_d:
            a_d, b_d = 3, phi - 1

        d = None
        for _ in range(10000):
            cand = random.randint(a_d, b_d)
            if euclid_gcd(cand, phi)[0] == 1:
                d = cand
                break

        if d is None:
            while True:
                d = random.randint(3, phi - 1)
                if euclid_gcd(d, phi)[0] == 1:
                    break

        # c из формулы cd mod phi = 1
        c = find_mod_inverse(d, phi)
        if c is None:
            continue

        return N, d, c
 
def file_hash(path, name='sha256'):
    with open(path, 'rb') as f:
        data = f.read()
    return hashlib.new(name, data).digest()
    

def sign_file(in_path, sig_path, N, c):
    
    y_bytes = file_hash(in_path)
    
    block_size = (N.bit_length() + 7) // 8
    signature = bytearray()
    

    for yi in y_bytes: #по каждому байту хеша
        #4.1: s = y^c mod N
        s = pow_mod(yi, c, N)
        signature += s.to_bytes(block_size, 'big')


    with open(sig_path, 'wb') as f:
        f.write(signature)

    print(f"Файл подписан. Хеш (y): {y_bytes.hex()}")
    print(f"Подпись сохранена в: {sig_path}")


def verify_file(in_path, sig_path, N, d):
    
    with open(sig_path, 'rb') as f:
        sig_data = f.read()

    block_size = (N.bit_length() + 7) // 8
    expected_len = 32 * block_size # 32 байта хеша * размер блока

    if len(sig_data) != expected_len:
        print("Ошибка! Неверный размер файла подписи.")
        return False


    w_bytes = bytearray()
    for start in range(0, len(sig_data), block_size): # идём по блокам
        s = int.from_bytes(sig_data[start:start + block_size], 'big')
        w_val = pow_mod(s, d, N) #4.3: w = s^d mod N
        if w_val > 255:
            print("Ошибка проверки! Подпись повреждена.")
            return False
        w_bytes.append(w_val)

    h_m = file_hash(in_path)

    print(f"Восстановленный хеш (w): {w_bytes.hex()}")
    print(f"Хеш файла: {h_m.hex()}")

    return w_bytes == h_m


def main():
    print(" Электронная подпись RSA ")
    

    print("Генерация ключей...")
    N, d, c = generate_keys()
    print(f"Открытый ключ: N = {N}")
    print(f"Открытая степень: d = {d}")
    print(f"Секретная степень: c = {c}")


    if not os.path.exists(FILES_DIR):
        os.makedirs(FILES_DIR)

    while True:
        print("\n   Меню    ")
        print("1.Подписать файл")
        print("2.Проверить подпись")
        print("0.Выход")
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
            sign_file(in_path, sig_path, N, c)
            
        elif choice == '2':
            sig_filename = input("Имя файла подписи: ").strip()
            sig_path = os.path.join(FILES_DIR, sig_filename)
            if not os.path.exists(sig_path):
                print("Файл подписи не найден.")
                continue
                
            is_valid = verify_file(in_path, sig_path, N, d)
            if is_valid:
                print("ПОДПИСЬ ВЕРНА (True)")
            else:
                print("ПОДПИСЬ НЕВЕРНА (False)")


if __name__ == "__main__":
    main()




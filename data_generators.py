import random

def gerar_usuario():
    qtd = random.randint(6, 8)
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(random.choices(chars, k=qtd))

def gerar_numero():
    return "219" + ''.join(random.choices("0123456789", k=7))

def gerar_senha():
    return "222221"

def gerar_senha_original():
    return "wAadg234@23aA"

def gerar_nome():
    qtd = random.randint(5, 7)
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join(random.choices(chars, k=qtd))

def gerar_cpf():
    return ''.join(random.choices("0123456789", k=11))

def gerar_email_uorak():
    qtd = random.randint(5, 7)
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(random.choices(chars, k=qtd)) + "@uorak.com"

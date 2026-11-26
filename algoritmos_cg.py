import math

# =============================================================================
# UTILITÁRIOS
# =============================================================================

def arredondar(valor):
    return int(math.floor(valor + 0.5))


def _criar_plotter(sup, cor):
    pontos = []
    if sup is None:
        def liga_pixel(x, y):
            pontos.append((x, y))
    else:
        largura, altura = sup.get_size()
        set_at = sup.set_at

        def liga_pixel(x, y):
            pontos.append((x, y))
            if 0 <= x < largura and 0 <= y < altura:
                set_at((x, y), cor)
    return liga_pixel, pontos


def _ponto_int(x, y):
    return arredondar(x), arredondar(y)


# =============================================================================
# 1. RASTERIZAÇÃO DE LINHAS
# =============================================================================

def linha_bresenham(sup, x1, y1, x2, y2, cor=None):
    liga_pixel, pontos = _criar_plotter(sup, cor)
    x1, y1 = _ponto_int(x1, y1)
    x2, y2 = _ponto_int(x2, y2)

    # Regra 3: reta íngreme -> troca x com y
    troca_xy = abs(y2 - y1) > abs(x2 - x1)
    if troca_xy:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Regra 1: x2 < x1 -> troca P1 com P2
    trocou_pontos = x2 < x1
    if trocou_pontos:
        x1, x2 = x2, x1
        y1, y2 = y2, y1

    # Regra 2: y2 < y1 -> espelha y (y <- -y)
    espelha_y = y2 < y1
    if espelha_y:
        y1, y2 = -y1, -y2

    # Núcleo do 1º octante
    dx = x2 - x1
    dy = y2 - y1
    y = y1
    p = (dy << 1) - dx                 # p0 = 2*dy - dx
    inc_e = dy << 1                    # 2*dy           (pixel E)
    inc_ne = (dy - dx) << 1            # 2*(dy - dx)    (pixel NE)

    for x in range(x1, x2 + 1):
        y_real = -y if espelha_y else y          # desfaz o espelhamento
        if troca_xy:
            liga_pixel(y_real, x)                # desfaz a troca x <-> y
        else:
            liga_pixel(x, y_real)
        if p >= 0:
            y += 1
            p += inc_ne
        else:
            p += inc_e

    if trocou_pontos:
        pontos.reverse()                         # mantém o sentido P1 -> P2
    return pontos


# =============================================================================
# 2. RASTERIZAÇÃO DE CIRCUNFERÊNCIA
# =============================================================================

def _liga_8_simetricos(liga_pixel, xc, yc, x, y):
    liga_pixel(x + xc, y + yc)
    liga_pixel(y + xc, x + yc)
    liga_pixel(-y + xc, x + yc)
    liga_pixel(-x + xc, y + yc)
    liga_pixel(-x + xc, -y + yc)
    liga_pixel(-y + xc, -x + yc)
    liga_pixel(y + xc, -x + yc)
    liga_pixel(x + xc, -y + yc)


def circunferencia_bresenham(sup, xc, yc, r, cor=None, p0_real=False):
    liga_pixel, pontos = _criar_plotter(sup, cor)
    xc, yc = _ponto_int(xc, yc)
    r = arredondar(r)

    x = 0
    y = r
    p = (5 / 4 - r) if p0_real else (1 - r)

    while x <= y:
        _liga_8_simetricos(liga_pixel, xc, yc, x, y)
        if p >= 0:
            p = p + 2 * x - 2 * y + 5
            y = y - 1
        else:
            p = p + 2 * x + 3
        x = x + 1
    return pontos


# =============================================================================
# 3. PREENCHIMENTO DE ÁREAS
# =============================================================================

def montar_tabela_lados(vertices):
    tabela = []
    n = len(vertices)
    for i in range(n):
        xa, ya = vertices[i]
        xb, yb = vertices[(i + 1) % n]
        if ya == yb:
            continue                              # aresta horizontal: ignorada
        if ya < yb:
            y_min, y_max, x_ymin = ya, yb, xa
        else:
            y_min, y_max, x_ymin = yb, ya, xb
        inv_m = (xb - xa) / (yb - ya)
        tabela.append((y_min, y_max, x_ymin, inv_m))
    tabela.sort(key=lambda lado: (lado[0], lado[2]))
    return tabela


def intersecoes_varredura(tabela, y_varredura):
    xs = []
    for y_min, y_max, x_ymin, inv_m in tabela:
        if y_min > y_varredura:
            break                                 # tabela ordenada por Y_min
        if y_min <= y_varredura < y_max:
            xs.append(inv_m * (y_varredura - y_min) + x_ymin)
    xs.sort()
    return xs


def preencher_poligono_varredura(sup, vertices, cor=None):
    liga_pixel, pontos = _criar_plotter(sup, cor)
    tabela = montar_tabela_lados(vertices)
    if not tabela:
        return pontos

    y_ini = math.ceil(min(lado[0] for lado in tabela))
    y_fim = math.ceil(max(lado[1] for lado in tabela))   # Y_max é exclusivo

    for y in range(y_ini, y_fim):
        xs = intersecoes_varredura(tabela, y)
        contador = 0
        for i in range(len(xs) - 1):
            contador += 1
            if contador % 2 == 1:                 # ímpar: dentro do polígono
                x_ini = math.ceil(xs[i])          # primeiro pixel: pintado
                x_fim = math.ceil(xs[i + 1])      # último pixel: não pintado
                for x in range(x_ini, x_fim):
                    liga_pixel(x, y)
    return pontos


def preencher_retangulo(sup, x_min, y_min, x_max, y_max, cor=None):
    liga_pixel, pontos = _criar_plotter(sup, cor)
    x_min, y_min = _ponto_int(x_min, y_min)
    x_max, y_max = _ponto_int(x_max, y_max)
    for y in range(y_min, y_max + 1):
        for x in range(x_min, x_max + 1):
            liga_pixel(x, y)
    return pontos


def preencher_circunferencia(sup, xc, yc, r, cor=None):
    liga_pixel, pontos = _criar_plotter(sup, cor)
    xc, yc = _ponto_int(xc, yc)
    r = arredondar(r)
    for y in range(yc - r + 1, yc + r):
        raiz = math.sqrt(r * r - (y - yc) ** 2)
        x1 = arredondar(xc - raiz)
        x2 = arredondar(xc + raiz)
        for x in range(x1, x2 + 1):
            liga_pixel(x, y)
    return pontos


def desenhar_poligono(sup, vertices, cor=None, algoritmo_linha=None):
    if algoritmo_linha is None:
        algoritmo_linha = linha_bresenham
    pontos = []
    n = len(vertices)
    for i in range(n):
        xa, ya = vertices[i]
        xb, yb = vertices[(i + 1) % n]
        pontos.extend(algoritmo_linha(sup, xa, ya, xb, yb, cor))
    return pontos


# =============================================================================
# 4. RECORTE (CLIPPING)
# =============================================================================
# Janela de recorte: tupla (x_min, y_min, x_max, y_max).

# Código de região (Slide 76): b3 b2 b1 b0
ACIMA = 0b1000      # P(1): y > y_max
ABAIXO = 0b0100     # P(2): y < y_min
DIREITA = 0b0010    # P(3): x > x_max
ESQUERDA = 0b0001   # P(4): x < x_min


def recorte_ponto(x, y, janela):
    x_min, y_min, x_max, y_max = janela
    return x_min < x < x_max and y_min < y < y_max


def codigo_regiao(x, y, janela):
    x_min, y_min, x_max, y_max = janela
    codigo = 0
    if x < x_min:
        codigo |= ESQUERDA
    if x > x_max:
        codigo |= DIREITA
    if y < y_min:
        codigo |= ABAIXO
    if y > y_max:
        codigo |= ACIMA
    return codigo


def _bits(codigo):
    return [(codigo >> 3) & 1, (codigo >> 2) & 1, (codigo >> 1) & 1, codigo & 1]


def aceitacao_trivial(codigo1, codigo2):
    bits1, bits2 = _bits(codigo1), _bits(codigo2)
    soma = 0
    for i in range(4):
        soma = soma + bits1[i] + bits2[i]
    return soma == 0


def rejeicao_trivial(codigo1, codigo2):
    bits1, bits2 = _bits(codigo1), _bits(codigo2)
    for i in range(4):
        inter = bits1[i] + bits2[i]
        if inter == 2:
            return True
    return False


def cohen_sutherland(x1, y1, x2, y2, janela):
    x_min, y_min, x_max, y_max = janela
    c1 = codigo_regiao(x1, y1, janela)
    c2 = codigo_regiao(x2, y2, janela)

    while True:
        if aceitacao_trivial(c1, c2):
            return (x1, y1, x2, y2)
        if rejeicao_trivial(c1, c2):
            return None

        c_fora = c1 if c1 != 0 else c2
        vertical = (x2 == x1)
        M = None if vertical else (y2 - y1) / (x2 - x1)

        if c_fora & ACIMA:
            y = y_max
            x = x1 if (vertical or M == 0) else x1 + (1 / M) * (y_max - y1)
        elif c_fora & ABAIXO:
            y = y_min
            x = x1 if (vertical or M == 0) else x1 + (1 / M) * (y_min - y1)
        elif c_fora & DIREITA:
            x = x_max
            y = M * (x_max - x1) + y1
        else:  # ESQUERDA
            x = x_min
            y = M * (x_min - x1) + y1

        if c_fora == c1:
            x1, y1 = x, y
            c1 = codigo_regiao(x1, y1, janela)
        else:
            x2, y2 = x, y
            c2 = codigo_regiao(x2, y2, janela)


def _dentro_borda(px, py, borda, janela):
    x_min, y_min, x_max, y_max = janela
    if borda == "esquerda":
        return px >= x_min
    if borda == "direita":
        return px <= x_max
    if borda == "superior":
        return py <= y_max
    return py >= y_min                            # "inferior"


def _intersecao_borda(sx, sy, px, py, borda, janela):
    x_min, y_min, x_max, y_max = janela
    if borda in ("esquerda", "direita"):
        xb = x_min if borda == "esquerda" else x_max
        M = (py - sy) / (px - sx)                 # px != sx: a aresta cruza a borda
        return (xb, M * (xb - sx) + sy)
    yb = y_max if borda == "superior" else y_min
    if px == sx:                                  # aresta vertical
        return (sx, yb)
    M = (py - sy) / (px - sx)
    return (sx + (1 / M) * (yb - sy), yb)


def sutherland_hodgman(vertices, janela):
    saida = list(vertices)
    for borda in ("esquerda", "direita", "superior", "inferior"):
        entrada = saida
        saida = []
        if not entrada:
            break
        sx, sy = entrada[-1]                      # aresta de fechamento vn -> v1
        for px, py in entrada:
            s_dentro = _dentro_borda(sx, sy, borda, janela)
            p_dentro = _dentro_borda(px, py, borda, janela)
            if s_dentro and p_dentro:                         # Caso 1
                saida.append((px, py))
            elif s_dentro and not p_dentro:                   # Caso 2
                saida.append(_intersecao_borda(sx, sy, px, py, borda, janela))
            elif not s_dentro and p_dentro:                   # Caso 4
                saida.append(_intersecao_borda(sx, sy, px, py, borda, janela))
                saida.append((px, py))
            # Caso 3 (fora, fora): nada é adicionado
            sx, sy = px, py
    return saida


# =============================================================================
# 5. CURVAS DE BÉZIER E ALGORITMO DE CASTELJAU
# =============================================================================

def coeficiente_binomial(n, i):
    return math.factorial(n) // (math.factorial(i) * math.factorial(n - i))


def bernstein(i, n, t):
    return coeficiente_binomial(n, i) * (t ** i) * ((1 - t) ** (n - i))


def ponto_bezier(controles, t):
    n = len(controles) - 1
    x = 0.0
    y = 0.0
    for i, (xi, yi) in enumerate(controles):
        b = bernstein(i, n, t)
        x += b * xi
        y += b * yi
    return (x, y)


def subdividir_casteljau(controles):
    niveis = [list(controles)]
    atual = niveis[0]
    while len(atual) > 1:
        atual = [((atual[i][0] + atual[i + 1][0]) / 2,
                  (atual[i][1] + atual[i + 1][1]) / 2)
                 for i in range(len(atual) - 1)]
        niveis.append(atual)
    esquerda = [nivel[0] for nivel in niveis]
    direita = [nivel[-1] for nivel in reversed(niveis)]
    return esquerda, direita


def bezier_casteljau(sup, controles, cor=None, tolerancia=1.0,
                     profundidade_max=12, algoritmo_linha=None):
    if algoritmo_linha is None:
        algoritmo_linha = linha_bresenham
    pontos = []

    def recursao(ctrl, profundidade):
        xs = [p[0] for p in ctrl]
        ys = [p[1] for p in ctrl]
        pequeno = (max(xs) - min(xs) <= tolerancia and
                   max(ys) - min(ys) <= tolerancia)
        if pequeno or profundidade >= profundidade_max:
            (xa, ya), (xb, yb) = ctrl[0], ctrl[-1]
            pontos.extend(algoritmo_linha(sup, xa, ya, xb, yb, cor))
            return
        esquerda, direita = subdividir_casteljau(ctrl)
        recursao(esquerda, profundidade + 1)
        recursao(direita, profundidade + 1)

    recursao(list(controles), 0)
    return pontos

# sons.py - efeitos sonoros gerados por síntese (sem arquivos externos)
import math
import random
from array import array
import pygame
 
TAXA = 22050
INTERVALO_MIN_MS = 45  # evita empilhar o mesmo som no mesmo instante
 
VOL = {"geral": 0.8, "musica": 0.5, "tiros": 0.7, "explosoes": 0.8}
_CATEGORIA = {"tiro": "tiros", "explosao": "explosoes"}
_sons = {}
_base = {}
_ultimo = {}
_ativo = False
_musica = None
_canal_musica = None
MUSICA_BASE = 0.35
 
 
def _env(i, n, ataque=0.004):
    a = min(1.0, i / max(1, TAXA * ataque))
    return a * (1 - i / n) ** 2
 
 
def _explosao(dur=0.75, seed=3):
    rnd = random.Random(seed)
    n = int(TAXA * dur)
    y = y2 = fase = 0.0
    out = []
    for i in range(n):
        p = i / n
        y += (rnd.uniform(-1, 1) - y) * (0.22 * (1 - p) + 0.03)  # ruído com filtro fechando
        y2 += (y - y2) * 0.45
        fase += 2 * math.pi * (70 - 40 * p) / TAXA
        estrondo = math.sin(fase) * 0.7 * (1 - p) ** 1.5
        out.append((y2 * 2.4 + estrondo) * _env(i, n, 0.003))
    return out
 
 
def _dano_inimigo(dur=0.14, seed=5):
    rnd = random.Random(seed)
    n = int(TAXA * dur)
    out = []
    for i in range(n):
        t, p = i / TAXA, i / n
        tom = (math.sin(2 * math.pi * 920 * t) + 0.6 * math.sin(2 * math.pi * 1390 * t)
               + 0.3 * math.sin(2 * math.pi * 2310 * t))
        ruido = rnd.uniform(-1, 1) * max(0.0, 1 - p * 6)
        out.append((tom * 0.45 + ruido * 0.5) * _env(i, n, 0.001))
    return out
 
 
def _dano_jogador(dur=0.32, seed=7):
    rnd = random.Random(seed)
    n = int(TAXA * dur)
    fase = 0.0
    out = []
    for i in range(n):
        p = i / n
        fase += (320 - 210 * p) / TAXA
        serra = 2 * (fase % 1.0) - 1
        tremolo = 0.65 + 0.35 * math.sin(2 * math.pi * 28 * i / TAXA)
        ruido = rnd.uniform(-1, 1) * max(0.0, 1 - p * 4)
        out.append((serra * 0.55 * tremolo + ruido * 0.45) * _env(i, n, 0.002))
    return out
 
 
def _tiro(dur=0.15, seed=11):
    rnd = random.Random(seed)
    n = int(TAXA * dur)
    y = fase = 0.0
    out = []
    for i in range(n):
        p = i / n
        y += (rnd.uniform(-1, 1) - y) * 0.10  # ruído bem abafado (sem agudos)
        fase += 2 * math.pi * (130 - 80 * p) / TAXA
        env = min(1.0, i / (TAXA * 0.002)) * (1 - p) ** 3
        out.append((math.sin(fase) * 0.8 + y * 1.8) * env)
    return out
 
 
def _musica_marcha(bpm=104, batidas=16, seed=17):
    rnd = random.Random(seed)
    bt = 60 / bpm
    n = int(TAXA * bt * batidas)
    buf = [0.0] * n
 
    def somar(t0, dur, gerar):
        i0 = int(t0 * TAXA)
        m = min(int(dur * TAXA), n - i0)
        for k in range(m):
            buf[i0 + k] += gerar(k, m)
 
    def bumbo(k, m):
        p = k / m
        return math.sin(2 * math.pi * (62 - 22 * p) * k / TAXA) * (1 - p) ** 2 * 0.9
 
    def caixa_gen(vol):
        estado = [0.0]
 
        def g(k, m):
            estado[0] += (rnd.uniform(-1, 1) - estado[0]) * 0.35
            return estado[0] * (1 - k / m) ** 3 * vol
        return g
 
    def baixo(f):
        def g(k, m):
            p = k / m
            tri = 2 * abs(2 * ((f * k / TAXA) % 1.0) - 1) - 1
            return tri * 0.55 * min(1.0, k / 200) * (1 - p) ** 1.5
        return g
 
    def trompa(f):
        estado = [0.0]
 
        def g(k, m):
            q = 1.0 if (f * k / TAXA) % 1.0 < 0.5 else -1.0
            estado[0] += (q - estado[0]) * 0.08  # quadrada filtrada = timbre de metal abafado
            env = min(1.0, k / (TAXA * 0.04)) * min(1.0, (m - k) / (TAXA * 0.08))
            return estado[0] * env * 0.22
        return g
 
    A2, D2, E2, F2 = 110.0, 73.42, 82.41, 87.31
    graves = (A2, A2, A2, A2, F2, F2, F2, F2, D2, D2, E2, E2, A2, A2, E2, E2)
    melodia = (220.0, 261.63, 329.63, 293.66, 261.63, 220.0, 246.94, 164.81)
    for b in range(batidas):
        t = b * bt
        if b % 2 == 0:
            somar(t, bt * 0.9, bumbo)
        else:
            somar(t, bt * 0.5, caixa_gen(0.45))
        if b in (7, 15):
            for k in (1, 2, 3):
                somar(t + k * bt / 4, bt * 0.2, caixa_gen(0.3))
        for k in (0, 1):
            somar(t + k * bt / 2, bt * 0.45, baixo(graves[b]))
    for i, f in enumerate(melodia):
        somar(i * 2 * bt, 2 * bt * 0.95, trompa(f))
    return buf
 
 
def _bip(freqs, dur_nota=0.05, vol=0.6):
    out = []
    for f in freqs:
        n = int(TAXA * dur_nota)
        for i in range(n):
            q = 1.0 if math.sin(2 * math.pi * f * i / TAXA) >= 0 else -1.0  # onda quadrada (8-bit)
            out.append(q * vol * (1 - i / n))
    return out
 
 
def _criar_sound(amostras, canais):
    pico = max(1e-6, max(abs(a) for a in amostras))
    k = 32000 / max(1.0, pico)
    dados = array("h")
    for a in amostras:
        v = int(max(-32767, min(32767, a * k)))
        dados.extend((v,) * canais)
    return pygame.mixer.Sound(buffer=dados.tobytes())
 
 
def pre_iniciar():
    try:
        pygame.mixer.pre_init(TAXA, -16, 1, 512)
    except Exception:
        pass
 
 
def iniciar():
    global _ativo, TAXA
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(TAXA, -16, 1, 512)
        freq, tamanho, canais = pygame.mixer.get_init()
        if tamanho != -16:
            return
        TAXA = freq
        pygame.mixer.set_num_channels(17)
        pygame.mixer.set_reserved(1)
        global _musica, _canal_musica
        _musica = _criar_sound(_musica_marcha(), canais)
        _canal_musica = pygame.mixer.Channel(0)
        for nome, gerar, vol in (
            ("tiro", _tiro, 0.28),
            ("explosao", _explosao, 0.75),
            ("dano_inimigo", _dano_inimigo, 0.45),
            ("dano_jogador", _dano_jogador, 0.6),
            ("menu_mover", lambda: _bip((660,), 0.045), 0.1),
            ("menu_ok", lambda: _bip((660, 990), 0.06), 0.14),
        ):
            _sons[nome] = _criar_sound(gerar(), canais)
            _base[nome] = vol
        _ativo = True
        _aplicar()
    except Exception:
        _ativo = False  # sem dispositivo de áudio: jogo segue mudo
 
 
def _aplicar():
    for nome, s in _sons.items():
        cat = _CATEGORIA.get(nome)
        s.set_volume(_base[nome] * VOL["geral"] * (VOL[cat] if cat else 1.0))
    if _canal_musica is not None:
        _canal_musica.set_volume(MUSICA_BASE * VOL["geral"] * VOL["musica"])
 
 
def definir_volume(chave, valor):
    VOL[chave] = round(max(0.0, min(1.0, valor)), 2)
    if _ativo:
        _aplicar()
 
 
def tocar_musica():
    if _ativo and _musica is not None and not _canal_musica.get_busy():
        _canal_musica.play(_musica, loops=-1)
        _aplicar()
 
 
def tocar(nome, forcar=False):
    if not _ativo or nome not in _sons:
        return
    agora = pygame.time.get_ticks()
    if not forcar and agora - _ultimo.get(nome, -10 ** 9) < INTERVALO_MIN_MS:
        return
    _ultimo[nome] = agora
    _sons[nome].play()
 
# arena.py
import math
import random
import pygame
from algoritmos_cg import (
    linha_bresenham, circunferencia_bresenham, preencher_poligono_varredura,
    preencher_retangulo, preencher_circunferencia, desenhar_poligono,
    cohen_sutherland, sutherland_hodgman, recorte_ponto,
)
from config import *
 
XMIN, YMIN, XMAX, YMAX = JANELA_JOGO
ESP = 5
SX, SY = XMIN + XMAX, YMIN + YMAX  # 479, 285
TILE = 16
ARAME_FATOR = 0.55
SACOS_VIDA = 2
MARGEM_ARBUSTO = 3  # folga p/ o desenho do tanque (esteiras/quinas) não invadir a copa
 
COR_EXTRA = dict(
    ourico=(176, 182, 190), ourico_luz=(222, 228, 236), ourico_sombra=(8, 8, 10), ourico_parafuso=(38, 40, 46),
    barril_sombra=(0, 0, 0, 175), barril_contorno=(30, 6, 4), barril_perigo=(255, 214, 0), barril_brilho=(255, 255, 255),
    saco=(198, 178, 130), saco_alt=(184, 164, 118), saco_luz=(224, 208, 164),
    saco_junta=(132, 114, 78), saco_borda=(104, 88, 58),
)
 
# ---------- paletas dos biomas ----------
BIOMAS = {
    1: dict(  # Base Militar
        tema=0, fundo=(16, 18, 20), piso=(62, 64, 66), piso_alt=(58, 60, 62), junta=(46, 48, 50),
        graos=((72, 74, 76), (50, 52, 54), (82, 82, 80)), trinca=(38, 40, 42),
        oleo=(32, 32, 36), oleo_brilho=(66, 60, 82), faixa=(212, 172, 38), faixa_esc=(112, 98, 44),
        marca=(206, 206, 198), grade_fundo=(26, 28, 30), grade=(96, 100, 104), grade_borda=(40, 42, 44),
        heli_base=(72, 74, 76), heli_anel=(228, 186, 46), heli_h=(232, 232, 226),
        lama=(15, 15, 18), lama_escura=(30, 30, 38), lama_borda=(45, 45, 55),
        concreto=(124, 126, 120), concreto_borda=(64, 66, 62), brilho=(170, 172, 164), chanfro=(92, 94, 90),
        pintas=((112, 114, 108), (138, 140, 134)),
        destrutivel="caixote", dest=(92, 108, 62), dest_alt=(84, 98, 56), dest_borda=(44, 54, 28),
        dest_det=(62, 76, 40), rachadura=(24, 22, 12),
        sombra=(0, 0, 0, 150), arvore="moita", arbusto=((30, 66, 30), (46, 96, 40), (80, 138, 60)),
        escombros=((92, 108, 62), (62, 76, 40), (124, 126, 120)), rastro=(44, 46, 48),
    ),
    2: dict(  # Deserto / Ruínas
        tema=1, fundo=(30, 24, 16), piso=(198, 170, 118),
        manchas=((204, 178, 126), (191, 163, 111), (209, 183, 133), (187, 159, 107)),
        duna=(176, 148, 98), graos=((170, 142, 94), (216, 192, 142)),
        pedra=(126, 108, 82), pedra_luz=(170, 152, 122),
        laje=((184, 160, 116), (176, 150, 106), (192, 168, 124)), laje_luz=(214, 194, 150), laje_sombra=(150, 124, 84),
        terra=(184, 156, 106), terra_trinca=(138, 110, 70), capim=((150, 136, 74), (124, 110, 58), (176, 160, 92)),
        lama=(162, 130, 84), lama_escura=(142, 112, 70), lama_borda=(122, 96, 60),
        concreto=(150, 122, 92), concreto_borda=(86, 66, 46), brilho=(194, 168, 130), chanfro=(118, 94, 68),
        pintas=((134, 108, 80), (168, 140, 106), (112, 90, 66)),
        destrutivel="tijolo", dest=(164, 88, 60), dest_alt=(146, 76, 52), dest_borda=(92, 46, 30),
        dest_det=(206, 184, 148), rachadura=(48, 24, 14),
        trinch_fundo=(92, 70, 44), trinch_sombra=(58, 42, 26), trinch_luz=(160, 132, 92),
        trinch_borda=(178, 150, 106), trinch_det=(118, 88, 54),
        ponte_tipo="madeira", ponte=(150, 108, 62), ponte_junta=(96, 64, 34),
        ponte_borda=(78, 50, 24), ponte_luz=(184, 142, 90),
        sombra=(34, 20, 6, 150), arvore="rolante", arbusto=((96, 70, 36), (150, 116, 64), (206, 174, 112)),
        escombros=((164, 88, 60), (146, 76, 52), (206, 184, 148)), rastro=(170, 142, 96),
    ),
    3: dict(  # Base Ártica
        tema=2, fundo=(20, 28, 40), piso=(226, 236, 244),
        manchas=((236, 244, 250), (214, 226, 238), (244, 248, 252), (208, 222, 236)),
        duna=(200, 216, 232), graos=((198, 214, 230), (255, 255, 255)),
        gelo=(178, 208, 232), gelo_borda=(140, 178, 212),
        rocha=(96, 108, 124), rocha_borda=(58, 66, 80), pegada=(184, 202, 224), estaca=(60, 52, 46), bandeira=(236, 96, 36), trinca=(140, 176, 208), trinca_luz=(250, 252, 255),
        lama=(168, 202, 228), lama_escura=(146, 184, 214), lama_borda=(116, 158, 196),
        concreto=(48, 66, 96), concreto_borda=(18, 26, 42), brilho=(214, 228, 244), chanfro=(32, 46, 70),
        pintas=None, rebite_muro=(26, 36, 56),
        destrutivel="caixote", dest=(126, 92, 56), dest_alt=(114, 82, 48), dest_borda=(66, 44, 22),
        dest_det=(92, 64, 34), rachadura=(36, 22, 10),
        trinch_fundo=(44, 90, 148), trinch_sombra=(22, 52, 98), trinch_luz=(176, 218, 244),
        trinch_borda=(250, 252, 255), trinch_det=(96, 156, 206),
        ponte_tipo="metal", ponte=(92, 104, 120), ponte_junta=(56, 64, 78),
        ponte_borda=(36, 42, 54), ponte_luz=(156, 168, 184),
        sombra=(30, 50, 90, 110), arvore="pinheiro", arbusto=((18, 58, 42), (30, 84, 58), (48, 112, 76)),
        neve=(246, 250, 255), tronco=(88, 60, 38),
        escombros=((126, 92, 56), (48, 66, 96), (230, 238, 246)), rastro=(176, 198, 220),
    ),
}
 
 
def _ret(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
 
 
def _espelhar(poly, mx, my):
    return [(SX - x if mx else x, SY - y if my else y) for x, y in poly]
 
 
def _quatro(poly):
    return [poly, _espelhar(poly, True, False), _espelhar(poly, False, True), _espelhar(poly, True, True)]
 
 
def _par_x(poly):
    return [poly, _espelhar(poly, True, False)]
 
 
def _diag(poly):
    return [poly, _espelhar(poly, True, True)]
 
 
def _pts_quatro(x, y):
    return [(x, y), (SX - x, y), (x, SY - y), (SX - x, SY - y)]
 
 
def _rocha(cx, cy, rx, ry, n, seed):
    rnd = random.Random(seed)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.25, 0.25)
        k = rnd.uniform(0.72, 1.0)
        pts.append((int(round(cx + math.cos(a) * rx * k)), int(round(cy + math.sin(a) * ry * k))))
    return pts
 
 
def _seg_recortado(r):
    if not r:
        return None
    if len(r) == 5:
        return tuple(r[1:]) if r[0] else None
    if len(r) == 2:
        return (*r[0], *r[1])
    return tuple(r)
 
 
def _dist2_seg(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    l2 = dx * dx + dy * dy
    t = 0.0 if l2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
    qx, qy = ax + t * dx - px, ay + t * dy - py
    return qx * qx + qy * qy
 
 
def _dentro(poly, x, y):
    dentro, n = False, len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            dentro = not dentro
    return dentro
 
 
def _bbox(v):
    xs, ys = [x for x, _ in v], [y for _, y in v]
    return (min(xs), min(ys), max(xs), max(ys))
 
 
def _ok(j):
    return j[0] <= j[2] and j[1] <= j[3]
 
 
class Muro:
    def __init__(self, vertices, destrutivel=False, vida=MURO_VIDA, estilo=None):
        self.vertices = vertices
        self.destrutivel = destrutivel
        self.estilo = estilo
        self.vida = self.vida_max = vida if destrutivel else 0
        self.ativo = True
        self.bbox = _bbox(vertices)
        self.centro = ((self.bbox[0] + self.bbox[2]) / 2, (self.bbox[1] + self.bbox[3]) / 2)
 
    def toca_circulo(self, x, y, r):
        bx0, by0, bx1, by1 = self.bbox
        if x + r < bx0 or x - r > bx1 or y + r < by0 or y - r > by1:
            return False
        if _dentro(self.vertices, x, y):
            return True
        r2, v, n = r * r, self.vertices, len(self.vertices)
        return any(_dist2_seg(x, y, *v[i], *v[(i + 1) % n]) <= r2 for i in range(n))
 
 
class Barril:
    def __init__(self, x, y, r=BARRIL_RAIO):
        self.x, self.y, self.r = float(x), float(y), r
        self.ativo = True
 
    def toca_circulo(self, x, y, r):
        return (x - self.x) ** 2 + (y - self.y) ** 2 <= (r + self.r) ** 2
 
 
class Lama:
    def __init__(self, vertices):
        self.vertices = vertices
        self.bbox = _bbox(vertices)
 
    def contem(self, x, y):
        bx0, by0, bx1, by1 = self.bbox
        return bx0 <= x <= bx1 and by0 <= y <= by1 and _dentro(self.vertices, x, y)
 
 
class Arame(Lama):
    def contem(self, x, y):
        bx0, by0, bx1, by1 = self.bbox
        return bx0 <= x <= bx1 and by0 <= y <= by1
 
 
class Trincheira(Arame):
    def toca_circulo(self, x, y, r):
        bx0, by0, bx1, by1 = self.bbox
        qx, qy = min(max(x, bx0), bx1), min(max(y, by0), by1)
        return (qx - x) ** 2 + (qy - y) ** 2 <= r * r
 
 
class Arbusto:
    def __init__(self, x, y, tipo="moita"):
        self.x, self.y, self.tipo = x, y, tipo
        if tipo == "pinheiro":
            self.circulos = [(x, y - 5, 6), (x, y + 3, 10)]
        elif tipo == "rolante":
            self.circulos = [(x, y, 7)]
        else:
            self.circulos = [(x - 5, y + 1, 6), (x + 5, y + 2, 6), (x, y - 4, 7)]
        self.bbox = (min(cx - r for cx, _, r in self.circulos), min(cy - r for _, cy, r in self.circulos),
                     max(cx + r for cx, _, r in self.circulos), max(cy + r for _, cy, r in self.circulos))
 
    def toca_circulo(self, x, y, r):
        bx0, by0, bx1, by1 = self.bbox
        r += MARGEM_ARBUSTO
        if x + r < bx0 or x - r > bx1 or y + r < by0 or y - r > by1:
            return False
        return any((x - cx) ** 2 + (y - cy) ** 2 <= (r + rc) ** 2 for cx, cy, rc in self.circulos)
 
    def contem(self, x, y):
        bx0, by0, bx1, by1 = self.bbox
        if x < bx0 or x > bx1 or y < by0 or y > by1:
            return False
        return any((x - cx) ** 2 + (y - cy) ** 2 <= r * r for cx, cy, r in self.circulos)
 
 
# ---------- layouts (spawns: x, y, tipo, escudo) ----------
def _fase1():
    l = [(70, 50), (120, 50), (120, 57), (78, 57), (78, 90), (70, 90)]
    lama = [(95, 175), (135, 170), (150, 190), (130, 215), (95, 210), (85, 192)]
    return dict(
        concreto=_quatro(l) + _quatro(_ret(160, 100, 171, 111)) + _quatro(_ret(208, 112, 215, 119)),
        tijolo=[_ret(210, 60, 269, 66), _ret(210, SY - 66, 269, SY - 60)]
        + _par_x(_ret(140, 128, 146, 157)) + _quatro(_ret(40, 100, 46, 125)),
        sacos=_par_x(_ret(176, 132, 182, 152)) + _quatro(_ret(120, 18, 145, 24)),
        arame=_par_x(_ret(60, 134, 88, 150)),
        barris=[(200, 142), (SX - 200, 142), (120, 142), (SX - 120, 142), (239, 92), (239, SY - 92)],
        lama=_diag(lama),
        arbustos=_pts_quatro(185, 40),
        hangares=[_bbox(p) for p in _quatro(_ret(12, 12, 58, 40))],
        grades=_pts_quatro(30, 70) + [(239, 35), (239, SY - 35)],
        spawns=[(450, 142, "padrao", True), (445, 35, "rapido", False), (445, 250, "padrao", False),
                (239, 38, "padrao", False), (380, 142, "rapido", False)],
    )
 
 
def _fase2():
    lama_a = [(190, 232), (228, 228), (240, 242), (222, 258), (188, 255)]
    return dict(
        concreto=_quatro(_rocha(70, 60, 13, 12, 7, 3)) + [_ret(234, 115, 245, 170), _ret(212, 137, 267, 148)]
        + _quatro(_ret(165, 70, 205, 76)) + _par_x(_rocha(185, 142, 9, 8, 7, 5)),
        tijolo=_quatro(_ret(206, 70, 222, 76)),
        sacos=_par_x(_ret(88, 126, 95, 159)) + _quatro(_ret(140, 40, 168, 46)),
        arame=_par_x(_ret(145, 126, 165, 158)) + _diag(_ret(50, 246, 95, 255)),
        trincheiras=_par_x(_ret(118, 34, 128, 251)),
        pontes=_par_x(_ret(104, 130, 142, 156)),
        barris=[(200, 100), (SX - 200, SY - 100), (239, 65), (239, SY - 65)],
        lama=_diag(lama_a),
        arbustos=[(60, 105), (SX - 60, SY - 105), (185, 33), (SX - 185, SY - 33), (175, 185), (SX - 175, 185)],
        spawns=[(450, 142, "padrao", True), (440, 35, "rapido", False), (440, 250, "rapido", False),
                (400, 100, "artilharia", False), (400, 185, "padrao", True), (300, 100, "padrao", False)],
    )
 
 
def _fase3():
    lama_a = [(20, 180), (60, 175), (70, 200), (50, 240), (20, 235)]
    return dict(
        concreto=_quatro(_ret(60, 70, 170, 76)) + _quatro(_ret(60, 77, 66, 110))
        + [_ret(234, 21, 245, 80), _ret(234, SY - 80, 245, SY - 21)] + _quatro(_ret(195, 115, 215, 121)),
        tijolo=_quatro(_ret(171, 70, 195, 76)) + [_ret(220, 128, 259, 157)] + _par_x(_ret(100, 128, 106, 157)),
        sacos=_par_x(_ret(135, 125, 141, 160)) + _quatro(_ret(185, 92, 205, 98)),
        arame=_quatro(_ret(60, 23, 90, 33)) + [_ret(226, 88, 253, 108), _ret(226, SY - 108, 253, SY - 88)],
        trincheiras=_quatro(_ret(120, 38, 228, 47)),
        pontes=_quatro(_ret(163, 28, 189, 57)),
        barris=[(150, 142), (SX - 150, 142)] + _pts_quatro(120, 100)[::3],
        lama=_diag(lama_a),
        arbustos=_pts_quatro(90, 95) + [(35, 250), (465, 250)],
        spawns=[(450, 142, "artilharia", False), (440, 35, "rapido", True), (440, 250, "rapido", False),
                (300, 142, "padrao", True), (330, 59, "padrao", False), (330, 227, "artilharia", False)],
    )
 
 
FASES = {1: _fase1, 2: _fase2, 3: _fase3}
 
 
class Arena:
    def __init__(self, fase=1):
        self.janela = JANELA_JOGO
        self._piso = pygame.Surface((LARGURA, ALTURA))
        self.camada_muros = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        self._camada_solida = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        self.carregar_fase(fase)
 
    @property
    def piso(self):
        return self._piso
 
    @property
    def muros_ativos(self):
        return [m for m in self.muros if m.ativo]
 
    @property
    def barris_ativos(self):
        return [b for b in self.barris if b.ativo]
 
    # ---------- fases ----------
    def carregar_fase(self, numero):
        self.fase = (numero - 1) % NUM_FASES + 1
        self.cores = c = BIOMAS[(self.fase - 1) % len(BIOMAS) + 1]
        d = FASES[(self.fase - 1) % len(FASES) + 1]()
        externos = [
            _ret(XMIN, YMIN, XMAX, YMIN + ESP - 1),
            _ret(XMIN, YMAX - ESP + 1, XMAX, YMAX),
            _ret(XMIN, YMIN + ESP, XMIN + ESP - 1, YMAX - ESP),
            _ret(XMAX - ESP + 1, YMIN + ESP, XMAX, YMAX - ESP),
        ]
        self.muros = [Muro(p) for p in externos + d["concreto"]]
        self.muros += [Muro(p, destrutivel=True, estilo=c["destrutivel"]) for p in d["tijolo"]]
        self.muros += [Muro(p, destrutivel=True, vida=SACOS_VIDA, estilo="sacos") for p in d.get("sacos", ())]
        self.barris = [Barril(x, y) for x, y in d["barris"]]
        self.lamas = [Lama(p) for p in d["lama"]]
        self.arames = [Arame(p) for p in d.get("arame", ())]
        self.trincheiras = [Trincheira(p) for p in d.get("trincheiras", ())]
        self.pontes = [_bbox(p) for p in d.get("pontes", ())]
        self.arbustos = [Arbusto(x, y, c["arvore"]) for x, y in d.get("arbustos", ())]
        self._hangares = d.get("hangares", ())
        self._grades = d.get("grades", ())
        self._spawns = d["spawns"]
        self._rng = random.Random(self.fase * 31)
        self._render_piso()
        self._render_muros()
 
    def reiniciar(self):
        self.carregar_fase(self.fase)
 
    # ---------- piso ----------
    def _render_piso(self):
        s, c = self._piso, self.cores
        preencher_retangulo(s, 0, 0, LARGURA - 1, ALTURA - 1, c["fundo"])
        rnd = random.Random(7 + self.fase)
        (self._piso_base, self._piso_deserto, self._piso_artico)[c["tema"]](s, c, rnd)
        for lama in self.lamas:
            rec = sutherland_hodgman(lama.vertices, self.janela)
            if not rec or len(rec) < 3:
                continue
            rec = [(int(x), int(y)) for x, y in rec]
            preencher_poligono_varredura(s, rec, c["lama"])
            bx0, by0, bx1, by1 = lama.bbox
            for _ in range((bx1 - bx0) * (by1 - by0) // 18):
                x, y = rnd.randint(bx0, bx1), rnd.randint(by0, by1)
                if lama.contem(x, y) and lama.contem(x + 1, y):
                    preencher_retangulo(s, x, y, x + rnd.randint(0, 1), y, c["lama_escura"])
            desenhar_poligono(s, rec, c["lama_borda"], algoritmo_linha=linha_bresenham)
        for t in self.trincheiras:
            self._desenhar_trincheira(s, t, c, rnd)
        for p in self.pontes:
            self._desenhar_ponte(s, p, c)
        for a in self.arames:
            self._desenhar_arame(s, a)
 
    def _placas(self, s, c, t):
        for j, ty in enumerate(range(YMIN, YMAX + 1, t)):
            for i, tx in enumerate(range(XMIN, XMAX + 1, t)):
                x1, y1 = min(tx + t - 1, XMAX), min(ty + t - 1, YMAX)
                preencher_retangulo(s, tx, ty, x1, y1, c["piso"] if (i + j) & 1 else c["piso_alt"])
                preencher_retangulo(s, tx, ty, x1, ty, c["junta"])
                preencher_retangulo(s, tx, ty, tx, y1, c["junta"])
 
    def _graos(self, s, rnd, n, cores):
        for _ in range(n):
            s.set_at((rnd.randint(XMIN, XMAX), rnd.randint(YMIN, YMAX)), rnd.choice(cores))
 
    def _manchas(self, s, rnd, n, cores):
        for _ in range(n):
            r = rnd.randint(3, 10)
            preencher_circunferencia(s, rnd.randint(XMIN + r, XMAX - r), rnd.randint(YMIN + r, YMAX - r),
                                     r, rnd.choice(cores))
 
    def _ondas(self, s, rnd, n, cor):
        for _ in range(n):
            x, y = rnd.randint(XMIN, XMAX - 30), rnd.randint(YMIN + 3, YMAX - 3)
            comp, fs = rnd.randint(12, 28), rnd.uniform(0, 6)
            px, py = x, y
            for i in range(2, comp + 1, 2):
                nx, ny = x + i, y + int(round(math.sin(i * 0.35 + fs) * 1.5))
                linha_bresenham(s, px, py, nx, ny, cor)
                px, py = nx, ny
 
    def _trinca(self, s, rnd, cor, luz=None, x=None, y=None, passos=(3, 7)):
        if x is None:
            x, y = rnd.randint(XMIN + ESP, XMAX - ESP), rnd.randint(YMIN + ESP, YMAX - ESP)
        a = rnd.uniform(0, 2 * math.pi)
        for _ in range(rnd.randint(*passos)):
            n = rnd.randint(*passos)
            nx, ny = x + math.cos(a) * n, y + math.sin(a) * n
            if luz:
                self.desenhar_linha_recortada(s, x + 1, y + 1, nx + 1, ny + 1, luz)
            self.desenhar_linha_recortada(s, x, y, nx, ny, cor)
            if rnd.random() < 0.25:
                b = a + rnd.choice((-1.1, 1.1))
                self.desenhar_linha_recortada(s, nx, ny, nx + math.cos(b) * 4, ny + math.sin(b) * 4, cor)
            x, y = nx, ny
            a += rnd.uniform(-0.8, 0.8)
 
    def _mancha_oleo(self, s, rnd, c):
        r = rnd.randint(3, 7)
        m = r + r // 2 + 3
        cx, cy = rnd.randint(XMIN + ESP + m, XMAX - ESP - m), rnd.randint(YMIN + ESP + m, YMAX - ESP - m)
        preencher_circunferencia(s, cx, cy, r, c["oleo"])
        for _ in range(3):
            preencher_circunferencia(s, cx + rnd.randint(-r, r), cy + rnd.randint(-r, r),
                                     rnd.randint(1, max(1, r // 2)), c["oleo"])
        s.set_at((cx - 1, cy - 1), c["oleo_brilho"])
        s.set_at((cx, cy - 1), c["oleo_brilho"])
 
    def _contorno(self, s, x0, y0, x1, y1, cor):
        linha_bresenham(s, x0, y0, x1, y0, cor)
        linha_bresenham(s, x0, y1, x1, y1, cor)
        linha_bresenham(s, x0, y0, x0, y1, cor)
        linha_bresenham(s, x1, y0, x1, y1, cor)
 
    def _hangar(self, s, r, c):
        x0, y0, x1, y1 = r
        jan = (x0 + 4, y0 + 4, x1 - 4, y1 - 4)
        for k in range(x0 - y1, x1 - y0 + 1, 7):
            self.desenhar_linha_recortada(s, k + y0, y0, k + y1, y1, c["faixa_esc"], jan)
        self._contorno(s, x0, y0, x1, y1, c["marca"])
        self._contorno(s, x0 + 2, y0 + 2, x1 - 2, y1 - 2, c["marca"])
        cx = (x0 + x1) // 2
        linha_bresenham(s, cx - 4, y0 + 2, cx + 4, y0 + 2, c["faixa"])
        linha_bresenham(s, cx - 4, y1 - 2, cx + 4, y1 - 2, c["faixa"])
 
    def _grade(self, s, x, y, c):
        preencher_retangulo(s, x - 6, y - 3, x + 6, y + 3, c["grade_fundo"])
        for xx in range(x - 5, x + 6, 2):
            linha_bresenham(s, xx, y - 2, xx, y + 2, c["grade"])
        self._contorno(s, x - 6, y - 3, x + 6, y + 3, c["grade_borda"])
 
    def _heliponto(self, s, c):
        cx, cy = SX // 2, SY // 2
        preencher_circunferencia(s, cx, cy, 27, c["heli_base"])
        circunferencia_bresenham(s, cx, cy, 27, c["heli_anel"])
        circunferencia_bresenham(s, cx, cy, 26, c["heli_anel"])
        circunferencia_bresenham(s, cx, cy, 21, c["heli_h"])
        for d in range(3):
            linha_bresenham(s, cx - 8 + d, cy - 9, cx - 8 + d, cy + 9, c["heli_h"])
            linha_bresenham(s, cx + 6 + d, cy - 9, cx + 6 + d, cy + 9, c["heli_h"])
        for d in range(2):
            linha_bresenham(s, cx - 5, cy - 1 + d, cx + 5, cy - 1 + d, c["heli_h"])
        for k in range(8):
            a = k * math.pi / 4
            s.set_at((int(round(cx + math.cos(a) * 24)), int(round(cy + math.sin(a) * 24))), c["heli_anel"])
 
    def _piso_base(self, s, c, rnd):
        self._placas(s, c, 32)
        self._graos(s, rnd, 900, c["graos"])
        for _ in range(16):
            self._trinca(s, rnd, c["trinca"])
        for _ in range(8):
            self._mancha_oleo(s, rnd, c)
        for y in (YMIN + 30, YMAX - 31):
            for x in range(XMIN + 64, XMAX - 64, 16):
                preencher_retangulo(s, x, y, min(x + 8, XMAX - 64), y + 1, c["faixa"])
        for r in self._hangares:
            self._hangar(s, r, c)
        for x, y in self._grades:
            self._grade(s, x, y, c)
        self._heliponto(s, c)
 
    def _piso_deserto(self, s, c, rnd):
        preencher_retangulo(s, XMIN, YMIN, XMAX, YMAX, c["piso"])
        self._manchas(s, rnd, 160, c["manchas"])
        self._ondas(s, rnd, 55, c["duna"])
        for _ in range(6):
            self._laje_ruina(s, c, rnd)
        for _ in range(6):
            self._terra_rachada(s, c, rnd)
        self._marcas_esteira(s, rnd, c["rastro"], 3)
        for _ in range(28):
            self._capim(s, c, rnd)
        self._graos(s, rnd, 500, c["graos"])
        for _ in range(40):
            x, y = rnd.randint(XMIN, XMAX - 1), rnd.randint(YMIN + 1, YMAX)
            preencher_retangulo(s, x, y, x + 1, y, c["pedra"])
            s.set_at((x, y - 1), c["pedra_luz"])
 
    def _piso_artico(self, s, c, rnd):
        preencher_retangulo(s, XMIN, YMIN, XMAX, YMAX, c["piso"])
        self._manchas(s, rnd, 170, c["manchas"])
        for _ in range(9):
            rx, ry = rnd.randint(10, 22), rnd.randint(7, 14)
            cx = rnd.randint(XMIN + ESP + rx + 2, XMAX - ESP - rx - 2)
            cy = rnd.randint(YMIN + ESP + ry + 2, YMAX - ESP - ry - 2)
            p = _rocha(cx, cy, rx, ry, 8, rnd.randint(0, 9999))
            preencher_poligono_varredura(s, p, c["gelo"])
            desenhar_poligono(s, p, c["gelo_borda"], algoritmo_linha=linha_bresenham)
            linha_bresenham(s, cx - rx // 2, cy - 1, cx - rx // 4, cy - 3, c["trinca_luz"])
            linha_bresenham(s, cx - rx // 3, cy + 1, cx - rx // 6, cy - 1, c["trinca_luz"])
        self._ondas(s, rnd, 40, c["duna"])
        for _ in range(26):
            self._trinca(s, rnd, c["trinca"], c["trinca_luz"])
        self._marcas_esteira(s, rnd, c["rastro"], 3)
        self._pegadas(s, rnd, c["pegada"], 6)
        for _ in range(12):
            self._rocha_neve(s, c, rnd)
        for _ in range(7):
            self._estaca(s, c, rnd)
        self._graos(s, rnd, 450, c["graos"])
 
    def _dentro_jogo(self, x, y):
        return XMIN + ESP < x < XMAX - ESP and YMIN + ESP < y < YMAX - ESP
 
    def _laje_ruina(self, s, c, rnd):
        t, n, m = 8, rnd.randint(2, 5), rnd.randint(2, 4)
        x = rnd.randint(XMIN + ESP + 2, XMAX - ESP - 2 - n * t)
        y = rnd.randint(YMIN + ESP + 2, YMAX - ESP - 2 - m * t)
        for i in range(n):
            for j in range(m):
                if rnd.random() < 0.3:
                    continue
                x0, y0 = x + i * t, y + j * t
                x1, y1 = x0 + t - 2, y0 + t - 2
                preencher_retangulo(s, x0, y0, x1, y1, rnd.choice(c["laje"]))
                linha_bresenham(s, x0, y0, x1, y0, c["laje_luz"])
                linha_bresenham(s, x0, y0, x0, y1, c["laje_luz"])
                linha_bresenham(s, x0 + 1, y1 + 1, x1 + 1, y1 + 1, c["laje_sombra"])
                linha_bresenham(s, x1 + 1, y0 + 1, x1 + 1, y1 + 1, c["laje_sombra"])
                if rnd.random() < 0.35:
                    linha_bresenham(s, x0 + rnd.randint(1, 3), y0 + 1, x0 + rnd.randint(3, 5), y1 - 1, c["laje_sombra"])
                for _ in range(rnd.randint(0, 5)):
                    s.set_at((rnd.randint(x0, x1), rnd.randint(y0, y1)), c["piso"])
 
    def _terra_rachada(self, s, c, rnd):
        r = rnd.randint(7, 12)
        cx = rnd.randint(XMIN + ESP + r + 8, XMAX - ESP - r - 8)
        cy = rnd.randint(YMIN + ESP + r + 8, YMAX - ESP - r - 8)
        preencher_circunferencia(s, cx, cy, r, c["terra"])
        for _ in range(rnd.randint(3, 6)):
            a, d = rnd.uniform(0, 2 * math.pi), rnd.uniform(0, r * 0.6)
            self._trinca(s, rnd, c["terra_trinca"], x=cx + math.cos(a) * d, y=cy + math.sin(a) * d, passos=(2, 3))
 
    def _capim(self, s, c, rnd):
        x = rnd.randint(XMIN + ESP + 3, XMAX - ESP - 3)
        y = rnd.randint(YMIN + ESP + 4, YMAX - ESP - 1)
        for dx in (-2, -1, 0, 1, 2):
            if rnd.random() < 0.7:
                linha_bresenham(s, x, y, x + dx, y - rnd.randint(1, 3), rnd.choice(c["capim"]))
 
    def _marcas_esteira(self, s, rnd, cor, n):
        for _ in range(n):
            x, y = rnd.uniform(XMIN + 20, XMAX - 20), rnd.uniform(YMIN + 20, YMAX - 20)
            a = rnd.uniform(0, 2 * math.pi)
            for k in range(rnd.randint(40, 90)):
                x, y = x + math.cos(a) * 2, y + math.sin(a) * 2
                a += rnd.uniform(-0.06, 0.06)
                if k % 4 == 3:
                    continue
                for lado in (-1, 1):
                    px, py = int(round(x - math.sin(a) * 4 * lado)), int(round(y + math.cos(a) * 4 * lado))
                    if self._dentro_jogo(px, py):
                        s.set_at((px, py), cor)
 
    def _pegadas(self, s, rnd, cor, n):
        for _ in range(n):
            x, y = rnd.uniform(XMIN + 20, XMAX - 20), rnd.uniform(YMIN + 20, YMAX - 20)
            a = rnd.uniform(0, 2 * math.pi)
            for k in range(rnd.randint(10, 22)):
                x, y = x + math.cos(a) * 3, y + math.sin(a) * 3
                a += rnd.uniform(-0.15, 0.15)
                lado = 1 if k & 1 else -1
                px, py = int(round(x - math.sin(a) * 1.5 * lado)), int(round(y + math.cos(a) * 1.5 * lado))
                for qx, qy in ((px, py), (px + int(round(math.cos(a))), py + int(round(math.sin(a))))):
                    if self._dentro_jogo(qx, qy):
                        s.set_at((qx, qy), cor)
 
    def _rocha_neve(self, s, c, rnd):
        rx, ry = rnd.randint(3, 5), rnd.randint(2, 4)
        cx = rnd.randint(XMIN + ESP + 8, XMAX - ESP - 8)
        cy = rnd.randint(YMIN + ESP + 8, YMAX - ESP - 8)
        linha_bresenham(s, cx - rx + 2, cy + ry + 1, cx + rx, cy + ry + 1, c["trinca"])
        p = _rocha(cx, cy, rx, ry, 7, rnd.randint(0, 9999))
        preencher_poligono_varredura(s, p, c["rocha"])
        desenhar_poligono(s, p, c["rocha_borda"], algoritmo_linha=linha_bresenham)
        q = _rocha(cx, cy - ry // 2 - 1, rx, max(1, ry // 2 + 1), 6, rnd.randint(0, 9999))
        preencher_poligono_varredura(s, q, c["neve"])
 
    def _estaca(self, s, c, rnd):
        x = rnd.randint(XMIN + ESP + 4, XMAX - ESP - 4)
        y = rnd.randint(YMIN + ESP + 6, YMAX - ESP - 3)
        linha_bresenham(s, x + 1, y + 1, x + 2, y + 1, c["trinca"])
        linha_bresenham(s, x, y - 5, x, y, c["estaca"])
        preencher_retangulo(s, x + 1, y - 5, x + 3, y - 4, c["bandeira"])
 
    def _desenhar_trincheira(self, s, t, c, rnd):
        x0, y0, x1, y1 = t.bbox
        horiz = x1 - x0 >= y1 - y0
        u0, u1, v0, v1 = (x0, x1, y0, y1) if horiz else (y0, y1, x0, x1)
        P = (lambda u, v: (u, v)) if horiz else (lambda u, v: (v, u))
 
        def lin(ua, va, ub, vb, cor):
            a, b = P(ua, va), P(ub, vb)
            self.desenhar_linha_recortada(s, a[0], a[1], b[0], b[1], cor)
 
        def px(u, v, cor):
            x, y = P(u, v)
            if recorte_ponto(x, y, self.janela):
                s.set_at((x, y), cor)
 
        madeira = c.get("ponte_tipo") == "madeira"
        if madeira:  # parapeito de sacos de areia
            X = COR_EXTRA
            for va, vb in ((v0 - 3, v0 - 2), (v1 + 3, v1 + 2)):
                for i, u in enumerate(range(u0 - 2, u1 + 2, 4)):
                    cor = X["saco"] if i & 1 else X["saco_alt"]
                    lin(u, va, u + 2, va, cor)
                    lin(u, vb, u + 2, vb, cor)
                    px(u + 1, va, X["saco_luz"])
                    px(u + 3, vb, X["saco_junta"])
        else:  # neve acumulada na borda
            neve = c.get("neve", (250, 252, 255))
            for vv, fora in ((v0 - 2, -1), (v1 + 2, 1)):
                u = u0 - 1
                while u < u1:
                    n = rnd.randint(2, 5)
                    lin(u, vv, min(u + n, u1 + 1), vv, neve)
                    if rnd.random() < 0.5 and n > 2:
                        lin(u + 1, vv + fora, min(u + n - 1, u1), vv + fora, neve)
                    u += n + rnd.randint(1, 3)
 
        preencher_retangulo(s, x0 - 1, y0 - 1, x1 + 1, y1 + 1, c["trinch_borda"])
        preencher_retangulo(s, x0, y0, x1, y1, c["trinch_fundo"])
        preencher_retangulo(s, x0, y0, x1, min(y1, y0 + 2), c["trinch_sombra"])
        preencher_retangulo(s, x0, y0, min(x1, x0 + 2), y1, c["trinch_sombra"])
        preencher_retangulo(s, x0 + 1, y1, x1, y1, c["trinch_luz"])
        preencher_retangulo(s, x1, y0 + 1, x1, y1, c["trinch_luz"])
        if not _ok((x0 + 3, y0 + 3, x1 - 1, y1 - 1)):
            return
        vm = (v0 + v1) // 2 + 1
        if madeira:
            for u in range(u0 + 3, u1 - 1, 7):  # escoras de madeira nas paredes
                lin(u, v0 + 3, u, v0 + 4, c["trinch_det"])
                lin(u, v1 - 2, u, v1 - 1, c["trinch_det"])
            lin(u0 + 3, vm - 2, u1 - 2, vm - 2, c["ponte_junta"])  # estrado de tábuas
            lin(u0 + 3, vm + 2, u1 - 2, vm + 2, c["ponte_junta"])
            for u in range(u0 + 3, u1 - 1, 2):
                lin(u, vm - 1, u, vm + 1, c["ponte"] if (u // 2) & 1 else c["ponte_luz"])
            for _ in range(max(1, (u1 - u0) // 70)):  # caixas de munição
                u = rnd.randint(u0 + 6, u1 - 8)
                a, b = P(u, vm - 2), P(u + 4, vm + 2)
                preencher_retangulo(s, min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]), (88, 104, 56))
                self._contorno(s, min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]), (44, 54, 28))
                px(u + 2, vm, (212, 176, 64))
            for _ in range((u1 - u0) // 12):  # cartuchos
                px(rnd.randint(u0 + 3, u1 - 2), rnd.choice((v0 + 3, v1 - 1)), (212, 176, 64))
        else:
            for u in range(u0 + 6, u1 - 3, 12):  # escoras metálicas
                lin(u, v0 + 3, u, v1 - 1, c["ponte_luz"])
            lin(u0 + 3, vm - 1, u1 - 2, vm - 1, c["ponte_borda"])  # grade metálica
            lin(u0 + 3, vm + 1, u1 - 2, vm + 1, c["ponte_borda"])
            for u in range(u0 + 3, u1 - 1, 2):
                lin(u, vm - 1, u, vm + 1, c["ponte"])
            for u in range(u0 + 2, u1 - 1, 3):  # pingentes de gelo
                if rnd.random() < 0.7:
                    lin(u, v0 + 1, u, v0 + rnd.randint(1, 2), c["trinch_luz"])
            for u in range(u0 + 1, u1, 3):
                px(u, v0, c["trinch_borda"])
            for _ in range((u1 - u0) // 5):  # cintilação
                px(rnd.randint(u0 + 3, u1 - 2), rnd.randint(v0 + 3, v1 - 1), (255, 255, 255))
 
    def _desenhar_ponte(self, s, p, c):
        x0, y0, x1, y1 = p
        horiz = x1 - x0 >= y1 - y0
        preencher_retangulo(s, x0 + 2, y0 + 2, min(x1 + 2, XMAX), min(y1 + 2, YMAX), c["trinch_sombra"])
        preencher_retangulo(s, x0, y0, x1, y1, c["ponte"])
        madeira = c.get("ponte_tipo") == "madeira"
        if horiz:
            for x in range(x0 + 2, x1 - 1, 4 if madeira else 3):
                linha_bresenham(s, x, y0 + 2, x, y1 - 2, c["ponte_junta"])
                if madeira:
                    s.set_at((x + 1, y0 + 3), c["ponte_luz"])
                    s.set_at((x + 1, y1 - 3), c["ponte_luz"])
            if not madeira:
                for y in range(y0 + 4, y1 - 2, 6):
                    linha_bresenham(s, x0 + 2, y, x1 - 2, y, c["ponte_luz"])
            for y, cor in ((y0, c["ponte_borda"]), (y0 + 1, c["ponte_luz"]), (y1, c["ponte_borda"]), (y1 - 1, c["ponte_borda"])):
                linha_bresenham(s, x0, y, x1, y, cor)
        else:
            for y in range(y0 + 2, y1 - 1, 4 if madeira else 3):
                linha_bresenham(s, x0 + 2, y, x1 - 2, y, c["ponte_junta"])
                if madeira:
                    s.set_at((x0 + 3, y + 1), c["ponte_luz"])
                    s.set_at((x1 - 3, y + 1), c["ponte_luz"])
            if not madeira:
                for x in range(x0 + 4, x1 - 2, 6):
                    linha_bresenham(s, x, y0 + 2, x, y1 - 2, c["ponte_luz"])
            for x, cor in ((x0, c["ponte_borda"]), (x0 + 1, c["ponte_luz"]), (x1, c["ponte_borda"]), (x1 - 1, c["ponte_borda"])):
                linha_bresenham(s, x, y0, x, y1, cor)
 
    def _desenhar_arame(self, s, a):  # fileira de ouriços tchecos
        x0, y0, x1, y1 = a.bbox
        horiz = x1 - x0 >= y1 - y0
        u0, u1, v0, v1 = (x0, x1, y0, y1) if horiz else (y0, y1, x0, x1)
        larg = v1 - v0
        k = max(2, min(4, larg // 2 - 1))
        fileiras = [v0 + larg // 4, v1 - larg // 4] if larg >= 16 else [(v0 + v1) // 2]
        passo = 2 * k + 3
        util = u1 - u0 - 2 * k
        n = max(1, util // passo + 1)
        ini = u0 + k + (util - (n - 1) * passo) // 2
        centros = [(u, v) if horiz else (v, u) for v in fileiras for u in range(ini, ini + n * passo, passo)]
        for sombra in (True, False):
            for cx, cy in centros:
                self._ourico(s, cx, cy, k, sombra)
        for cx, cy in centros:
            if recorte_ponto(cx, cy, self.janela):
                s.set_at((cx, cy), COR_EXTRA["ourico_parafuso"])
 
    def _ourico(self, s, cx, cy, k, sombra):
        X = COR_EXTRA
        o = 1 if sombra else 0
        for ax, ay, bx, by in ((-k, -k, k, k), (-k, k, k, -k)):
            for d in (-1, 1, 0):
                cor = X["ourico_sombra"] if sombra else (X["ourico_luz"] if d == 0 else X["ourico"])
                self.desenhar_linha_recortada(s, cx + ax + d + o, cy + ay + o, cx + bx + d + o, cy + by + o, cor)
 
    # ---------- muros ----------
    def _render_muros(self):
        c = self.cores
        s, sol = self.camada_muros, self._camada_solida
        s.fill((0, 0, 0, 0))
        sol.fill((0, 0, 0, 0))
        recortados = []
        for m in self.muros_ativos:
            rec = sutherland_hodgman(m.vertices, self.janela)
            if rec and len(rec) >= 3:
                recortados.append(([(int(x), int(y)) for x, y in rec], m))
        for rec, _ in recortados:  # sombras projetadas
            sombra = sutherland_hodgman([(x + 3, y + 3) for x, y in rec], self.janela)
            if sombra and len(sombra) >= 3:
                preencher_poligono_varredura(s, [(int(x), int(y)) for x, y in sombra], c["sombra"])
        for b in self.barris_ativos:
            preencher_circunferencia(s, int(b.x) + 2, int(b.y) + 2, b.r + 1, COR_EXTRA["barril_sombra"])
        for a in self.arbustos:
            for cx, cy, r in a.circulos:
                preencher_circunferencia(s, cx + 3, cy + 3, r, c["sombra"])
        for rec, m in recortados:
            if m.destrutivel:
                self._desenhar_destrutivel(sol, rec, m, c)
            else:
                self._desenhar_solido(sol, rec, c)
        for b in self.barris_ativos:
            self._desenhar_barril(sol, int(b.x), int(b.y), b.r)
        self.mascara = pygame.mask.from_surface(sol)
        s.blit(sol, (0, 0))
        for a in self.arbustos:
            if a.tipo == "pinheiro":
                self._desenhar_pinheiro(s, a, c)
            elif a.tipo == "rolante":
                self._desenhar_rolante(s, a, c)
            else:
                self._desenhar_arbusto(s, a, c)
 
    def _desenhar_barril(self, s, cx, cy, r):
        X = COR_EXTRA
        preencher_circunferencia(s, cx, cy, r, COR_BARRIL)
        circunferencia_bresenham(s, cx, cy, r, X["barril_contorno"])
        k = max(1, r - 2)
        linha_bresenham(s, cx - k, cy - k, cx + k, cy + k, X["barril_perigo"])
        linha_bresenham(s, cx - k, cy + k, cx + k, cy - k, X["barril_perigo"])
        s.set_at((cx - 1, cy - r + 1), X["barril_brilho"])
        s.set_at((cx, cy - r + 1), X["barril_brilho"])
 
    def _desenhar_solido(self, s, rec, c):
        preencher_poligono_varredura(s, rec, c["concreto"])
        x0, y0, x1, y1 = _bbox(rec)
        rnd = random.Random(x0 * 131 + y0 * 17 + x1 * 7 + y1)
        if c.get("pintas") and x1 - x0 >= 2 and y1 - y0 >= 2:
            for _ in range((x1 - x0) * (y1 - y0) // 14):
                x, y = rnd.randint(x0 + 1, x1 - 1), rnd.randint(y0 + 1, y1 - 1)
                if _dentro(rec, x, y):
                    s.set_at((x, y), rnd.choice(c["pintas"]))
        self._chanfro(s, rec, (x0, y0, x1, y1), c)
        if c.get("rebite_muro"):
            self._rebites(s, rec, (x0, y0, x1, y1), c)
        desenhar_poligono(s, rec, c["concreto_borda"], algoritmo_linha=linha_bresenham)
 
    def _chanfro(self, s, rec, bbox, c):
        x0, y0, x1, y1 = bbox
        jan = (x0 + 1, y0 + 1, x1 - 1, y1 - 1)
        if not _ok(jan):
            return
        n = len(rec)
        for i in range(n):
            ax, ay = rec[i]
            bx, by = rec[(i + 1) % n]
            dx, dy = bx - ax, by - ay
            ln = math.hypot(dx, dy)
            if ln == 0:
                continue
            nx, ny = -dy / ln, dx / ln
            if not _dentro(rec, (ax + bx) / 2 + nx * 1.5, (ay + by) / 2 + ny * 1.5):
                nx, ny = -nx, -ny
            ox, oy = int(round(nx)), int(round(ny))
            cor = c["brilho"] if (ny > 0.3 or nx > 0.3) else c["chanfro"]
            self.desenhar_linha_recortada(s, ax + ox, ay + oy, bx + ox, by + oy, cor, jan)
 
    def _rebites(self, s, rec, bbox, c):
        x0, y0, x1, y1 = bbox
        w, h = x1 - x0, y1 - y0
        if min(w, h) >= 9:
            pts = [(x0 + 3, y0 + 3), (x1 - 3, y0 + 3), (x0 + 3, y1 - 3), (x1 - 3, y1 - 3)]
        elif w >= h:
            pts = [(x, (y0 + y1) // 2) for x in range(x0 + 4, x1 - 2, 10)]
        else:
            pts = [((x0 + x1) // 2, y) for y in range(y0 + 4, y1 - 2, 10)]
        for x, y in pts:
            if _dentro(rec, x, y) and _dentro(rec, x - 1, y - 1):
                s.set_at((x, y), c["rebite_muro"])
                s.set_at((x - 1, y - 1), c["brilho"])
 
    def _desenhar_destrutivel(self, s, rec, m, c):
        estilo = m.estilo or c["destrutivel"]
        if estilo == "sacos":
            preencher_poligono_varredura(s, rec, COR_EXTRA["saco_junta"])
            self._sacos(s, m.bbox)
            borda = COR_EXTRA["saco_borda"]
        else:
            preencher_poligono_varredura(s, rec, c["dest"])
            if estilo == "tijolo":
                self._tijolos(s, m.bbox, c)
            else:
                self._caixote(s, m.bbox, c)
            borda = c["dest_borda"]
        if m.vida < m.vida_max:
            self._rachaduras(s, m, c)
        desenhar_poligono(s, rec, borda, algoritmo_linha=linha_bresenham)
 
    def _sacos(self, s, bbox):
        X = COR_EXTRA
        x0, y0, x1, y1 = bbox
        jan = (x0 + 1, y0 + 1, x1 - 1, y1 - 1)
        if not _ok(jan):
            return
        rnd = random.Random(x0 * 29 + y0 * 11 + x1)
        for i, y in enumerate(range(y0 + 1, y1, 4)):
            by0, by1 = y, min(y + 2, jan[3])
            for x in range(x0 + 1 - (3 if i & 1 else 0), x1, 7):
                bx0, bx1 = max(x, jan[0]), min(x + 5, jan[2])
                if bx0 > bx1 or by0 > by1:
                    continue
                preencher_retangulo(s, bx0, by0, bx1, by1, rnd.choice((X["saco"], X["saco_alt"])))
                if bx1 - bx0 >= 2:
                    linha_bresenham(s, bx0 + 1, by0, bx1 - 1, by0, X["saco_luz"])
                for px in (bx0, bx1):
                    if px in (x, x + 5):
                        s.set_at((px, by0), X["saco_junta"])
                        s.set_at((px, by1), X["saco_junta"])
 
    def _tijolos(self, s, bbox, c):
        x0, y0, x1, y1 = bbox
        jan = (x0 + 1, y0 + 1, x1 - 1, y1 - 1)
        if not _ok(jan):
            return
        rnd = random.Random(x0 * 31 + y0 * 7 + x1)
        for i, y in enumerate(range(y0 + 1, y1, 3)):
            for x in range(x0 + 1 - (3 if i & 1 else 0), x1, 6):
                bx0, bx1, by1 = max(x, jan[0]), min(x + 5, jan[2]), min(y + 1, jan[3])
                if bx0 <= bx1 and y <= by1:
                    preencher_retangulo(s, bx0, y, bx1, by1, rnd.choice((c["dest"], c["dest_alt"])))
        for i, y in enumerate(range(y0 + 3, y1, 3)):
            self.desenhar_linha_recortada(s, x0, y, x1, y, c["dest_det"], jan)
            for x in range(x0 + (3 if i & 1 else 0), x1, 6):
                self.desenhar_linha_recortada(s, x, y - 3, x, y, c["dest_det"], jan)
 
    def _caixote(self, s, bbox, c):
        x0, y0, x1, y1 = bbox
        w, h = x1 - x0, y1 - y0
        horiz = w >= h
        comp = w if horiz else h
        n = max(1, int(round(comp / max(4, min(w, h)))))
        passo = comp / n
        for i in range(n):
            a0, a1 = int(round(i * passo)), int(round((i + 1) * passo))
            bx0, by0, bx1, by1 = (x0 + a0, y0, x0 + a1, y1) if horiz else (x0, y0 + a0, x1, y0 + a1)
            jan = (bx0 + 1, by0 + 1, bx1 - 1, by1 - 1)
            if not _ok(jan):
                continue
            if i & 1:
                preencher_retangulo(s, *jan, c["dest_alt"])
            self._contorno(s, *jan, c["dest_det"])
            self.desenhar_linha_recortada(s, bx0 + 2, by0 + 2, bx1 - 2, by1 - 2, c["dest_det"], jan)
            self.desenhar_linha_recortada(s, bx0 + 2, by1 - 2, bx1 - 2, by0 + 2, c["dest_det"], jan)
            if i > 0:
                if horiz:
                    linha_bresenham(s, bx0, by0, bx0, by1, c["dest_borda"])
                else:
                    linha_bresenham(s, bx0, by0, bx1, by0, c["dest_borda"])
 
    def _rachaduras(self, s, m, c):
        x0, y0, x1, y1 = m.bbox
        jan = (x0 + 1, y0 + 1, x1 - 1, y1 - 1)
        if not _ok(jan):
            return
        rnd = random.Random(x0 * 7349 + y0 * 1931 + x1 * 83 + y1)
        w, h = x1 - x0, y1 - y0
        horiz = w >= h
        comp, larg = (w, h) if horiz else (h, w)
        meio = larg / 2
        for _ in range(min(m.vida_max - m.vida, 3)):
            t, lado = rnd.randint(0, max(0, comp // 4)), 1
            ant = None
            while t <= comp:
                off = meio + lado * rnd.uniform(0.5, max(1.0, larg / 2 - 0.5))
                p = (x0 + t, y0 + off) if horiz else (x0 + off, y0 + t)
                if ant:
                    self.desenhar_linha_recortada(s, *ant, *p, c["rachadura"], jan)
                ant, lado = p, -lado
                t += rnd.randint(2, 4)
 
    def _desenhar_arbusto(self, s, a, c):
        esc, med, cla = c["arbusto"]
        for cx, cy, r in a.circulos:
            preencher_circunferencia(s, cx, cy, r, esc)
        for cx, cy, r in a.circulos:
            preencher_circunferencia(s, cx - 1, cy - 1, r - 2, med)
        for cx, cy, r in a.circulos:
            preencher_circunferencia(s, cx - 2, cy - 2, max(1, r - 4), cla)
        rnd = random.Random(a.x * 13 + a.y)
        for _ in range(10):
            x, y = rnd.randint(a.bbox[0], a.bbox[2]), rnd.randint(a.bbox[1], a.bbox[3])
            if a.contem(x, y):
                s.set_at((x, y), rnd.choice((esc, cla)))
 
    def _desenhar_rolante(self, s, a, c):  # erva-roliça: galhos secos emaranhados
        esc, med, cla = c["arbusto"]
        cx, cy, r = a.circulos[0]
        rnd = random.Random(a.x * 17 + a.y * 3)
        for cor, n in ((esc, 9), (med, 9), (cla, 6)):
            for _ in range(n):
                a1, a2 = rnd.uniform(0, 2 * math.pi), rnd.uniform(0, 2 * math.pi)
                r1, r2 = rnd.uniform(0.3, 1.0) * r, rnd.uniform(0.5, 1.0) * r
                linha_bresenham(s, int(round(cx + math.cos(a1) * r1)), int(round(cy + math.sin(a1) * r1)),
                                int(round(cx + math.cos(a2) * r2)), int(round(cy + math.sin(a2) * r2)), cor)
        circunferencia_bresenham(s, cx, cy, r, esc)
        circunferencia_bresenham(s, cx - 1, cy - 1, r - 3, med)
        for _ in range(8):  # pontas soltas
            ang = rnd.uniform(0, 2 * math.pi)
            linha_bresenham(s, int(round(cx + math.cos(ang) * (r - 1))), int(round(cy + math.sin(ang) * (r - 1))),
                            int(round(cx + math.cos(ang) * (r + 1))), int(round(cy + math.sin(ang) * (r + 1))), med)
        s.set_at((cx - 2, cy - 3), cla)
 
    def _desenhar_pinheiro(self, s, a, c):
        x, y = a.x, a.y
        esc, med, _ = c["arbusto"]
        neve = c["neve"]
        preencher_retangulo(s, x - 1, y + 7, x + 1, y + 10, c["tronco"])
        for topo, hw in ((y - 1, 9), (y - 6, 7), (y - 11, 5)):
            base = topo + 8
            preencher_poligono_varredura(s, [(x, topo), (x + hw, base), (x - hw, base)], esc)
            preencher_poligono_varredura(s, [(x, topo + 2), (x, base - 1), (x - hw + 2, base - 1)], med)
            linha_bresenham(s, x - hw, base, x + hw, base, neve)
            linha_bresenham(s, x - hw + 2, base - 1, x - 1, base - 1, neve)
            s.set_at((x, topo), neve)
            s.set_at((x - 1, topo + 1), neve)
            s.set_at((x + 1, topo + 1), neve)
 
    # ---------- marcas no piso ----------
    def _carimbar_cratera(self, x, y, r):
        s = self._piso
        preencher_circunferencia(s, x, y, r + 1, COR_CRATERA_QUEIMADO)
        preencher_circunferencia(s, x, y, max(1, r * 2 // 3), COR_CRATERA)
        preencher_circunferencia(s, x, y, max(0, r // 3), COR_CRATERA_CENTRO)
        circunferencia_bresenham(s, x, y, r, COR_CRATERA_ANEL)
        if r >= 4:
            for k in range(5):
                a = k * 2.513 + r
                self.desenhar_linha_recortada(s, x, y, x + math.cos(a) * (r + 3), y + math.sin(a) * (r + 3), COR_CRATERA)
 
    def adicionar_cratera(self, x, y, raio):
        x, y = int(x), int(y)
        if recorte_ponto(x, y, self.janela):
            self._carimbar_cratera(x, y, raio)
 
    def adicionar_rastro(self, x, y, angulo, meia_largura=4):
        c, s = math.cos(angulo), math.sin(angulo)
        cor = self.cores.get("rastro", COR_RASTRO_ESTEIRA)
        for lado in (-1, 1):
            px = int(round(x - c * 2 - s * meia_largura * lado))
            py = int(round(y - s * 2 + c * meia_largura * lado))
            if recorte_ponto(px, py, self.janela):
                preencher_retangulo(self._piso, px, py, px, py, cor)
 
    def _escombros(self, m):
        x0, y0, x1, y1 = m.bbox
        self._carimbar_cratera(int(m.centro[0]), int(m.centro[1]), max(3, min(x1 - x0, y1 - y0) // 2))
        if m.estilo == "sacos":
            cores = (COR_EXTRA["saco"], COR_EXTRA["saco_alt"], COR_EXTRA["saco_junta"])
        else:
            cores = self.cores.get("escombros", COR_ESCOMBROS)
        for _ in range(ESCOMBROS_QTD):
            ex, ey = self._rng.randint(x0 - 2, x1 + 2), self._rng.randint(y0 - 2, y1 + 2)
            t = self._rng.randint(0, 1)
            if recorte_ponto(ex, ey, self.janela) and recorte_ponto(ex + t, ey + t, self.janela):
                preencher_retangulo(self._piso, ex, ey, ex + t, ey + t, self._rng.choice(cores))
 
    def desenhar(self, sup):
        sup.blit(self._piso, (0, 0))
        sup.blit(self.camada_muros, (0, 0))
 
    # ---------- destrutíveis ----------
    def danificar_muro(self, muro, dano=1):
        if muro is None or not muro.destrutivel or not muro.ativo:
            return False
        muro.vida -= dano
        if muro.vida <= 0:
            muro.ativo = False
            self._escombros(muro)
        self._render_muros()
        return not muro.ativo
 
    def explodir_barril(self, b):
        if b is None or not b.ativo:
            return None
        b.ativo = False
        self._carimbar_cratera(int(b.x), int(b.y), 7)
        self._render_muros()
        return (b.x, b.y)
 
    def muro_em(self, x, y):
        for m in self.muros:
            if m.ativo and m.toca_circulo(x, y, 1.0):
                return m
        return None
 
    def barril_em(self, x, y):
        for b in self.barris:
            if b.ativo and b.toca_circulo(x, y, 1.0):
                return b
        return None
 
    def muros_em_raio(self, x, y, r):
        return [m for m in self.muros if m.ativo and m.toca_circulo(x, y, r)]
 
    def barris_em_raio(self, x, y, r):
        return [b for b in self.barris if b.ativo and b.toca_circulo(x, y, r)]
 
    def fator_terreno(self, x, y):
        f = 1.0
        if any(l.contem(x, y) for l in self.lamas):
            f *= LAMA_FATOR
        if any(a.contem(x, y) for a in self.arames):
            f *= ARAME_FATOR
        return f
 
    def em_arbusto(self, x, y):
        return any(a.contem(x, y) for a in self.arbustos)
 
    def na_trincheira(self, x, y, r):
        for t in self.trincheiras:
            if not t.toca_circulo(x, y, r):
                continue
            tx0, ty0, tx1, ty1 = t.bbox
            ix0, iy0 = max(x - r, tx0), max(y - r, ty0)
            ix1, iy1 = min(x + r, tx1), min(y + r, ty1)
            if not any(p[0] <= ix0 and ix1 <= p[2] and p[1] <= iy0 and iy1 <= p[3] for p in self.pontes):
                return True
        return False
 
    # ---------- helpers ----------
    def desenhar_linha_recortada(self, sup, x1, y1, x2, y2, cor, janela=None):
        seg = _seg_recortado(cohen_sutherland(x1, y1, x2, y2, janela or self.janela))
        if seg:
            a, b, c, d = (int(round(v)) for v in seg)
            linha_bresenham(sup, a, b, c, d, cor)
 
    def colide_ponto(self, x, y):
        xi, yi = int(x), int(y)
        if not recorte_ponto(xi, yi, self.janela):
            return True
        return bool(self.mascara.get_at((xi, yi))) or self.em_arbusto(x, y)
 
    def colide_circulo(self, x, y, r):
        if x - r < XMIN + ESP or x + r > XMAX - ESP or y - r < YMIN + ESP or y + r > YMAX - ESP:
            return True
        if any(m.ativo and m.toca_circulo(x, y, r) for m in self.muros):
            return True
        if any(b.ativo and b.toca_circulo(x, y, r) for b in self.barris):
            return True
        if any(a.toca_circulo(x, y, r) for a in self.arbustos):
            return True
        return self.na_trincheira(x, y, r)
 
    def refletir(self, px, py, x, y, vx, vy):
        hx = self.colide_ponto(x, py)
        hy = self.colide_ponto(px, y)
        if hx:
            vx = -vx
        if hy:
            vy = -vy
        if not hx and not hy:
            vx, vy = -vx, -vy
        return vx, vy
 
    def tem_linha_de_visao(self, p1, p2):
        pts = linha_bresenham(None, int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]))
        return not any(self.colide_ponto(px, py) for px, py in pts or ())
 
    def spawn_jogador(self):
        return (XMIN + 28.0, SY / 2)
 
    def spawns_inimigos(self):
        res = []
        for x, y, tipo, escudo in self._spawns:
            if not self.colide_circulo(x, y, TIPOS_INIMIGO[tipo]["raio"] + 1):
                res.append((float(x), float(y), tipo, escudo))
        return res
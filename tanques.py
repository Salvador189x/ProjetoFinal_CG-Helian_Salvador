# tanques.py
import math
import random
from algoritmos_cg import (
    linha_bresenham, circunferencia_bresenham, preencher_poligono_varredura,
    preencher_retangulo, preencher_circunferencia, desenhar_poligono,
    ponto_bezier, bezier_casteljau,
)
from config import *
from pathfinding import calcular_caminho, TAM_CELULA
import sons
 
XMIN, YMIN, XMAX, YMAX = JANELA_JOGO
MORTEIRO_MUNICAO = MORTEIRO_MUNICAO_MAX
BRANCO = (255, 255, 255)
COR_TRAJ = (190, 196, 200)
COR_TRAJ_RICOCHETE = (40, 235, 220)
DISTANCIA_TIPO = {"padrao": 70, "rapido": 45, "artilharia": 0}
FRAMES_RASTRO = 4
RECALC_FRAMES = 25
FRAMES_PRESO = 15
FRAMES_DESVIO = 8
COR_ESTEIRA_BORDA = (12, 12, 14)
_DIR8 = ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))
COR_ESTEIRA_ELO = (78, 78, 84)
 
 
def _dif(a, b):
    return (b - a + math.pi) % (2 * math.pi) - math.pi
 
 
def _aproximar(a, b, passo):
    d = _dif(a, b)
    return b if abs(d) <= passo else a + math.copysign(passo, d)
 
 
def _escurecer(cor, f=0.55):
    return tuple(int(c * f) for c in cor[:3])
 
 
def _cor_boca(det, cano):
    if sum((a - b) ** 2 for a, b in zip(det, cano)) >= 90 ** 2:
        return tuple(det[:3])
    m = sum(det[:3]) / 3
    return tuple(min(255, max(0, int(m + (c - m) * 1.8))) for c in det[:3])
 
 
def _pixel(sup, x, y, cor):
    linha_bresenham(sup, x, y, x, y, cor)
 
 
def gerar_pontos_patrulha(arena, passo=20):
    pts = []
    for y in range(YMIN + 14, YMAX - 10, passo):
        for x in range(XMIN + 14, XMAX - 10, passo):
            if not arena.colide_circulo(x, y, INI_RAIO + 5):
                pts.append((float(x), float(y)))
    return pts
 
 
# ---------------- Tanque base ----------------
class Tanque:
    def __init__(self, x, y, raio, vida, vel, vel_rot, cor, cor_det, cor_cano, escudo=False):
        self.x, self.y = float(x), float(y)
        self.raio, self.vida, self.vida_max = raio, vida, vida
        self.vel, self.vel_rot = vel, vel_rot
        self.cor, self.cor_det, self.cor_cano = cor, cor_det, cor_cano
        self.cor_boca = _cor_boca(cor_det, cor_cano)
        self.angulo_corpo = self.ang_canhao = 0.0
        self.cadencia_t = 0.0
        self.flash = 0.0
        self.vivo = True
        self.escudo = escudo
        self.escudo_inicial = escudo
        self._frames_mov = 0
        self._frame = 0
        self._tempo = random.uniform(0, 3)
 
    @property
    def ang_corpo(self):
        return self.angulo_corpo
 
    @ang_corpo.setter
    def ang_corpo(self, v):
        self.angulo_corpo = v
 
    def atualizar_timers(self, dt):
        self.cadencia_t = max(0.0, self.cadencia_t - dt)
        self.flash = max(0.0, self.flash - dt)
        self._tempo += dt
        self._frame += 1
 
    def mover(self, dx, dy, dt, arena, fator=1.0):
        n = math.hypot(dx, dy)
        if n == 0:
            return False
        dx, dy = dx / n, dy / n
        self.angulo_corpo = _aproximar(self.angulo_corpo, math.atan2(dy, dx), self.vel_rot * dt * 2)
        passo = self.vel * fator * arena.fator_terreno(self.x, self.y) * dt  # lama: -50%
        ox, oy = self.x, self.y
        nx = self.x + dx * passo
        if not arena.colide_circulo(nx, self.y, self.raio):
            self.x = nx
        ny = self.y + dy * passo
        if not arena.colide_circulo(self.x, ny, self.raio):
            self.y = ny
        moveu = abs(self.x - ox) + abs(self.y - oy) > passo * 0.2
        if moveu:
            self._frames_mov += 1
            if self._frames_mov % FRAMES_RASTRO == 0:
                arena.adicionar_rastro(self.x, self.y, self.angulo_corpo, self.raio - 1)
        return moveu
 
    def mirar(self, tx, ty):
        self.ang_canhao = math.atan2(ty - self.y, tx - self.x)
 
    def pode_atirar(self):
        return self.vivo and self.cadencia_t <= 0
 
    def ponta_cano(self):
        return (self.x + math.cos(self.ang_canhao) * COMPRIMENTO_CANO,
                self.y + math.sin(self.ang_canhao) * COMPRIMENTO_CANO)
 
    def atirar(self, cor, dono, cadencia):
        self.cadencia_t = cadencia
        sons.tocar("tiro")
        return Projetil(*self.ponta_cano(), self.ang_canhao, cor, dono)
 
    def sofrer_dano(self, d):
        # retorna "escudo" (absorvido) | True (dano) | False (ignorado)
        if not self.vivo:
            return False
        if self.escudo:
            self.escudo = False
            self.flash = 0.08
            return "escudo"
        self.vida -= d
        self.flash = 0.12
        if self.vida <= 0:
            self.vivo = False
        return True
 
    def desenhar_escudo(self, sup):
        if not self.escudo:
            return
        cx, cy = int(round(self.x)), int(round(self.y))
        p = int(round(math.sin(self._tempo * 6)))
        c1, c2 = (COR_ESCUDO, COR_ESCUDO_BRILHO) if self._frame % 2 else (COR_ESCUDO_BRILHO, COR_ESCUDO)
        circunferencia_bresenham(sup, cx, cy, self.raio + 3 + p, c1)
        circunferencia_bresenham(sup, cx, cy, self.raio + 5 + p, c2)
 
    def desenhar(self, sup):
        piscando = self.flash > 0
        cor = BRANCO if piscando else self.cor
        det = BRANCO if piscando else self.cor_det
        cano = BRANCO if piscando else self.cor_cano
        escuro = _escurecer(cor, 0.4)
        c, s = math.cos(self.angulo_corpo), math.sin(self.angulo_corpo)
        hl, hw = self.raio + 1, self.raio - 1
 
        def rot(lx, ly):
            return (int(round(self.x + lx * c - ly * s)), int(round(self.y + lx * s + ly * c)))
 
        for lado in (-1, 1):  # esteiras
            e0, e1 = lado * (hw - 1), lado * (hw + 1)
            preencher_poligono_varredura(sup, [rot(-hl - 1, e0), rot(hl + 1, e0), rot(hl + 1, e1), rot(-hl - 1, e1)], COR_ESTEIRA)
            desenhar_poligono(sup, [rot(-hl - 1, e0), rot(hl + 1, e0), rot(hl + 1, e1), rot(-hl - 1, e1)],
                              COR_ESTEIRA_BORDA, algoritmo_linha=linha_bresenham)
            for t in range(-hl, hl + 1, 3):
                _pixel(sup, *rot(t + (self._frames_mov // 2) % 3 - 1, lado * hw), COR_ESTEIRA_ELO)
        corpo = [rot(-hl, -hw), rot(hl, -hw), rot(hl, hw), rot(-hl, hw)]
        preencher_poligono_varredura(sup, corpo, escuro)  # borda externa
        placa = [rot(-hl + 1, -hw + 1), rot(hl - 1, -hw + 1), rot(hl - 1, hw - 1), rot(-hl + 1, hw - 1)]
        preencher_poligono_varredura(sup, placa, cor)
        desenhar_poligono(sup, corpo, escuro, algoritmo_linha=linha_bresenham)
        linha_bresenham(sup, *rot(hl - 1, -hw + 1), *rot(hl - 1, hw - 1), det)
        linha_bresenham(sup, *rot(-hl + 1, -hw + 1), *rot(-hl + 1, hw - 1), _escurecer(cor, 0.7))
 
        cx, cy = int(round(self.x)), int(round(self.y))
        rt = max(2, self.raio - 2)
        ca, sa = math.cos(self.ang_canhao), math.sin(self.ang_canhao)
        nx, ny = -sa, ca
        ix, iy = int(round(self.x + ca * rt)), int(round(self.y + sa * rt))
        fx, fy = int(round(self.x + ca * COMPRIMENTO_CANO)), int(round(self.y + sa * COMPRIMENTO_CANO))
        ox, oy = (0, 1) if abs(ca) >= abs(sa) else (1, 0)  # espessura fixa de 2 px, sem buracos
        linha_bresenham(sup, ix + ox, iy + oy, fx + ox, fy + oy, _escurecer(cano, 0.45))
        linha_bresenham(sup, ix, iy, fx, fy, cano)
        preencher_circunferencia(sup, cx, cy, rt, _escurecer(cor, 0.85))
        circunferencia_bresenham(sup, cx, cy, rt, escuro)
        hx, hy = int(round(self.x - ca + nx)), int(round(self.y - sa + ny))
        circunferencia_bresenham(sup, hx, hy, 1, escuro)  # escotilha
        _pixel(sup, hx, hy, det)
        boca = BRANCO if piscando else self.cor_boca  # boca em "T", barra quantizada em 45° (estável)
        q = int(round(math.atan2(ny, nx) / (math.pi / 4))) % 8
        dx, dy = _DIR8[q]
        bx, by = _DIR8[(q + 2) % 8]
        h = 2 if dx == 0 or dy == 0 else 1
        linha_bresenham(sup, fx + bx - dx * h, fy + by - dy * h, fx + bx + dx * h, fy + by + dy * h, escuro)
        linha_bresenham(sup, fx - dx * h, fy - dy * h, fx + dx * h, fy + dy * h, boca)
        _pixel(sup, fx, fy, BRANCO)
        self.desenhar_escudo(sup)
 
 
# ---------------- Jogador ----------------
class Jogador(Tanque):
    def __init__(self, x, y):
        super().__init__(x, y, JOG_RAIO, JOG_VIDA, JOG_VELOCIDADE, JOG_VEL_ROTACAO,
                         COR_JOGADOR, COR_JOGADOR_DET, COR_JOGADOR_CANO)
        self.invencivel = 0.0
        self.morteiros = MORTEIRO_MUNICAO_MAX
        self.recarga = 0.0
        self.escudo_t = 0.0
 
    def atualizar(self, dt):
        self.atualizar_timers(dt)
        self.invencivel = max(0.0, self.invencivel - dt)
        if self.escudo:
            self.escudo_t -= dt
            if self.escudo_t <= 0:
                self.escudo = False
        if self.morteiros < MORTEIRO_MUNICAO_MAX:
            self.recarga += dt
            if self.recarga >= MORTEIRO_RECARGA:
                self.morteiros += 1
                self.recarga = 0.0
        else:
            self.recarga = 0.0
 
    def lancar_morteiro(self, tx, ty):
        if self.morteiros <= 0 or not self.vivo:
            return None
        self.morteiros -= 1
        sons.tocar("tiro")
        return Morteiro(self.x, self.y, tx, ty, "jogador")
 
    def ativar_escudo(self):
        self.escudo = True
        self.escudo_t = ESCUDO_DURACAO
 
    def sofrer_dano(self, d):
        if self.invencivel > 0:
            return False
        r = super().sofrer_dano(d)
        self.invencivel = 0.4 if r == "escudo" else JOG_INVENCIVEL
        return r
 
    def desenhar_trajetoria(self, sup, arena, alcance=320, alcance_ric=90):
        c, s = math.cos(self.ang_canhao), math.sin(self.ang_canhao)
        ox, oy = self.ponta_cano()
        if arena.colide_ponto(ox, oy):
            return
        ant, hit = (int(ox), int(oy)), None
        pts = linha_bresenham(None, int(ox), int(oy), int(ox + c * alcance), int(oy + s * alcance)) or ()
        for i, (px, py) in enumerate(pts):
            if arena.colide_ponto(px, py):
                hit = (px, py)
                break
            if i % 4 < 2:
                _pixel(sup, px, py, COR_TRAJ)
            ant = (px, py)
        if hit is None:
            return
        muro = arena.muro_em(*hit)
        if arena.barril_em(*hit) or (muro is not None and muro.destrutivel):
            _pixel(sup, ant[0], ant[1], COR_ONDA)
            return
        vx, vy = arena.refletir(ant[0], ant[1], hit[0], hit[1], c, s)
        pts = linha_bresenham(None, ant[0], ant[1], int(ant[0] + vx * alcance_ric), int(ant[1] + vy * alcance_ric)) or ()
        for i, (px, py) in enumerate(pts):
            if i and arena.colide_ponto(px, py):
                break
            if i % 4 < 2:
                _pixel(sup, px, py, COR_TRAJ_RICOCHETE)
 
    def desenhar(self, sup):
        if self.invencivel > 0 and int(self.invencivel * 20) % 2:
            return
        super().desenhar(sup)
 
 
# ---------------- Inimigos ----------------
class Inimigo(Tanque):
    def __init__(self, x, y, tipo="padrao", escudo=False):
        p = TIPOS_INIMIGO[tipo]
        super().__init__(x, y, p["raio"], p["vida"], p["velocidade"], p["vel_rot"],
                         p["cor"], p["cor_det"], p["cor_cano"], escudo)
        self.tipo = tipo
        self.cadencia = p["cadencia"]
        self.alcance = p["alcance"]
        self.angulo_corpo = self.ang_canhao = math.pi
        self.alvo = None
        self.t_alvo = 0.0
        self.t_visao = random.uniform(0, 0.12)
        self.vendo = False
        self.ultimo_visto = None
        self.cadencia_t = random.uniform(0.6, self.cadencia)
        self.caminho = []
        self._dest_cam = None
        self._t_cam = random.randint(0, RECALC_FRAMES - 1)
        self._ref_preso = None
        self._frames_preso = 0
        self._desvio = 0
        self._lado = 1
 
    def _enxerga(self, arena, j):
        dx, dy = j.x - self.x, j.y - self.y
        d = math.hypot(dx, dy)
        if d > self.alcance:
            return False
        if self.tipo == "artilharia":
            return True
        no_cone = abs(_dif(self.ang_canhao, math.atan2(dy, dx))) <= math.radians(INI_ANGULO_VISAO) / 2
        if not (self.vendo or no_cone or d < 40):
            return False
        return arena.tem_linha_de_visao((self.x, self.y), (j.x, j.y))
 
    def _ir_para(self, tx, ty, dt, arena, fator=1.0):
        return self.mover(tx - self.x, ty - self.y, dt, arena, fator)
 
    def _seguir(self, tx, ty, dt, arena, fator=1.0):
        self._t_cam -= 1
        d = self._dest_cam
        if self._t_cam <= 0 or d is None or math.hypot(tx - d[0], ty - d[1]) > 2 * TAM_CELULA:
            self.caminho = calcular_caminho(arena, (self.x, self.y), (tx, ty), self.raio)
            self._dest_cam, self._t_cam = (tx, ty), RECALC_FRAMES
        while self.caminho and math.hypot(self.caminho[0][0] - self.x, self.caminho[0][1] - self.y) < 4:
            self.caminho.pop(0)
        if not self.caminho:
            return False
        wx, wy = self.caminho[0]
        if self._ref_preso is None:
            self._ref_preso, self._frames_preso = (self.x, self.y), 0
        if self._desvio > 0:
            self._desvio -= 1
            fx, fy = wx - self.x, wy - self.y
            n = math.hypot(fx, fy) or 1.0
            fx, fy = fx / n, fy / n
            self.mover(-fy * self._lado - fx * 0.4, fx * self._lado - fy * 0.4, dt, arena, fator)
        else:
            self._ir_para(wx, wy, dt, arena, fator)
        self._frames_preso += 1
        if self._frames_preso >= FRAMES_PRESO:
            if math.hypot(self.x - self._ref_preso[0], self.y - self._ref_preso[1]) < 1.0:
                self._t_cam = 0
                self._desvio = FRAMES_DESVIO
                self._lado = -self._lado
            self._ref_preso, self._frames_preso = (self.x, self.y), 0
        return True
 
    def _disparar(self, jogador):
        if self.tipo == "artilharia":
            self.cadencia_t = self.cadencia
            tx = jogador.x + random.uniform(-7, 7)
            ty = jogador.y + random.uniform(-7, 7)
            sons.tocar("tiro")
            return Morteiro(self.x, self.y, tx, ty, "inimigo", alcance=self.alcance, cor=self.cor_det)
        return self.atirar(COR_BALA_INIMIGO, "inimigo", self.cadencia)
 
    def atualizar(self, dt, arena, jogador, pontos):
        self.atualizar_timers(dt)
        self.t_alvo -= dt
        self.t_visao -= dt
        if self.t_visao <= 0:
            self.t_visao = 0.12
            self.vendo = jogador.vivo and self._enxerga(arena, jogador)
 
        if self.vendo:
            self.ultimo_visto = (jogador.x, jogador.y)
            ang = math.atan2(jogador.y - self.y, jogador.x - self.x)
            self.ang_canhao = _aproximar(self.ang_canhao, ang, self.vel_rot * dt)
            dist_min = DISTANCIA_TIPO[self.tipo]
            if dist_min and math.hypot(jogador.x - self.x, jogador.y - self.y) > dist_min:
                self._seguir(jogador.x, jogador.y, dt, arena, 0.6)
            if abs(_dif(self.ang_canhao, ang)) < 0.12 and self.pode_atirar():
                return self._disparar(jogador)
            return None
 
        if self.ultimo_visto and self.tipo != "artilharia":
            self.alvo, self.t_alvo = self.ultimo_visto, 4.0
        self.ultimo_visto = None
        if (self.alvo is None or self.t_alvo <= 0
                or math.hypot(self.alvo[0] - self.x, self.alvo[1] - self.y) < 4):
            self.alvo = random.choice(pontos) if pontos else (self.x, self.y)
            self.t_alvo = 6.0
        if not self._seguir(*self.alvo, dt, arena):
            self.alvo = None
        self.ang_canhao = _aproximar(self.ang_canhao, self.angulo_corpo, self.vel_rot * dt)
        return None
 
 
# ---------------- Projéteis ----------------
class Projetil:
    def __init__(self, x, y, ang, cor, dono):
        self.x, self.y = x, y
        self.px, self.py = x, y
        self.vx, self.vy = math.cos(ang) * BALA_VELOCIDADE, math.sin(ang) * BALA_VELOCIDADE
        self.cor, self.rastro = cor, _escurecer(cor)
        self.dono = dono
        self.t = BALA_DURACAO
        self.ricochetes = 0
        self.muro_destruido = None
        self.barril = None
        self.vivo = True
 
    def atualizar(self, dt, arena, alvos):
        # None | "ricochete" | "muro" | "barril" | tanque atingido
        self.px, self.py = self.x, self.y
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.t -= dt
        if self.t <= 0:
            self.vivo = False
            return None
        if arena.colide_ponto(self.x, self.y):
            barril = arena.barril_em(self.x, self.y)
            if barril is not None:
                self.barril = barril
                self.vivo = False
                return "barril"
            muro = arena.muro_em(self.x, self.y)
            if muro is not None and muro.destrutivel:
                if arena.danificar_muro(muro, BALA_DANO_MURO):
                    self.muro_destruido = muro
                self.vivo = False
                return "muro"
            if self.ricochetes < BALA_MAX_RICOCHETES:
                self.vx, self.vy = arena.refletir(self.px, self.py, self.x, self.y, self.vx, self.vy)
                self.x, self.y = self.px, self.py
                self.ricochetes += 1
                return "ricochete"
            self.vivo = False
            return "muro"
        for a in alvos:
            if a.vivo and (a.x - self.x) ** 2 + (a.y - self.y) ** 2 <= (a.raio + BALA_RAIO + (3 if a.escudo else 0)) ** 2:
                self.vivo = False
                return a
        return None
 
    def desenhar(self, sup, arena):
        k = 0.03
        arena.desenhar_linha_recortada(sup, self.x - self.vx * k, self.y - self.vy * k, self.x, self.y, self.rastro)
        preencher_circunferencia(sup, int(round(self.x)), int(round(self.y)), BALA_RAIO, self.cor)
 
 
Bala = Projetil
 
 
class Morteiro:
    def __init__(self, ox, oy, tx, ty, dono="jogador", alcance=MORTEIRO_ALCANCE_MAX,
                 cor=COR_MORTEIRO, raio_explosao=MORTEIRO_RAIO_EXPLOSAO):
        dx, dy = tx - ox, ty - oy
        d = math.hypot(dx, dy)
        if d > alcance:
            tx, ty = ox + dx / d * alcance, oy + dy / d * alcance
            d = alcance
        tx = min(max(tx, XMIN + 6), XMAX - 6)
        ty = min(max(ty, YMIN + 6), YMAX - 6)
        self.dono, self.cor, self.raio_explosao = dono, cor, raio_explosao
        self.p0, self.p2 = (ox, oy), (tx, ty)
        self.p1 = ((ox + tx) / 2, (oy + ty) / 2 - MORTEIRO_ALTURA - d * 0.15)
        self.ctrl = [self.p0, self.p1, self.p2]
        self.ctrl_i = [(int(x), int(y)) for x, y in self.ctrl]
        self.t = 0.0
        self.ativo, self.explodiu = True, False
 
    @property
    def destino(self):
        return self.p2
 
    def atualizar(self, dt):
        self.t += dt
        if self.t >= MORTEIRO_DURACAO:
            self.ativo, self.explodiu = False, True
 
    def desenhar(self, sup):
        u = min(1.0, self.t / MORTEIRO_DURACAO)
        tx, ty = int(self.p2[0]), int(self.p2[1])
        bezier_casteljau(sup, self.ctrl_i, _escurecer(self.cor, 0.6))
        if int(self.t * 12) % 2:
            circunferencia_bresenham(sup, tx, ty, self.raio_explosao, COR_ONDA)
        for k in range(1, MORTEIRO_RASTRO_PASSOS):
            uk = u - k * 0.015
            if uk <= 0:
                break
            rx, ry = ponto_bezier(self.ctrl, uk)
            preencher_retangulo(sup, int(rx), int(ry), int(rx), int(ry), self.cor)
        sx = self.p0[0] + (self.p2[0] - self.p0[0]) * u
        sy = self.p0[1] + (self.p2[1] - self.p0[1]) * u
        preencher_circunferencia(sup, int(sx), int(sy), 1, (15, 15, 15))
        x, y = ponto_bezier(self.ctrl, u)
        preencher_circunferencia(sup, int(x), int(y), 1 + int(round(2 * math.sin(math.pi * u))), self.cor)
 
 
# ---------------- Efeitos ----------------
class OndaImpacto:
    def __init__(self, x, y, raio_max=ONDA_RAIO_MAX, duracao=ONDA_DURACAO, nucleo=False,
                 cor1=COR_ONDA, cor2=COR_ONDA_NUCLEO):
        self.x, self.y = int(x), int(y)
        self.raio_max, self.duracao, self.nucleo = raio_max, duracao, nucleo
        self.cor1, self.cor2 = cor1, cor2
        self.t = 0.0
        self.vivo = True
 
    def atualizar(self, dt):
        self.t += dt
        if self.t >= self.duracao:
            self.vivo = False
 
    def desenhar(self, sup):
        p = self.t / self.duracao
        if self.nucleo and p < 0.3:
            preencher_circunferencia(sup, self.x, self.y, int(self.raio_max * (0.3 - p) * 2), self.cor2)
        r1 = int(self.raio_max * p)
        r2 = int(self.raio_max * max(0.0, (p - 0.3) / 0.7))
        if r1 > 0:
            circunferencia_bresenham(sup, self.x, self.y, r1, self.cor1)
        if r2 > 0:
            circunferencia_bresenham(sup, self.x, self.y, r2, self.cor2)
 
 
def onda_escudo(x, y, raio):
    return OndaImpacto(x, y, raio + 9, 0.4, False, COR_ESCUDO, COR_ESCUDO_BRILHO)
 
 
# ---------------- Power-ups ----------------
class PowerUp:
    def __init__(self, x, y, tipo):
        self.x, self.y = float(x), float(y)
        self.tipo = tipo
        self.cor = POWERUP_TIPOS[tipo]
        self.t = POWERUP_TEMPO_VIDA
        self.vivo = True
 
    def atualizar(self, dt, jogador):
        self.t -= dt
        if self.t <= 0:
            self.vivo = False
            return False
        if jogador.vivo and math.hypot(jogador.x - self.x, jogador.y - self.y) <= jogador.raio + POWERUP_RAIO:
            self.aplicar(jogador)
            self.vivo = False
            return True
        return False
 
    def aplicar(self, j):
        if self.tipo == "cura":
            j.vida = min(j.vida + 1, j.vida_max)
        elif self.tipo == "morteiro":
            j.morteiros = min(j.morteiros + MORTEIRO_BONUS, MORTEIRO_MUNICAO_MAX * 2)
        elif self.tipo == "escudo":
            j.ativar_escudo()
 
    def desenhar(self, sup):
        if self.t < 3 and int(self.t * 8) % 2:
            return
        x = int(round(self.x))
        y = int(round(self.y + math.sin(self.t * 5)))
        r = POWERUP_RAIO
        if self.tipo == "cura":
            for o in (0, 1):
                linha_bresenham(sup, x - r, y + o, x + r, y + o, self.cor)
                linha_bresenham(sup, x + o, y - r, x + o, y + r, self.cor)
            _pixel(sup, x, y, COR_PU_BORDA)
        elif self.tipo == "morteiro":
            preencher_circunferencia(sup, x, y, r - 1, self.cor)
            circunferencia_bresenham(sup, x, y, r, COR_PU_BORDA)
        else:
            circunferencia_bresenham(sup, x, y, r, self.cor)
            circunferencia_bresenham(sup, x, y, r - 2, COR_PU_BORDA)
 
 
def sortear_powerup(x, y, chance=POWERUP_CHANCE):
    if random.random() > chance:
        return None
    return PowerUp(x, y, random.choice(list(POWERUP_TIPOS)))
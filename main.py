# main.py
import sys
import math
import pygame
from config import *
from algoritmos_cg import (
    linha_bresenham, preencher_retangulo, preencher_poligono_varredura,
    preencher_circunferencia, desenhar_poligono,
)
from arena import Arena
import sons
from tanques import (
    Jogador, Inimigo, Morteiro, OndaImpacto, PowerUp,
    gerar_pontos_patrulha, sortear_powerup, onda_escudo,
)
 
XMIN, YMIN, XMAX, YMAX = JANELA_JOGO
COR_ESCURO = (38, 42, 56)
COR_LUZ = (255, 245, 215)
CHANCE_PU_MURO = 0.15
DANO_MORTEIRO_INIMIGO = 1
T_FASE_COMPLETA = 1.6
T_BANNER = 2.0
BARRA_INF = 10
TECLA_NOVO_JOGO = pygame.K_n
MENU_OPCOES = ("INICIAR", "TUTORIAL", "ÁUDIO", "SAIR")
LG_W, LG_H = 250, 50
LG_X, LG_Y = (LARGURA - LG_W) // 2, 22
MN_W, MN_H = 200, 148
MN_X, MN_Y = (LARGURA - MN_W) // 2, LG_Y + LG_H + 8
BT_W, BT_H = 150, 22
BT_X = (LARGURA - BT_W) // 2
BT_Y0, BT_PASSO = MN_Y + 14, 30
TU_X, TU_Y, TU_W, TU_H = 34, 30, 412, 210
AU_W, AU_H = 290, 200
AU_X, AU_Y = (LARGURA - AU_W) // 2, 34
AU_ITENS = (("GERAL", "geral"), ("MÚSICA", "musica"), ("TIROS", "tiros"), ("EXPLOSÕES", "explosoes"))
AU_LIN0, AU_PASSO = AU_Y + 48, 28
AU_BAR0, AU_BAR1 = AU_X + 118, AU_X + AU_W - 62
AU_VOLTAR_Y = AU_LIN0 + len(AU_ITENS) * AU_PASSO + 4
TECLAS_OK = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)
 
# ---------- Military GUI ----------
MIL_FUNDO = (182, 204, 114)
MIL_MOLDURA = (102, 128, 38)
MIL_CONTORNO = (42, 54, 14)
MIL_REALCE = (140, 165, 58)
MIL_REBITE = (150, 155, 145)
MIL_TEXTO = (65, 82, 22)
MIL_TITULO = (255, 255, 255)
MIL_TITULO_DERROTA = (235, 30, 30)
MIL_ESP = 5
ESTADOS_FIM = ("vitoria", "derrota", "fase_completa")
 
PM_W, PM_H = 280, 110
PI_W, PI_H = 250, 28
PM_X = (LARGURA - PM_W) // 2
PM_Y = (ALTURA - (PM_H + PI_H - MIL_ESP)) // 2
PI_X = (LARGURA - PI_W) // 2
PI_Y = PM_Y + PM_H - MIL_ESP
 
CONTROLES = ("WASD: Mover | Mouse: Mirar/Atirar | F: Morteiro | V: Farol | TAB: Tutorial | "
             "R: Reiniciar fase | N: Novo jogo | F11: Tela cheia | ESC: Menu")
COR_TUT_TEXTO = (24, 34, 10)
TUT_PASSO = 11
TUT_CONTROLES = (("WASD", "Mover"), ("Mouse", "Mirar/Atirar"), ("F", "Morteiro"), ("V", "Farol"),
                 ("R", "Reiniciar fase"), ("N", "Novo jogo"), ("TAB", "Tutorial"), ("ESC", "Menu"))
TUT_OBJETIVO = ("Destrua todos os tanques inimigos", "para avançar. São 3 fases.")
TUT_MECANICAS = ("Balas ricocheteiam 2x (concreto/árvores)", "Tijolo, caixote e sacos: destrutíveis",
                 "Barril explode em reação em cadeia", "Lama e ouriços reduzem a velocidade",
                 "Trincheira: cruze só pelas pontes", "Vegetação bloqueia a visão inimiga")
TUT_INIMIGOS = ((COR_INI_PADRAO, "Vermelho", "padrão"), (COR_INI_RAPIDO, "Amarelo", "rápido"),
                (COR_INI_ARTILHARIA, "Roxo", "artilharia"))
TUT_POWERUPS = ((COR_PU_CURA, "Verde", "+1 vida"), (COR_PU_MORTEIRO, "Laranja", "+2 morteiros"),
                (COR_PU_ESCUDO, "Azul", "escudo"))
 
 
def _sup_alpha(w, h, cor):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    preencher_retangulo(s, 0, 0, w - 1, h - 1, cor)
    return s
 
 
def _ret(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
 
 
def _fonte(tam, negrito=False):
    f = pygame.font.Font(None, tam)
    f.set_bold(negrito)
    return f
 
 
def placa_militar(b, x, y, w, h):
    x1, y1, e = x + w - 1, y + h - 1, MIL_ESP
    preencher_retangulo(b, x, y, x1, y1, MIL_MOLDURA)
    desenhar_poligono(b, _ret(x, y, x1, y1), MIL_CONTORNO, algoritmo_linha=linha_bresenham)
    desenhar_poligono(b, _ret(x + 1, y + 1, x1 - 1, y1 - 1), MIL_REALCE, algoritmo_linha=linha_bresenham)
    preencher_retangulo(b, x + e, y + e, x1 - e, y1 - e, MIL_FUNDO)
    desenhar_poligono(b, _ret(x + e - 1, y + e - 1, x1 - e + 1, y1 - e + 1), MIL_CONTORNO,
                      algoritmo_linha=linha_bresenham)
    desenhar_poligono(b, _ret(x + e, y + e, x1 - e, y1 - e), MIL_REALCE, algoritmo_linha=linha_bresenham)
    r = e // 2
    for cx, cy in ((x + r + 1, y + r + 1), (x1 - r - 1, y + r + 1),
                   (x + r + 1, y1 - r - 1), (x1 - r - 1, y1 - r - 1)):
        preencher_circunferencia(b, cx, cy, 2, MIL_REBITE)
        linha_bresenham(b, cx - 1, cy, cx + 1, cy, MIL_CONTORNO)
 
 
class Jogo:
    def __init__(self):
        sons.pre_iniciar()
        pygame.init()
        sons.iniciar()
        self.tela_cheia = TELA_CHEIA_INICIAL
        self._criar_tela()
        pygame.display.set_caption(TITULO)
        pygame.mouse.set_visible(False)
        self.buf = pygame.Surface((LARGURA, ALTURA))
        self.relogio = pygame.time.Clock()
        self.f_hud = pygame.font.Font(None, 26)
        self.f_peq = pygame.font.Font(None, 22)
        self.f_ajuda = pygame.font.Font(None, 28)
        self.f_grande = pygame.font.Font(None, 100)
        self.f_titulo = _fonte(84, True)
        self.f_mil = _fonte(30, True)
        self.f_mil_peq = _fonte(24, True)
        self.f_tut = _fonte(23)
        self.f_tut_b = _fonte(23, True)
 
        self.arena = Arena(1)
 
        self.mascara_base = pygame.Surface((LARGURA, ALTURA))
        preencher_retangulo(self.mascara_base, 0, 0, LARGURA - 1, ALTURA - 1, COR_ESCURO)
        preencher_retangulo(self.mascara_base, 0, 0, LARGURA - 1, ALTURA_HUD - 1, (255, 255, 255))
        self.mascara = pygame.Surface((LARGURA, ALTURA))
        self.barra_inf = _sup_alpha(LARGURA, BARRA_INF, (0, 0, 0, 170))
        self.painel = _sup_alpha(320, 150, (8, 10, 14, 225))
        self.faixa = _sup_alpha(LARGURA, 40, (0, 0, 0, 150))
        self.veu = _sup_alpha(LARGURA, ALTURA, (0, 0, 0, 160))
 
        self.visao = False
        self.ajuda = False
        self.t_anim = 0.0
        self.menu_sel = 0
        self.tela_menu = "principal"
        self.audio_sel = 0
        self._arrastando = None
        sons.tocar_musica()
        self.reiniciar()
        self.estado = "menu"
 
    def _criar_tela(self):
        flags = pygame.SCALED | (pygame.FULLSCREEN if self.tela_cheia else 0)
        self.tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA), flags)
 
    def alternar_tela_cheia(self):
        self.tela_cheia = not self.tela_cheia
        try:
            pygame.display.toggle_fullscreen()
        except pygame.error:
            self._criar_tela()
 
    # ---------- fases ----------
    def reiniciar(self):
        self.jogador = None
        self.abatidos = 0
        self.carregar_fase(1)
 
    def reiniciar_fase(self):
        self.jogador = None
        self.abatidos = self.abatidos_fase
        self.carregar_fase(self.fase)
 
    def carregar_fase(self, n):
        self.arena.carregar_fase(n)
        self.fase = self.arena.fase
        self.abatidos_fase = self.abatidos
        self.patrulha = gerar_pontos_patrulha(self.arena)
        sx, sy = self.arena.spawn_jogador()
        if self.jogador is None:
            self.jogador = Jogador(sx, sy)
        else:
            j = self.jogador
            j.x, j.y = sx, sy
            j.vida = min(j.vida + 1, j.vida_max)
            j.invencivel = 1.0
        self.inimigos = [Inimigo(x, y, t, e) for x, y, t, e in self.arena.spawns_inimigos()[:INI_MAX]]
        self.balas, self.morteiros, self.ondas, self.powerups = [], [], [], []
        self.estado = "jogando"
        self.t_estado = 0.0
        self.banner_t = T_BANNER
 
    # ---------- entrada ----------
    def mira(self):
        mx, my = pygame.mouse.get_pos()
        return (min(max(mx // ESCALA, XMIN), XMAX), min(max(my // ESCALA, YMIN), YMAX))
 
    def eventos(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.sair()
            if self.estado == "menu":
                self._eventos_menu(e)
                continue
            if e.type == pygame.KEYDOWN and e.key == TECLA_SAIR:
                self.ajuda = False
                self.estado, self.tela_menu = "menu", "principal"
                sons.tocar("menu_mover")
                continue
            if e.type == pygame.KEYDOWN:
                if e.key == TECLA_TELA_CHEIA:
                    self.alternar_tela_cheia()
                elif e.key == TECLA_REINICIAR:
                    if self.estado == "vitoria":
                        self.reiniciar()
                    else:
                        self.reiniciar_fase()
                elif e.key == TECLA_NOVO_JOGO:
                    self.reiniciar()
                elif e.key == TECLA_VISAO:
                    self.visao = not self.visao
                elif e.key == TECLA_CONTROLES:
                    self.ajuda = not self.ajuda
                elif e.key == TECLA_MORTEIRO and self.estado == "jogando" and not self.ajuda:
                    m = self.jogador.lancar_morteiro(*self.mira())
                    if m:
                        self.morteiros.append(m)
 
    def sair(self):
        pygame.quit()
        sys.exit()
 
    # ---------- menu ----------
    def _menu_item_em(self, mx, my):
        x, y = mx // ESCALA, my // ESCALA
        for i in range(len(MENU_OPCOES)):
            by = BT_Y0 + i * BT_PASSO
            if BT_X <= x < BT_X + BT_W and by <= y < by + BT_H:
                return i
        return None
 
    def _menu_mover(self, d):
        self.menu_sel = (self.menu_sel + d) % len(MENU_OPCOES)
        sons.tocar("menu_mover")
 
    def _menu_escolher(self):
        sons.tocar("menu_ok")
        op = MENU_OPCOES[self.menu_sel]
        if op == "INICIAR":
            self.reiniciar()
            self.jogador.cadencia_t = 0.3  # o clique do menu não dispara
        elif op == "TUTORIAL":
            self.tela_menu = "tutorial"
        elif op == "ÁUDIO":
            self.tela_menu, self.audio_sel = "audio", 0
        else:
            self.sair()
 
    def _eventos_menu(self, e):
        if e.type == pygame.KEYDOWN and e.key == TECLA_TELA_CHEIA:
            self.alternar_tela_cheia()
            return
        if self.tela_menu == "tutorial":
            if e.type == pygame.KEYDOWN or (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1):
                self.tela_menu = "principal"
                sons.tocar("menu_mover")
            return
        if self.tela_menu == "audio":
            self._eventos_audio(e)
            return
        if e.type == pygame.KEYDOWN:
            if e.key == TECLA_SAIR:
                self.sair()
            elif e.key in (pygame.K_w, pygame.K_UP):
                self._menu_mover(-1)
            elif e.key in (pygame.K_s, pygame.K_DOWN):
                self._menu_mover(1)
            elif e.key in TECLAS_OK:
                self._menu_escolher()
        elif e.type == pygame.MOUSEMOTION:
            i = self._menu_item_em(*e.pos)
            if i is not None and i != self.menu_sel:
                self.menu_sel = i
                sons.tocar("menu_mover")
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            i = self._menu_item_em(*e.pos)
            if i is not None:
                self.menu_sel = i
                self._menu_escolher()
 
    # ---------- áudio ----------
    def _audio_item_em(self, mx, my):
        x, y = mx // ESCALA, my // ESCALA
        for i in range(len(AU_ITENS)):
            ly = AU_LIN0 + i * AU_PASSO
            if AU_X + 10 <= x < AU_X + AU_W - 10 and ly - 9 <= y <= ly + 9:
                return i
        vx = (LARGURA - 120) // 2
        if vx <= x < vx + 120 and AU_VOLTAR_Y <= y < AU_VOLTAR_Y + BT_H:
            return len(AU_ITENS)
        return None
 
    def _audio_ajustar(self, i, valor):
        chave = AU_ITENS[i][1]
        antes = sons.VOL[chave]
        sons.definir_volume(chave, valor)
        if int(round(sons.VOL[chave] * 10)) != int(round(antes * 10)):
            sons.tocar({"tiros": "tiro", "explosoes": "explosao"}.get(chave, "menu_mover"), forcar=True)
 
    def _audio_bar_valor(self, mx):
        return (mx // ESCALA - AU_BAR0) / (AU_BAR1 - AU_BAR0)
 
    def _eventos_audio(self, e):
        n = len(AU_ITENS) + 1
        if e.type == pygame.KEYDOWN:
            if e.key == TECLA_SAIR or (e.key in TECLAS_OK and self.audio_sel == len(AU_ITENS)):
                self.tela_menu = "principal"
                sons.tocar("menu_ok")
            elif e.key in (pygame.K_w, pygame.K_UP):
                self.audio_sel = (self.audio_sel - 1) % n
                sons.tocar("menu_mover")
            elif e.key in (pygame.K_s, pygame.K_DOWN):
                self.audio_sel = (self.audio_sel + 1) % n
                sons.tocar("menu_mover")
            elif e.key in (pygame.K_a, pygame.K_LEFT, pygame.K_d, pygame.K_RIGHT) and self.audio_sel < len(AU_ITENS):
                d = -0.1 if e.key in (pygame.K_a, pygame.K_LEFT) else 0.1
                self._audio_ajustar(self.audio_sel, sons.VOL[AU_ITENS[self.audio_sel][1]] + d)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            i = self._audio_item_em(*e.pos)
            if i == len(AU_ITENS):
                self.tela_menu = "principal"
                sons.tocar("menu_ok")
            elif i is not None:
                self.audio_sel = self._arrastando = i
                self._audio_ajustar(i, self._audio_bar_valor(e.pos[0]))
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            self._arrastando = None
        elif e.type == pygame.MOUSEMOTION:
            if self._arrastando is not None:
                self._audio_ajustar(self._arrastando, self._audio_bar_valor(e.pos[0]))
            else:
                i = self._audio_item_em(*e.pos)
                if i is not None and i != self.audio_sel:
                    self.audio_sel = i
                    sons.tocar("menu_mover")
 
    # ---------- combate ----------
    def _abater(self, t):
        sons.tocar("explosao")
        self.arena.adicionar_cratera(t.x, t.y, 6)
        self.ondas.append(OndaImpacto(t.x, t.y, 12, 0.5, True))
        if isinstance(t, Inimigo):
            self.abatidos += 1
            pu = PowerUp(t.x, t.y, "escudo") if t.escudo_inicial else sortear_powerup(t.x, t.y)
            if pu:
                self.powerups.append(pu)
 
    def _ferir(self, t, dano, x=None, y=None):
        if not t.vivo:
            return
        r = t.sofrer_dano(dano)
        if r:
            sons.tocar("dano_inimigo" if isinstance(t, Inimigo) else "dano_jogador")
        if r == "escudo":
            self.ondas.append(onda_escudo(t.x, t.y, t.raio))
        elif r:
            self.ondas.append(OndaImpacto(t.x if x is None else x, t.y if y is None else y))
            if not t.vivo:
                self._abater(t)
 
    def _muro_destruido(self, m):
        cx, cy = m.centro
        self.ondas.append(OndaImpacto(cx, cy, 10, 0.4, True))
        pu = sortear_powerup(cx, cy, CHANCE_PU_MURO)
        if pu and not self.arena.colide_circulo(cx, cy, POWERUP_RAIO):
            self.powerups.append(pu)
 
    def _explosao(self, x, y, r, dano_jog, dano_ini, dano_muro):
        sons.tocar("explosao")
        self.arena.adicionar_cratera(x, y, CRATERA_RAIO_MORTEIRO)
        self.ondas.append(OndaImpacto(x, y, r, 0.5, True))
        for muro in self.arena.muros_em_raio(x, y, r):
            if muro.destrutivel and self.arena.danificar_muro(muro, dano_muro):
                self._muro_destruido(muro)
        if dano_ini:
            for ini in self.inimigos:
                if ini.vivo and math.hypot(ini.x - x, ini.y - y) <= r + ini.raio:
                    self._ferir(ini, dano_ini)
        j = self.jogador
        if dano_jog and j.vivo and math.hypot(j.x - x, j.y - y) <= r + j.raio:
            self._ferir(j, dano_jog)
        for b in self.arena.barris_em_raio(x, y, r):  # reação em cadeia
            self._explodir_barril(b)
 
    def _explodir_barril(self, b):
        pos = self.arena.explodir_barril(b)
        if pos:
            self._explosao(*pos, BARRIL_RAIO_EXPLOSAO, BARRIL_DANO, BARRIL_DANO, BARRIL_DANO_MURO)
 
    def _explodir_morteiro(self, m):
        tx, ty = m.destino
        if m.dono == "jogador":
            self._explosao(tx, ty, m.raio_explosao, 0, MORTEIRO_DANO, MORTEIRO_DANO_MURO)
        else:
            self._explosao(tx, ty, m.raio_explosao, DANO_MORTEIRO_INIMIGO, 0, MORTEIRO_DANO_MURO)
 
    # ---------- lógica ----------
    def atualizar(self, dt):
        self.t_anim += dt
        for o in self.ondas:
            o.atualizar(dt)
        self.ondas = [o for o in self.ondas if o.vivo]
        self.banner_t = max(0.0, self.banner_t - dt)
 
        if self.estado == "menu":
            return
        if self.estado == "fase_completa":
            self.t_estado -= dt
            if self.t_estado <= 0:
                self.carregar_fase(self.fase + 1)
            return
        if self.estado != "jogando" or self.ajuda:
            return
 
        j = self.jogador
        k = pygame.key.get_pressed()
        j.mover(k[TECLA_DIREITA] - k[TECLA_ESQUERDA], k[TECLA_BAIXO] - k[TECLA_CIMA], dt, self.arena)
        j.mirar(*self.mira())
        j.atualizar(dt)
        if pygame.mouse.get_pressed()[MOUSE_TIRO - 1] and j.pode_atirar():
            self.balas.append(j.atirar(COR_BALA, "jogador", JOG_CADENCIA))
 
        for ini in self.inimigos:
            p = ini.atualizar(dt, self.arena, j, self.patrulha)
            if isinstance(p, Morteiro):
                self.morteiros.append(p)
            elif p is not None:
                self.balas.append(p)
 
        for b in self.balas:
            alvos = self.inimigos if b.dono == "jogador" else [j]
            res = b.atualizar(dt, self.arena, alvos)
            if res == "muro":
                self.arena.adicionar_cratera(b.px, b.py, CRATERA_RAIO_BALA)
                if b.muro_destruido:
                    self._muro_destruido(b.muro_destruido)
            elif res == "barril":
                self._explodir_barril(b.barril)
            elif res == "ricochete":
                self.ondas.append(OndaImpacto(b.x, b.y, 3, 0.15))
            elif res is not None:
                self._ferir(res, BALA_DANO, b.x, b.y)
        self.balas = [b for b in self.balas if b.vivo]
 
        for m in self.morteiros:
            m.atualizar(dt)
            if m.explodiu:
                self._explodir_morteiro(m)
        self.morteiros = [m for m in self.morteiros if m.ativo]
 
        for pu in self.powerups:
            if pu.atualizar(dt, j):
                cor = pu.cor
                self.ondas.append(OndaImpacto(pu.x, pu.y, 9, 0.3, False, cor, COR_ONDA_NUCLEO))
        self.powerups = [p for p in self.powerups if p.vivo]
        self.inimigos = [i for i in self.inimigos if i.vivo]
 
        if not j.vivo:
            self.estado = "derrota"
        elif not self.inimigos:
            if self.fase >= NUM_FASES:
                self.estado = "vitoria"
            else:
                self.estado = "fase_completa"
                self.t_estado = T_FASE_COMPLETA
                self.balas.clear()
                self.morteiros.clear()
 
    # ---------- desenho ----------
    def aplicar_visao(self):
        m, j = self.mascara, self.jogador
        m.blit(self.mascara_base, (0, 0))
        ox, oy = int(j.x), int(j.y)
        meio = math.radians(VISAO_ANGULO) / 2
        n = VISAO_RAIOS
        pts = [(ox, oy)]
        for i in range(n):
            a = j.ang_canhao - meio + 2 * meio * i / (n - 1)
            ex, ey = int(ox + math.cos(a) * VISAO_ALCANCE), int(oy + math.sin(a) * VISAO_ALCANCE)
            fim = (ox, oy)
            for px, py in linha_bresenham(None, ox, oy, ex, ey) or ():
                fim = (px, py)
                if self.arena.colide_ponto(px, py):
                    break
            pts.append(fim)
        preencher_poligono_varredura(m, pts, COR_LUZ)
        preencher_circunferencia(m, ox, oy, 18, COR_LUZ)
        self.buf.blit(m, (0, 0), special_flags=pygame.BLEND_MULT)
 
    def desenhar_mira(self):
        # desenhada direto na tela (após os textos), em blocos ESCALA x ESCALA
        x, y = self.mira()
        E, t = ESCALA, self.tela
        segs = ((x - 6, y, x - 2, y, COR_MIRA), (x + 2, y, x + 6, y, COR_MIRA),
                (x, y - 6, x, y - 2, COR_MIRA), (x, y + 2, x, y + 6, COR_MIRA), (x, y, x, y, COR_BALA))
        for x1, y1, x2, y2, cor in segs:
            for px, py in linha_bresenham(None, x1, y1, x2, y2):
                preencher_retangulo(t, px * E, py * E, px * E + E - 1, py * E + E - 1, cor)
 
    def _desenhar_painel_fim(self, b):
        placa_militar(b, PI_X, PI_Y, PI_W, PI_H)
        placa_militar(b, PM_X, PM_Y, PM_W, PM_H)
        ys = PM_Y + int(PM_H * 0.47)
        linha_bresenham(b, PM_X + 24, ys, PM_X + PM_W - 25, ys, MIL_MOLDURA)
        linha_bresenham(b, PM_X + 24, ys + 1, PM_X + PM_W - 25, ys + 1, MIL_REALCE)
 
    def _botao(self, b, x, y, w, h, ativo):
        x1, y1 = x + w - 1, y + h - 1
        preencher_retangulo(b, x, y, x1, y1, MIL_MOLDURA if ativo else MIL_REALCE)
        desenhar_poligono(b, _ret(x, y, x1, y1), MIL_CONTORNO, algoritmo_linha=linha_bresenham)
        linha_bresenham(b, x + 1, y + 1, x1 - 1, y + 1, MIL_FUNDO if ativo else (200, 218, 140))
        linha_bresenham(b, x + 1, y1 - 1, x1 - 1, y1 - 1, MIL_CONTORNO)
        if ativo:
            self._setas(b, x, x1, (y + y1) // 2)
 
    def _setas(self, b, x0, x1, cy):
        for k in range(4):
            linha_bresenham(b, x0 - 9 + k, cy - 3 + k, x0 - 9 + k, cy + 3 - k, COR_HUD_DESTAQUE)
            linha_bresenham(b, x1 + 9 - k, cy - 3 + k, x1 + 9 - k, cy + 3 - k, COR_HUD_DESTAQUE)
 
    def _separador(self, b, x0, x1, y):
        linha_bresenham(b, x0, y, x1, y, MIL_MOLDURA)
        linha_bresenham(b, x0, y + 1, x1, y + 1, MIL_REALCE)
 
    def _estrela(self, b, cx, cy, r):
        pts = []
        for k in range(10):
            a = -math.pi / 2 + k * math.pi / 5
            rr = r if k % 2 == 0 else r * 0.42
            pts.append((int(round(cx + math.cos(a) * rr)), int(round(cy + math.sin(a) * rr))))
        preencher_poligono_varredura(b, [(x + 1, y + 1) for x, y in pts], MIL_CONTORNO)
        preencher_poligono_varredura(b, pts, MIL_TITULO)
        desenhar_poligono(b, pts, MIL_CONTORNO, algoritmo_linha=linha_bresenham)
 
    def _logo_buf(self, b):
        placa_militar(b, LG_X, LG_Y, LG_W, LG_H)
        cy = LG_Y + LG_H // 2
        for x in (LG_X + 26, LG_X + LG_W - 27):
            self._estrela(b, x, cy, 10)
        for k in range(3):  # divisas
            y = LG_Y + LG_H - 11 + k * 2
            linha_bresenham(b, LG_X + 60, y, LG_X + LG_W - 61, y, MIL_MOLDURA if k != 1 else MIL_REALCE)
 
    def _tutorial_layout(self):
        # itens: (tipo, x, y, ...) em coordenadas do buffer
        meio = TU_X + TU_W // 2
        xe, xd = TU_X + 18, meio + 14
        y0 = TU_Y + 44
        it = [("h", xe, y0, "CONTROLES")]
        for k, (tecla, desc) in enumerate(TUT_CONTROLES):
            it.append(("k", xe + 4 + (k // 4) * 92, y0 + TUT_PASSO * (1 + k % 4) + 2, tecla, desc))
        y = y0 + TUT_PASSO * 6 + 4
        it.append(("h", xe, y, "OBJETIVO"))
        for k, txt in enumerate(TUT_OBJETIVO):
            it.append(("t", xe + 4, y + TUT_PASSO * (k + 1) + 2, txt))
        it.append(("h", xd, y0, "MECÂNICAS"))
        for k, txt in enumerate(TUT_MECANICAS):
            it.append(("b", xd + 4, y0 + TUT_PASSO * (k + 1) + 2, txt))
        y = y0 + TUT_PASSO * (len(TUT_MECANICAS) + 1) + 8
        it.append(("h", xd, y, "INIMIGOS / POWER-UPS"))
        for col, lista in enumerate((TUT_INIMIGOS, TUT_POWERUPS)):
            for k, (cor, nome, desc) in enumerate(lista):
                it.append(("c", xd + 4 + col * 84, y + TUT_PASSO * (k + 1) + 2, cor, nome, desc))
        it.append(("t", xd + 4, y + TUT_PASSO * 4 + 4, "Inimigo com escudo deixa um ESCUDO"))
        return it
 
    def _tutorial_buf(self, b):
        placa_militar(b, TU_X, TU_Y, TU_W, TU_H)
        self._separador(b, TU_X + 20, TU_X + TU_W - 21, TU_Y + 30)
        meio = TU_X + TU_W // 2
        linha_bresenham(b, meio, TU_Y + 40, meio, TU_Y + TU_H - 16, MIL_MOLDURA)
        linha_bresenham(b, meio + 1, TU_Y + 40, meio + 1, TU_Y + TU_H - 16, MIL_REALCE)
        for item in self._tutorial_layout():
            tipo, x, y = item[:3]
            if tipo == "h":
                preencher_retangulo(b, x - 5, y - 4, x - 3, y + 4, MIL_MOLDURA)
            elif tipo == "b":
                preencher_retangulo(b, x, y - 1, x + 1, y, COR_TUT_TEXTO)
            elif tipo == "c":
                preencher_retangulo(b, x, y - 3, x + 5, y + 2, item[3])
                desenhar_poligono(b, _ret(x - 1, y - 4, x + 6, y + 3), COR_TUT_TEXTO, algoritmo_linha=linha_bresenham)
 
    def _texto_par(self, forte, fraco, x, y):
        self.texto(forte, self.f_tut_b, COR_TUT_TEXTO, x, y)
        self.texto(fraco, self.f_tut, COR_TUT_TEXTO, x + self.f_tut_b.size(forte)[0] + 8, y)
 
    def _tutorial_textos(self):
        E = ESCALA
        self.texto_contorno("TUTORIAL", self.f_mil, MIL_TITULO, LARGURA_JANELA // 2, (TU_Y + 17) * E, 2)
        for item in self._tutorial_layout():
            tipo, x, y = item[:3]
            if tipo == "h":
                self.texto(item[3], self.f_mil, MIL_CONTORNO, x * E, y * E)
            elif tipo == "k":
                self._texto_par(item[3], item[4], x * E, y * E)
            elif tipo == "b":
                self.texto(item[3], self.f_tut, COR_TUT_TEXTO, (x + 5) * E, y * E)
            elif tipo == "c":
                self._texto_par(item[4], item[5], (x + 10) * E, y * E)
            else:
                self.texto(item[3], self.f_tut, COR_TUT_TEXTO, x * E, y * E)
 
    def _audio_buf(self, b):
        placa_militar(b, AU_X, AU_Y, AU_W, AU_H)
        self._separador(b, AU_X + 20, AU_X + AU_W - 21, AU_Y + 30)
        for i, (_, chave) in enumerate(AU_ITENS):
            ly = AU_LIN0 + i * AU_PASSO
            if i == self.audio_sel:
                preencher_retangulo(b, AU_X + 12, ly - 9, AU_X + AU_W - 13, ly + 9, MIL_REALCE)
                desenhar_poligono(b, _ret(AU_X + 12, ly - 9, AU_X + AU_W - 13, ly + 9), MIL_MOLDURA,
                                  algoritmo_linha=linha_bresenham)
            v = sons.VOL[chave]
            preencher_retangulo(b, AU_BAR0, ly - 3, AU_BAR1, ly + 3, MIL_CONTORNO)
            xv = AU_BAR0 + int(round(v * (AU_BAR1 - AU_BAR0)))
            if xv > AU_BAR0:
                preencher_retangulo(b, AU_BAR0 + 1, ly - 2, xv, ly + 2, COR_HUD_DESTAQUE if i == self.audio_sel else MIL_MOLDURA)
            for k in range(1, 10):  # marcas de 10%
                xm = AU_BAR0 + k * (AU_BAR1 - AU_BAR0) // 10
                linha_bresenham(b, xm, ly + 4, xm, ly + 5, MIL_CONTORNO)
            preencher_retangulo(b, xv - 1, ly - 5, xv + 1, ly + 5, MIL_TITULO)
            desenhar_poligono(b, _ret(xv - 2, ly - 6, xv + 2, ly + 6), MIL_CONTORNO, algoritmo_linha=linha_bresenham)
        vx = (LARGURA - 120) // 2
        voltar = self.audio_sel == len(AU_ITENS)
        self._botao(b, vx, AU_VOLTAR_Y, 120, BT_H, voltar)
 
    def _audio_textos(self):
        E = ESCALA
        self.texto_contorno("ÁUDIO", self.f_mil, MIL_TITULO, LARGURA_JANELA // 2, (AU_Y + 16) * E, 2)
        for i, (nome, chave) in enumerate(AU_ITENS):
            ly = AU_LIN0 + i * AU_PASSO
            cor = MIL_CONTORNO if i == self.audio_sel else MIL_TEXTO
            self.texto(nome, self.f_mil_peq, cor, (AU_X + 22) * E, ly * E)
            v = sons.VOL[chave]
            txt = "MUDO" if v <= 0 else f"{int(round(v * 100))}%"
            self.texto(txt, self.f_mil_peq, cor, (AU_BAR1 + 10) * E, ly * E)
        cor = MIL_TITULO if self.audio_sel == len(AU_ITENS) else MIL_TEXTO
        self.texto("VOLTAR", self.f_mil, cor, LARGURA_JANELA // 2, (AU_VOLTAR_Y + BT_H // 2) * E, True)
 
    def desenhar_menu(self):
        b = self.buf
        self.arena.desenhar(b)
        b.blit(self.veu, (0, 0))
        tm = self.tela_menu
        if tm == "tutorial":
            self._tutorial_buf(b)
        elif tm == "audio":
            self._audio_buf(b)
        else:
            self._logo_buf(b)
            placa_militar(b, MN_X, MN_Y, MN_W, MN_H)
            for i in range(len(MENU_OPCOES)):
                self._botao(b, BT_X, BT_Y0 + i * BT_PASSO, BT_W, BT_H, i == self.menu_sel)
        b.blit(self.barra_inf, (0, ALTURA - BARRA_INF))
        pygame.transform.scale(b, (LARGURA_JANELA, ALTURA_JANELA), self.tela)
        E, cx = ESCALA, LARGURA_JANELA // 2
        if tm == "tutorial":
            self._tutorial_textos()
            dica = "Pressione qualquer tecla ou clique para voltar"
        elif tm == "audio":
            self._audio_textos()
            dica = "W/S: escolher   |   A/D ou arraste a barra: ajustar   |   ESC: voltar"
        else:
            self.texto_contorno("TankCG", self.f_titulo, MIL_TITULO, cx, (LG_Y + LG_H // 2 - 3) * E)
            for i, op in enumerate(MENU_OPCOES):
                cor = MIL_TITULO if i == self.menu_sel else MIL_TEXTO
                self.texto(op, self.f_mil, cor, cx, (BT_Y0 + i * BT_PASSO + BT_H // 2) * E, True)
            dica = "W/S ou setas: escolher   |   ENTER ou clique: confirmar   |   ESC: sair"
        self.texto(dica, self.f_peq, (170, 178, 185), cx, (ALTURA - BARRA_INF // 2) * E, True)
        self.desenhar_mira()
        pygame.display.flip()
 
    def desenhar_hud_buf(self):
        b, j = self.buf, self.jogador
        preencher_retangulo(b, 0, 0, LARGURA - 1, ALTURA_HUD - 1, COR_HUD_FUNDO)
        linha_bresenham(b, 0, ALTURA_HUD - 1, LARGURA - 1, ALTURA_HUD - 1, COR_HUD_LINHA)
        for i in range(j.vida_max):
            x = 70 + i * 9
            cor = (COR_VIDA_OK if j.vida > 1 else COR_VIDA_BAIXA) if i < j.vida else (50, 50, 55)
            preencher_retangulo(b, x, 5, x + 6, 11, cor)
        if j.escudo:
            w = int(20 * max(0.0, j.escudo_t) / ESCUDO_DURACAO)
            preencher_retangulo(b, 138, 7, 158, 9, (40, 50, 60))
            if w > 0:
                preencher_retangulo(b, 138, 7, 138 + w, 9, COR_ESCUDO)
        n = max(MORTEIRO_MUNICAO_MAX, j.morteiros)
        for i in range(n):
            preencher_circunferencia(b, 218 + i * 7, 7, 2, COR_MORTEIRO if i < j.morteiros else (50, 50, 55))
        if j.morteiros < MORTEIRO_MUNICAO_MAX:
            w = int(20 * j.recarga / MORTEIRO_RECARGA)
            preencher_retangulo(b, 215, 12, 235, 12, (50, 50, 55))
            if w > 0:
                preencher_retangulo(b, 215, 12, 215 + w, 12, COR_HUD_DESTAQUE)
        b.blit(self.barra_inf, (0, ALTURA - BARRA_INF))
        if self.banner_t > 0 and self.estado == "jogando":
            b.blit(self.faixa, (0, ALTURA // 2 - 20))
        if self.ajuda:
            b.blit(self.veu, (0, 0))
            self._tutorial_buf(b)
        if self.estado in ESTADOS_FIM:
            b.blit(self.veu, (0, 0))
            self._desenhar_painel_fim(b)
 
    def texto(self, txt, fonte, cor, x, y, centro=False):
        s = fonte.render(txt, True, cor)
        r = s.get_rect()
        if centro:
            r.center = (x, y)
        else:
            r.midleft = (x, y)
        self.tela.blit(s, r)
 
    def texto_contorno(self, txt, fonte, cor, x, y, esp=3):
        self.texto(txt, fonte, (0, 0, 0), x + esp + 1, y + esp + 1, True)
        for dx in (-esp, 0, esp):
            for dy in (-esp, 0, esp):
                if dx or dy:
                    self.texto(txt, fonte, (0, 0, 0), x + dx, y + dy, True)
        self.texto(txt, fonte, cor, x, y, True)
 
    def _textos_fim(self, cx):
        E = ESCALA
        topo, alt = PM_Y * E, PM_H * E
        cor_t = MIL_TITULO
        if self.estado == "vitoria":
            titulo, sub = "VITÓRIA", "MISSÃO CUMPRIDA - ARENA DOMINADA"
            aviso = "R / N: Novo jogo   |   ESC: Menu"
        elif self.estado == "derrota":
            titulo, sub = "DERROTA", "TANQUE ABATIDO EM COMBATE"
            aviso = "R: Repetir fase   |   N: Novo jogo   |   ESC: Menu"
            cor_t = MIL_TITULO_DERROTA
        else:
            titulo, sub = f"FASE {self.fase}", "SETOR LIMPO - AVANÇANDO"
            aviso = f"Preparando FASE {self.fase + 1}..."
        self.texto_contorno(titulo, self.f_titulo, cor_t, cx, topo + int(alt * 0.27))
        self.texto(sub, self.f_mil, MIL_TEXTO, cx, topo + int(alt * 0.60), True)
        self.texto(f"FASE ALCANÇADA: {self.fase}/{NUM_FASES}     INIMIGOS DESTRUÍDOS: {self.abatidos}",
                   self.f_mil_peq, MIL_TEXTO, cx, topo + int(alt * 0.79), True)
        if int(self.t_anim * 2.5) % 2 == 0:
            self.texto(aviso, self.f_mil_peq, MIL_TEXTO, cx,
                       (PI_Y + MIL_ESP + (PI_H - MIL_ESP) // 2) * E, True)
 
    def desenhar_textos(self):
        E = ESCALA
        yh = ALTURA_HUD * E // 2
        cx, cy = LARGURA_JANELA // 2, ALTURA_JANELA // 2
        self.texto(f"FASE {self.fase}/{NUM_FASES}", self.f_hud, COR_HUD_DESTAQUE, 4 * E, yh)
        self.texto("VIDA", self.f_hud, COR_HUD_TEXTO, 52 * E, yh)
        if self.jogador.escudo:
            self.texto("ESCUDO", self.f_hud, COR_ESCUDO, 112 * E, yh)
        self.texto("MORTEIROS", self.f_hud, COR_HUD_TEXTO, 178 * E, yh)
        self.texto(f"INIMIGOS: {len(self.inimigos)}", self.f_hud, COR_INIMIGO_DET, 262 * E, yh)
        if self.visao:
            self.texto("FAROL", self.f_hud, COR_LUZ, 340 * E, yh)
        self.texto(CONTROLES, self.f_peq, (170, 178, 185), cx, (ALTURA - BARRA_INF // 2) * E, True)
 
        if self.banner_t > 0 and self.estado == "jogando":
            self.texto(f"FASE {self.fase}", self.f_grande, COR_HUD_TEXTO, cx, cy, True)
 
        if self.ajuda:
            self._tutorial_textos()
 
        if self.estado in ESTADOS_FIM:
            self._textos_fim(cx)
 
    def desenhar(self):
        if self.estado == "menu":
            self.desenhar_menu()
            return
        b = self.buf
        self.arena.desenhar(b)
        jogando = self.estado == "jogando" and not self.ajuda
        if jogando and self.jogador.vivo:
            self.jogador.desenhar_trajetoria(b, self.arena)
        for pu in self.powerups:
            pu.desenhar(b)
        for ini in self.inimigos:
            ini.desenhar(b)
        if self.jogador.vivo:
            self.jogador.desenhar(b)
        for bl in self.balas:
            bl.desenhar(b, self.arena)
        for m in self.morteiros:
            m.desenhar(b)
        for o in self.ondas:
            o.desenhar(b)
        if self.visao and self.jogador.vivo:
            self.aplicar_visao()
        self.desenhar_hud_buf()
        pygame.transform.scale(b, (LARGURA_JANELA, ALTURA_JANELA), self.tela)
        self.desenhar_textos()
        if jogando or self.ajuda:
            self.desenhar_mira()
        pygame.display.flip()
 
    def rodar(self):
        while True:
            dt = min(self.relogio.tick(FPS) / 1000.0, 0.05)
            self.eventos()
            self.atualizar(dt)
            self.desenhar()
 
 
if __name__ == "__main__":
    Jogo().rodar()
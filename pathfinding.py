# pathfinding.py
import heapq
import math
from config import JANELA_JOGO

TAM_CELULA = 16
CUSTO_SLOW = 3.0
DIAG = 1.414
MAX_NOS = 2500
PASSO_AMOSTRA = 4.0

XMIN, YMIN, XMAX, YMAX = JANELA_JOGO
COLS = (XMAX - XMIN + TAM_CELULA) // TAM_CELULA
LINS = (YMAX - YMIN + TAM_CELULA) // TAM_CELULA
_VIZ = ((1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
        (1, 1, DIAG), (1, -1, DIAG), (-1, 1, DIAG), (-1, -1, DIAG))


def _centro(c):
    return (min(XMIN + c[0] * TAM_CELULA + TAM_CELULA / 2, XMAX),
            min(YMIN + c[1] * TAM_CELULA + TAM_CELULA / 2, YMAX))


def _celula(x, y):
    i = int((x - XMIN) // TAM_CELULA)
    j = int((y - YMIN) // TAM_CELULA)
    return (min(max(i, 0), COLS - 1), min(max(j, 0), LINS - 1))


def _h(a, b):
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return dx + dy + (DIAG - 2) * min(dx, dy)


class _Grade:
    # cache lazy por chamada: reflete muros quebrados/pontes no momento do cálculo
    def __init__(self, arena, r):
        self.arena, self.r = arena, r
        self._livre, self._mult = {}, {}

    def livre(self, c):
        v = self._livre.get(c)
        if v is None:
            v = (0 <= c[0] < COLS and 0 <= c[1] < LINS
                 and not self.arena.colide_circulo(*_centro(c), self.r))
            self._livre[c] = v
        return v

    def mult(self, c):
        v = self._mult.get(c)
        if v is None:
            v = self._mult[c] = CUSTO_SLOW if self.arena.fator_terreno(*_centro(c)) < 1.0 else 1.0
        return v


def _livre_proxima(g, c, raio_max=3):
    if g.livre(c):
        return c
    for r in range(1, raio_max + 1):
        melhor, md = None, None
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                if max(abs(dx), abs(dy)) != r:
                    continue
                v = (c[0] + dx, c[1] + dy)
                if g.livre(v):
                    d = dx * dx + dy * dy
                    if md is None or d < md:
                        melhor, md = v, d
        if melhor:
            return melhor
    return None


def _astar(g, ini, fim):
    aberto = [(_h(ini, fim), 0.0, ini)]
    custo, pai = {ini: 0.0}, {ini: None}
    melhor, melhor_h, n = ini, _h(ini, fim), 0
    while aberto and n < MAX_NOS:
        _, gc, c = heapq.heappop(aberto)
        if gc > custo[c]:
            continue
        n += 1
        if c == fim:
            melhor = c
            break
        hc = _h(c, fim)
        if hc < melhor_h:
            melhor, melhor_h = c, hc
        for dx, dy, p in _VIZ:
            v = (c[0] + dx, c[1] + dy)
            if not g.livre(v):
                continue
            if dx and dy and not (g.livre((c[0] + dx, c[1])) and g.livre((c[0], c[1] + dy))):
                continue  # sem cortar quina
            ng = gc + p * g.mult(v)
            if ng < custo.get(v, math.inf):
                custo[v], pai[v] = ng, c
                heapq.heappush(aberto, (ng + _h(v, fim), ng, v))
    cam, c = [], melhor
    while c is not None:
        cam.append(c)
        c = pai[c]
    cam.reverse()
    return cam


def _custo_reta(arena, a, b, r):
    d = math.hypot(b[0] - a[0], b[1] - a[1])
    n = max(1, int(d / PASSO_AMOSTRA))
    tot = 0.0
    for k in range(1, n + 1):
        t = k / n
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        if arena.colide_circulo(x, y, r):
            return None
        tot += CUSTO_SLOW if arena.fator_terreno(x, y) < 1.0 else 1.0
    return tot * d / n / TAM_CELULA


def suavizar(arena, pts, r, g=None):
    # string pulling: atalho só se livre e não mais caro (respeita custo da lama)
    if len(pts) <= 2:
        return pts[:]
    acum = [0.0]
    for k in range(1, len(pts)):
        a, b = pts[k - 1], pts[k]
        m = g.mult(_celula(*b)) if g else 1.0
        acum.append(acum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]) / TAM_CELULA * m)
    out, i, n = [pts[0]], 0, len(pts)
    while i < n - 1:
        j = i + 1
        while j + 1 < n:
            c = _custo_reta(arena, pts[i], pts[j + 1], r)
            if c is None or c > acum[j + 1] - acum[i] + 0.05:
                break
            j += 1
        out.append(pts[j])
        i = j
    return out


def calcular_caminho(arena, origem, destino, raio_tanque=8):
    g = _Grade(arena, raio_tanque)
    c_ori, c_dst = _celula(*origem), _celula(*destino)
    ini, fim = _livre_proxima(g, c_ori), _livre_proxima(g, c_dst)
    if ini is None or fim is None:
        return []
    cels = _astar(g, ini, fim)
    pts = [(float(origem[0]), float(origem[1]))]
    pts += [_centro(c) for c in (cels if ini != c_ori else cels[1:])]
    if cels[-1] == fim and fim == c_dst and not arena.colide_circulo(destino[0], destino[1], raio_tanque):
        if len(pts) > 1 and cels[-1] == c_dst and pts[-1] == _centro(c_dst):
            pts[-1] = (float(destino[0]), float(destino[1]))
        else:
            pts.append((float(destino[0]), float(destino[1])))
    return suavizar(arena, pts, raio_tanque, g)[1:]
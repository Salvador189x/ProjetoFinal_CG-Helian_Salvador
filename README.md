TankCG

Projeto final da disciplina de Computação Gráfica — Universidade Federal de Roraima (UFRR)

Professor: Prof. Dr. Luciano F. Silva

Autores:

Helian Vinícius Filinto da Silva

Salvador de Jesus Malavé Campos

Sobre o Projeto

TankCG é um jogo 2D de combate entre tanques com visão superior (top-down) desenvolvido em Python com Pygame. A biblioteca é utilizada apenas como infraestrutura (janela, eventos, superfícies de pixels, fontes e mixer de áudio) — toda a renderização geométrica foi construída pixel a pixel sem nenhuma chamada a pygame.draw.*.

O projeto é totalmente autocontido (sem sprites nem arquivos de áudio externos) e roda em resolução interna de 480x270 ampliada 3x (1440x810) a 60 FPS.

Algoritmos de Computação Gráfica Implementados

Todos os algoritmos estão centralizados em algoritmos_cg.py e também são utilizados diretamente na lógica do jogo (linha de visão dos inimigos, prévia de trajetória com ricochete e raios do modo Farol):

Rasterização de Linhas: Algoritmo de Bresenham generalizado para os 8 octantes, utilizando apenas aritmética inteira e deslocamento de bits.

Rasterização de Circunferências: Algoritmo de Bresenham (Ponto Médio) com simetria de 8 vias.

Preenchimento de Áreas: Algoritmo de Varredura (Scanfill) com tabela de lados e regra de paridade para polígonos gerais, além de preenchimento para retângulos e circunferências.

Recorte (Clipping): Recorte de pontos, Cohen-Sutherland (segmentos de reta) e Sutherland-Hodgman (polígonos).

Curvas: Curvas de Bézier (polinômios de Bernstein) e subdivisão recursiva de De Casteljau aplicadas à trajetória parabólica dos morteiros.

Funcionalidades

3 Fases com Biomas Procedurais: Base Militar, Deserto/Ruínas e Base Ártica, com cenários pré-renderizados em camadas, sombras projetadas e marcas permanentes no piso (crateras, rastros de esteira e escombros).

Combate Tático: Canhão principal com até 2 ricochetes (e prévia de trajetória), morteiros em arco de Bézier, muros destrutíveis (tijolos, caixotes e sacos de areia), barris explosivos com reação em cadeia, terrenos que reduzem a velocidade (lama e ouriços tchecos), trincheiras com pontes, vegetação que bloqueia a visão e power-ups (cura, morteiro e escudo).

IA com Pathfinding: 3 arquétipos de inimigos (Padrão, Rápido e Artilharia) com navegação por A* em grade, suavização de rota (string pulling) e detecção de linha de visão via Bresenham.

Modo Farol (V): Iluminação dinâmica em cone construída com 36 raios de Bresenham, preenchimento por varredura e sombras projetadas pelos obstáculos.

Interface Militar e Áudio Procedural: Menu principal, tutorial e tela de áudio construídos com as mesmas primitivas gráficas; marcha militar de fundo e 6 efeitos sonoros sintetizados em código (PCM 16 bits), com ajuste de volume por categoria.

Controles

Tecla / Entrada

Ação

W A S D

Movimentar o tanque

Mouse

Mirar o canhão / Botão esquerdo para atirar

F

Lançar morteiro no ponto da mira

V

Ativar / desativar modo Farol

TAB

Abrir / fechar tutorial (pausa o jogo)

R

Reiniciar fase atual

N

Iniciar novo jogo (Fase 1)

F11

Alternar tela cheia / janela

ESC

Voltar ao menu principal / Sair

Estrutura do Repositório

├── dist/
│   └── TankCG.exe        # Executável standalone para Windows
├── algoritmos_cg.py      # Implementação dos algoritmos de Computação Gráfica
├── arena.py              # Biomas, fases, obstáculos, recorte e colisões
├── config.py             # Constantes, paletas, balanceamento e controles
├── main.py               # Laço principal, estados, HUD, menus e modo Farol
├── pathfinding.py        # Navegação A* em grade e suavização de rota
├── sons.py               # Síntese procedural de música e efeitos sonoros
├── tanques.py            # Jogador, inimigos, projéteis, morteiros e power-ups
└── TankCG.spec           # Especificação de empacotamento do PyInstaller


Como Executar

Opção 1: Executável (Windows)

Não é necessário instalar Python nem bibliotecas externas. Basta baixar o repositório e executar:

dist/TankCG.exe


Nota: Caso o Windows Defender exiba um alerta por se tratar de um executável sem assinatura digital, clique em Mais informações -> Executar assim mesmo.

Opção 2: Código-fonte (Python)

Requer Python 3 e a biblioteca pygame:

git clone https://github.com/Salvador189x/ProjetoFinal_CG-Helian_Salvador.git
cd ProjetoFinal_CG-Helian_Salvador
pip install pygame
python main.py

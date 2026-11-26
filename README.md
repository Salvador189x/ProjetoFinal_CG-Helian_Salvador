# TankCG

Projeto final da disciplina de **Computação Gráfica** (Universidade Federal de Roraima — UFRR), desenvolvido por:
* **Helian Vinícius Filinto da Silva**
* **Salvador de Jesus Malavé Campos**

## Sobre o Projeto

**TankCG** é um jogo 2D de combate entre tanques com visão superior (*top-down*) desenvolvido em Python com Pygame. A biblioteca é usada apenas como infraestrutura (janela, eventos, superfícies e áudio) — toda a renderização geométrica foi construída pixel a pixel **sem nenhuma chamada a `pygame.draw.*`**.

### Algoritmos de Computação Gráfica Implementados
* **Rasterização:** Bresenham para linhas (8 octantes) e circunferências (ponto médio).
* **Preenchimento de Áreas:** Varredura (*Scanfill*) para polígonos gerais, retângulos e circunferências.
* **Recorte (*Clipping*):** Recorte de pontos, Cohen-Sutherland (linhas) e Sutherland-Hodgman (polígonos).
* **Curvas:** Polinômios de Bernstein e subdivisão recursiva de De Casteljau (trajetória dos morteiros).

### Principais Funcionalidades
* **3 fases com biomas procedurais:** Base Militar, Deserto/Ruínas e Base Ártica.
* **IA com Pathfinding:** Inimigos com busca de caminhos **A\*** em grade, suavização de rota e linha de visão via Bresenham.
* **Modo Farol (`V`):** Iluminação dinâmica em cone com sombras projetadas pelos obstáculos.
* **Totalmente autocontido:** Sem sprites ou arquivos externos — trilha sonora e efeitos são sintetizados em código.

## Controles
* **WASD:** Movimentar o tanque
* **Mouse:** Mirar e atirar (botão esquerdo)
* **F:** Lançar morteiro
* **V:** Ativar/desativar modo Farol
* **TAB:** Abrir/fechar tutorial
* **R / N:** Reiniciar fase / Novo jogo
* **F11:** Alternar tela cheia
* **ESC:** Menu / Sair

## Como Executar

```bash
pip install pygame
python main.py

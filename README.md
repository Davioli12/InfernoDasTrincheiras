# 🔥 Inferno das Trincheiras

**Inferno das Trincheiras** é um jogo de **estratégia online** ambientado na **Primeira Guerra Mundial**.

No jogo, dois exércitos entram em conflito e precisam utilizar **soldados, recursos e cartas históricas** para superar o adversário. As cartas e acontecimentos do jogo são inspirados em eventos e situações reais do conflito.

> 🎖️ **Estratégia, recursos e decisões podem determinar o resultado da batalha.**

---

## 🎮 Sobre o jogo

Durante uma partida, cada jogador controla um exército e precisa administrar seus recursos enquanto toma decisões estratégicas.

O jogo combina:

* 🪖 **Soldados** — utilizados para defender e atacar.
* 📦 **Recursos** — necessários para manter e desenvolver o exército.
* 🃏 **Cartas históricas** — inspiradas em acontecimentos da Primeira Guerra Mundial.
* ⚔️ **Confrontos entre exércitos** — cada decisão pode alterar o andamento da partida.
* 🌐 **Multiplayer online** — jogadores podem enfrentar uns aos outros pela internet.

---

## 📜 Contexto histórico

O jogo utiliza a **Primeira Guerra Mundial** como inspiração para sua ambientação e suas mecânicas.

Algumas cartas e acontecimentos são baseados em situações que ocorreram durante o conflito, buscando aproximar elementos históricos da experiência de jogo.

O projeto possui caráter **educacional e recreativo**, utilizando elementos históricos como parte de suas mecânicas.

---

## 🕹️ Como jogar

Para jogar, baixe a versão mais recente disponível na página de Releases.

### Windows

O jogo possui um executável independente, portanto **não é necessário instalar Python ou configurar o ambiente de desenvolvimento** para executar a versão distribuída.

📥 **[Baixar a versão mais recente](https://github.com/Davioli12/InfernoDasTrincheiras/releases)**

---

## 🛠️ Tecnologias

O projeto foi desenvolvido utilizando:

* 🐍 **Python**
* 🌐 **Flask**
* 🔌 **Flask-SocketIO**
* ⚡ **Eventlet**
* 🎮 **Pygame**
* 📦 **PyInstaller**

---

## 🌐 Multiplayer

A comunicação entre os jogadores é realizada através de uma arquitetura cliente-servidor utilizando **WebSockets**, permitindo que as ações realizadas durante a partida sejam transmitidas em tempo real.

---

## 📂 Estrutura do projeto

O projeto é organizado em diferentes módulos responsáveis pelas mecânicas do jogo:

```text
InfernoDasTrincheiras/
│
├── app.py
├── cards.py
├── events.py
├── game.py
├── player.py
├── room.py
│
├── static/
│   └── ...
│
├── templates/
│   └── ...
│
└── ...
```

---

## 🚧 Status do projeto

🟢 **Em desenvolvimento**

O projeto continua recebendo melhorias, correções e novos recursos.

---

## 🎯 Objetivo

O **Inferno das Trincheiras** foi desenvolvido como um projeto que combina **programação, desenvolvimento de jogos e história**, utilizando a Primeira Guerra Mundial como base para criar uma experiência estratégica multiplayer.

---

## 👨‍💻 Desenvolvedor

Desenvolvido por **DaviOl12**.

🔗 **GitHub:** [DaviOl12](https://github.com/Davioli12)

---

## 📜 Licença

Consulte os arquivos do repositório para obter informações sobre a licença e as condições de uso do projeto.

---

⭐ Se você gostou do projeto, considere deixar uma **estrela no repositório**!

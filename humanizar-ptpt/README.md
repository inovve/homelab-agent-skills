# humanizar-ptpt

Skill de agente que revê e reescreve textos em português de Portugal para soarem naturais, humanos e profissionais. Elimina padrões frequentes de escrita por IA e qualquer vocabulário ou construção típica de português do Brasil.

Funciona com qualquer agente que suporte o formato [Agent Skills](https://agentskills.io) (Claude Code, Claude Agent SDK, claude.ai e outros), e também com agentes genéricos ou self hosted, através do prompt de sistema incluído em [system-prompt.md](system-prompt.md).

## O que faz

* Escreve exclusivamente em português europeu, sem termos brasileiros (usuário, arquivo, celular, time, etc.)
* Remove clichés e fórmulas típicas de texto gerado por IA ("No mundo actual", "Em suma", "levar ao próximo nível")
* Elimina travessões longos, excesso de negrito, emojis não pedidos e listas desnecessárias
* Dá ritmo natural às frases, alternando comprimentos
* Adapta o tom ao contexto: website, email, texto institucional, redes sociais, técnico ou e-commerce
* Nunca inventa factos, preços, garantias ou estatísticas

## Estrutura do repositório

```
humanizar-ptpt/
├── SKILL.md              O skill em formato Agent Skills (frontmatter YAML + instruções)
├── system-prompt.md      Versão sem frontmatter, pronta a colar em qualquer agente
├── README.md             Este ficheiro
├── LICENSE               Licença MIT
└── docs/
    ├── instalacao.md     Instalação detalhada por plataforma, incluindo agentes self hosted
    └── exemplos.md       Exemplos de antes e depois
```

Este skill faz parte do repositório [homelab-agent-skills](https://github.com/inovve/homelab-agent-skills).

## Instalação rápida

### Claude Code (pessoal, disponível em todos os projectos)

```bash
git clone https://github.com/inovve/homelab-agent-skills.git
cp -r homelab-agent-skills/humanizar-ptpt ~/.claude/skills/humanizar-ptpt
```

Em Windows (PowerShell):

```powershell
git clone https://github.com/inovve/homelab-agent-skills.git
Copy-Item -Recurse homelab-agent-skills\humanizar-ptpt "$env:USERPROFILE\.claude\skills\humanizar-ptpt"
```

### Claude Code (apenas num projecto)

```bash
git clone https://github.com/inovve/homelab-agent-skills.git
cp -r homelab-agent-skills/humanizar-ptpt .claude/skills/humanizar-ptpt
```

Depois de instalar, o skill é activado automaticamente sempre que pedires para escrever ou rever texto em português. Também podes invocá-lo directamente com `/humanizar-ptpt`.

### Qualquer outro agente

Consulta [docs/instalacao.md](docs/instalacao.md). Em resumo: se o agente suporta o formato Agent Skills, copia a pasta para o directório de skills; se não suporta, acrescenta o conteúdo de [system-prompt.md](system-prompt.md) ao prompt de sistema.

## Utilização

Não precisa de comandos especiais. Basta pedir:

* "Reescreve este texto para o site"
* "Revê este email antes de eu o enviar"
* "Resume este documento em dois parágrafos"
* "Traduz este texto para português"

O agente aplica as regras do skill e devolve o texto final pronto a utilizar. Se pedires análise, apresenta primeiro os problemas encontrados e só depois a versão revista.

## Licença

MIT. Consulta o ficheiro [LICENSE](LICENSE).

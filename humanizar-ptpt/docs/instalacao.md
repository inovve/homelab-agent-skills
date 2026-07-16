# Instalação

O skill segue o formato [Agent Skills](https://agentskills.io): uma pasta com um ficheiro `SKILL.md` que contém frontmatter YAML (`name` e `description`) seguido das instruções. Qualquer agente compatível com este formato consegue usá-lo sem alterações. Para agentes sem suporte nativo, existe o ficheiro `system-prompt.md`, com o mesmo conteúdo sem frontmatter, pronto a integrar num prompt de sistema.

## Claude Code

O skill vive no repositório [homelab-agent-skills](https://github.com/inovve/homelab-agent-skills), na pasta `humanizar-ptpt`.

### Instalação pessoal (todos os projectos)

Linux e macOS:

```bash
git clone https://github.com/inovve/homelab-agent-skills.git
cp -r homelab-agent-skills/humanizar-ptpt ~/.claude/skills/humanizar-ptpt
```

Windows (PowerShell):

```powershell
git clone https://github.com/inovve/homelab-agent-skills.git
Copy-Item -Recurse homelab-agent-skills\humanizar-ptpt "$env:USERPROFILE\.claude\skills\humanizar-ptpt"
```

### Instalação num projecto específico

Na raiz do projecto:

```bash
git clone https://github.com/inovve/homelab-agent-skills.git
cp -r homelab-agent-skills/humanizar-ptpt .claude/skills/humanizar-ptpt
```

Ou, se preferires não clonar nada, descarrega apenas o `SKILL.md`:

```bash
mkdir -p .claude/skills/humanizar-ptpt
curl -o .claude/skills/humanizar-ptpt/SKILL.md https://raw.githubusercontent.com/inovve/homelab-agent-skills/main/humanizar-ptpt/SKILL.md
```

### Verificação

Abre o Claude Code e escreve:

```
/humanizar-ptpt
```

Se o skill aparecer, está instalado. A partir daí é activado automaticamente sempre que pedires texto em português, sem precisares de o invocar.

## Claude Agent SDK (agentes self hosted com a API da Anthropic)

O Agent SDK carrega skills a partir de directórios de skills. Coloca a pasta `humanizar-ptpt` (com o `SKILL.md`) no directório de skills do teu agente e aponta a configuração para lá.

Exemplo em Python:

```python
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    setting_sources=["project"],   # carrega skills de .claude/skills do projecto
    allowed_tools=["Skill"],
    cwd="/caminho/para/o/projecto",
)

async for message in query(prompt="Reescreve este texto para o site: ...", options=options):
    print(message)
```

Exemplo em TypeScript:

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Revê este email: ...",
  options: {
    settingSources: ["project"],
    allowedTools: ["Skill"],
    cwd: "/caminho/para/o/projecto",
  },
})) {
  console.log(message);
}
```

A estrutura esperada no projecto é:

```
projecto/
└── .claude/
    └── skills/
        └── humanizar-ptpt/
            └── SKILL.md
```

## claude.ai e Claude Desktop

Em Definições, na secção de capacidades (Capabilities), activa Skills e carrega a pasta do skill como ficheiro zip. Para criar o zip:

```bash
zip -r humanizar-ptpt.zip humanizar-ptpt/SKILL.md
```

O zip deve conter a pasta `humanizar-ptpt` com o `SKILL.md` lá dentro.

## API da Anthropic (Messages API com skills)

A API suporta skills geridos através do parâmetro de contentor. Em alternativa, mais simples e compatível com qualquer modelo: inclui o conteúdo de `system-prompt.md` no parâmetro `system` do pedido.

```python
import anthropic

client = anthropic.Anthropic()

with open("system-prompt.md", encoding="utf-8") as f:
    regras = f.read()

resposta = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=2048,
    system=regras,
    messages=[{"role": "user", "content": "Reescreve este texto: ..."}],
)
print(resposta.content[0].text)
```

## Outros agentes self hosted (Ollama, LM Studio, vLLM, OpenWebUI, etc.)

Qualquer agente ou runtime que aceite um prompt de sistema serve. Três abordagens, da mais simples à mais integrada:

1. Prompt de sistema: copia o conteúdo de `system-prompt.md` para o campo de prompt de sistema do agente ou da personagem/modelfile. É o método universal e funciona com qualquer modelo.

2. Directório de skills: se o agente suporta o formato Agent Skills (cada vez mais frameworks suportam), copia a pasta completa para o directório de skills configurado e reinicia o agente.

3. RAG ou ficheiro de contexto: em plataformas como o OpenWebUI, podes anexar o `system-prompt.md` como conhecimento fixo do modelo.

Exemplo de Modelfile para Ollama:

```
FROM llama3.3
SYSTEM """
<conteúdo de system-prompt.md>
"""
```

## Actualização

Faz `git pull` no clone de `homelab-agent-skills` e volta a copiar a pasta `humanizar-ptpt` para o directório de skills. Se descarregaste os ficheiros manualmente, volta a descarregar o `SKILL.md` ou o `system-prompt.md` do repositório.

## Resolução de problemas

O skill não é activado automaticamente:

* Confirma que a pasta se chama exactamente `humanizar-ptpt` e contém o `SKILL.md` na raiz.
* Confirma que o frontmatter YAML está intacto (as três linhas de `---` e os campos `name` e `description`).
* No Claude Code, reinicia a sessão depois de instalar.

O agente continua a usar termos brasileiros:

* Verifica se existe outro prompt de sistema ou skill em conflito.
* Em modelos mais pequenos (self hosted), reforça o pedido: "aplica as regras de português de Portugal".

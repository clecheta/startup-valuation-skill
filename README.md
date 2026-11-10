# Startup valuation

Agent skill that prices an early-stage startup in three ways — replacement cost of the code, income, and market — in one currency per run. Missing premises stay blank and are listed. The skill answers in the language you used.

This page is the human guide. `SKILL.md` is what the agent follows. The cost series also runs from the command line with Python 3 and the standard library. English first, português do Brasil abaixo.

## English

### Install

| Scope | Path |
|-------|------|
| Every project on this machine | `~/.cursor/skills/startup-valuation/` |
| One repository | `<project>/.cursor/skills/startup-valuation/` |

`SKILL.md` must sit at the skill root. Open a new chat afterward. To only recompute labor cost, the clone path does not matter: run `scripts/calculate.py` from anywhere.

### The three approaches

Ask for “a valuation” and the agent runs **cost** (it can be computed from Git), then walks **market** and **income** and leaves every line blank that lacks a premise. `business/VALUATION.md` is written only when you ask for a valuation write-up.

| Approach | You supply | You get | Written file |
|----------|------------|---------|--------------|
| **Cost** | A Git history. Optional rate, currency, timezone, repos. | Labor as replacement cost: calendar days with at least one eligible commit, times 6 hours, times the hourly rate. | `business/CASH_FLOW.md`, labor region only, when you ask to persist it. |
| **Income** | Revenue (ARR, or MRR with an explicit ×12) and a multiple, or a full DCF (cash flows, discount rate, horizon, terminal premise). | An equity indication. Say whether you are treating it as pre-money or post-money. | `business/VALUATION.md` only if you asked for the document. |
| **Market** | TAM, SAM, and SOM in one currency and one horizon, then the inputs of one pricing method. | A round price, after the funnel is consistent. | Same rule as income. |

Cost is the cost of rebuilding the software. It is never the pre-money of a round.

### Market, in order

1. **TAM** — annual spend on the whole problem, no reach filter.
2. **SAM** — the share this model, geography, and segment can serve.
3. **SOM** — the share the company can capture in the stated horizon.

The series must satisfy `SOM ≤ SAM ≤ TAM`, same unit (accounts × annual spend). A population, ticket, or capture rate without a source stays blank. Bottom-up (reachable accounts × spend, then widen the filters) is the early-stage path. The skill ships no sector TAM.

Only then does it close a price, by one of:

| Method | Needs from you |
|--------|----------------|
| Comparable rounds | Rounds with stage, geography, year, pre- or post-money, and currency. Median is a draft. |
| VC method | Exit-year revenue or exit value, exit multiple, required return, ownership at exit, dilution path. Exit-year revenue must fit inside that year’s SOM. |
| Scorecard | A baseline pre-money, plus weights and scores (team, opportunity, product, competition, channels, need for capital). Opportunity size stays blank without SOM. |
| Berkus | A cap you state for each factor you award (idea, prototype, team, relationships, rollout). |
| Dilution math | Check size and the maximum dilution you accept, or a target post-money. |

Comps pasted with no funnel can be medianized as a draft labeled **comps without funnel**. That draft is not the round headline.

Price and readiness are separate. The agent asks about team, product evidence, how revenue is defined, growth rate and period, who would lead the round, the founder ownership target, and the instrument (priced equity, or a convertible/SAFE). Unanswered items stay blank. A SAFE has a cap only when you state the cap.

Round identities, same currency:

```text
post-money = pre-money + primary check
sold %     = primary check / post-money
```

If the sold % you state disagrees with `check / post-money`, the gap is shown. It is reconciled only when you name an option-pool increase, a secondary sale, or a convertible. Founder ownership after several rounds is the product of `(1 − dilution)` per round. One round does not answer that question.

If there is no next round, the agent describes a profitable hold with dividends, a buyback, a sale, or a wind-down. A buyback is priced only from a valuation and contract terms you provide.

### Income

```text
equity value ≈ revenue × multiple
PV           = Σ CF_t / (1+r)^t  +  PV(terminal)
```

Revenue and the multiple must share a definition (net revenue or GMV). Without revenue, or without a multiple and without a complete DCF, the income price stays blank.

### Cost formula and CLI

A day counts when it has at least one eligible commit in the project timezone. Extra commits that day add nothing. Merges are ignored. Bot authors (Dependabot, Renovate, `[bot]`, `github-actions`, `gitlab-bot`, `semantic-release`) are ignored. AI assistance is already in the observed days; there is no hour multiplier.

```text
hours(month) = active days × 6
value(month) = hours × hourly rate
```

Defaults: **USD 50 / hour** (senior monthly pay 7000 / 140 hours), **6 h** per active day, timezone **UTC**, locale `en`. The rate must already be in the chosen currency. There is no FX conversion.

```bash
python3 scripts/calculate.py calculate --cutoff YYYY-MM-DD --format json
python3 scripts/calculate.py calculate --cutoff YYYY-MM-DD --since YYYY-MM --format json
python3 scripts/calculate.py render --cutoff YYYY-MM-DD --cash-flow business/CASH_FLOW.md
```

`--since` chooses which months appear. Day counting still uses the full history through the cutoff. `render` replaces only the block between `<!-- valuation:labor:start -->` and `<!-- valuation:labor:end -->`. If `CASH_FLOW.md` is missing, it is seeded from `templates/cash-flow.md`. Flags override `business/valuation.json` in the repo that invoked the skill; anything still missing uses the defaults. Without `repos`, the script uses the Git repository of the working directory. A parent folder does not pick up sibling repos.

```json
{
  "currency": "USD",
  "hourly_rate": 50,
  "hours_per_active_day": 6,
  "timezone": "UTC",
  "locale": "en",
  "base": ".",
  "repos": ["."],
  "authors": [],
  "exclude_hashes": [],
  "series_start": null
}
```

`authors`, when non-empty, is an allow-list of names or emails. `exclude_hashes` drops template or bootstrap commits. `series_start` overrides “begin at the first eligible commit”. Changing the formula, the default rate, or the hours per day is a skill version change: older series are then not comparable.

### What stays out of v1

Liquidation-preference waterfalls, a full model of an option pool created before the check, a unit-economics pack (CAC, LTV, NRR, burn multiple, Rule of 40), and a live database of comparable rounds. Teaching tables of round sizes are used only when you paste them with year, country, and currency.

### Map of this repo

| Path | Role |
|------|------|
| `SKILL.md` | Procedure the agent follows |
| `references/cost.md` | Eligible commits, formula, CLI |
| `references/market-sizing.md` | TAM / SAM / SOM |
| `references/market.md` | Round methods and stage readiness |
| `references/income.md` | Multiple and DCF |
| `references/round-math.md` | Pre-money, post-money, dilution |
| `templates/cash-flow.md` | Seed for a new cash-flow file |
| `scripts/calculate.py` | Cost CLI |
| `scripts/market_sizing.py`, `scripts/round_math.py` | Checked formulas (stdlib) |
| `scripts/test_*.py` | `python3 scripts/test_calculate.py` (and the other two) |

License: MIT-style, company and project agnostic.

---

## Português

### Instalar

| Alcance | Caminho |
|---------|---------|
| Todos os projetos desta máquina | `~/.cursor/skills/startup-valuation/` |
| Um repositório | `<projeto>/.cursor/skills/startup-valuation/` |

`SKILL.md` precisa estar na raiz da skill. Abra um chat novo em seguida. Para só recalcular o custo de mão de obra, o caminho do clone não importa: rode `scripts/calculate.py` de qualquer lugar.

### As três abordagens

Peça “um valuation” e o agente roda **custo** (dá para calcular a partir do Git), depois percorre **mercado** e **renda** e deixa em branco toda linha sem premissa. `business/VALUATION.md` só é escrito quando você pede o documento de valuation.

| Abordagem | Você entrega | Você recebe | Arquivo |
|-----------|--------------|-------------|---------|
| **Custo** | Um histórico Git. Opcional: taxa, moeda, fuso, repositórios. | Mão de obra como custo de reposição: dias de calendário com pelo menos um commit elegível, vezes 6 horas, vezes a taxa horária. | `business/CASH_FLOW.md`, só a região de mão de obra, quando você pede para gravar. |
| **Renda** | Receita (ARR, ou MRR com um ×12 explícito) e um múltiplo, ou um DCF completo (fluxos, taxa de desconto, horizonte, premissa terminal). | Uma indicação de valor do equity. Diga se está tratando como pre-money ou post-money. | `business/VALUATION.md` só se você pediu o documento. |
| **Mercado** | TAM, SAM e SOM numa moeda e num horizonte, depois os insumos de um método de preço. | O preço da rodada, depois que o funil fecha. | A mesma regra da renda. |

Custo é o custo de reconstruir o software. Nunca é o pre-money de uma rodada.

### Mercado, nesta ordem

1. **TAM** — gasto anual com o problema inteiro, sem filtro de alcance.
2. **SAM** — a parte que este modelo, geografia e segmento conseguem atender.
3. **SOM** — a parte que a empresa consegue capturar no horizonte declarado.

A série precisa cumprir `SOM ≤ SAM ≤ TAM`, na mesma unidade (contas × gasto anual). População, ticket ou taxa de captura sem fonte ficam em branco. O caminho de estágio inicial é de baixo para cima (contas alcançáveis × gasto, depois alargar os filtros). A skill não traz TAM de setor.

Só então fecha um preço, por um destes métodos:

| Método | O que você precisa informar |
|--------|------------------------------|
| Rodadas comparáveis | Rodadas com estágio, geografia, ano, pre- ou post-money e moeda. A mediana é rascunho. |
| Método VC | Receita ou valor de saída no ano de exit, múltiplo de saída, retorno exigido, participação na saída, caminho de diluição. A receita do ano de exit precisa caber no SOM daquele ano. |
| Scorecard | Um pre-money de base, mais pesos e notas (time, oportunidade, produto, competição, canais, necessidade de capital). Tamanho da oportunidade fica em branco sem SOM. |
| Berkus | Um teto que você declara para cada fator que concede (ideia, protótipo, time, relacionamentos, rollout). |
| Conta de diluição | Tamanho do cheque e a diluição máxima que você aceita, ou um post-money alvo. |

Comparáveis colados sem funil podem virar mediana rotulada **comps without funnel** (comparáveis sem funil). Esse rascunho não é a manchete da rodada.

Preço e prontidão são coisas separadas. O agente pergunta sobre time, evidência de produto, como a receita é definida, taxa e período de crescimento, quem lideraria a rodada, a meta de participação do fundador e o instrumento (equity precificado, ou conversível/SAFE). O que não for respondido fica em branco. SAFE só tem cap quando você informa o cap.

Identidades da rodada, na mesma moeda:

```text
post-money = pre-money + cheque primário
% vendido  = cheque primário / post-money
```

Se o % vendido que você declara discorda de `cheque / post-money`, a diferença aparece. Só é reconciliada quando você nomeia aumento de option pool, venda secundária ou conversível. A participação do fundador depois de várias rodadas é o produto de `(1 − diluição)` em cada rodada. Uma rodada só não responde essa pergunta.

Se não houver próxima rodada, o agente descreve seguir lucrativo e distribuir, recompra, venda ou encerramento. Recompra só ganha preço a partir de um valuation e de termos de contrato que você fornecer.

### Renda

```text
valor do equity ≈ receita × múltiplo
VP               = Σ FC_t / (1+r)^t  +  VP(terminal)
```

Receita e múltiplo precisam da mesma definição (receita líquida ou GMV). Sem receita, ou sem múltiplo e sem um DCF completo, o preço por renda fica em branco.

### Fórmula de custo e linha de comando

Um dia conta quando tem pelo menos um commit elegível no fuso do projeto. Commits a mais nesse dia não somam nada. Merges são ignorados. Autores bot (Dependabot, Renovate, `[bot]`, `github-actions`, `gitlab-bot`, `semantic-release`) são ignorados. Assistência de IA já está nos dias observados; não há multiplicador de horas.

```text
horas(mês) = dias ativos × 6
valor(mês) = horas × taxa horária
```

Padrões: **USD 50 / hora** (salário sênior mensal 7000 / 140 horas), **6 h** por dia ativo, fuso **UTC**, locale `en`. A taxa já precisa estar na moeda escolhida. Não há conversão de câmbio.

```bash
python3 scripts/calculate.py calculate --cutoff YYYY-MM-DD --format json
python3 scripts/calculate.py calculate --cutoff YYYY-MM-DD --since YYYY-MM --format json
python3 scripts/calculate.py render --cutoff YYYY-MM-DD --cash-flow business/CASH_FLOW.md
```

`--since` escolhe quais meses aparecem. A contagem de dias continua usando o histórico inteiro até o cutoff. `render` substitui só o bloco entre `<!-- valuation:labor:start -->` e `<!-- valuation:labor:end -->`. Se `CASH_FLOW.md` não existir, nasce de `templates/cash-flow.md`. Flags vencem `business/valuation.json` no repositório que invocou a skill; o que ainda faltar usa os padrões. Sem `repos`, o script usa o repositório Git do diretório de trabalho. Uma pasta pai não puxa repositórios irmãos.

```json
{
  "currency": "USD",
  "hourly_rate": 50,
  "hours_per_active_day": 6,
  "timezone": "UTC",
  "locale": "en",
  "base": ".",
  "repos": ["."],
  "authors": [],
  "exclude_hashes": [],
  "series_start": null
}
```

`authors`, quando não vazio, é uma lista de nomes ou e-mails que contam. `exclude_hashes` tira commits de template ou bootstrap. `series_start` troca o “começar no primeiro commit elegível”. Mudar a fórmula, a taxa padrão ou as horas por dia é mudança de versão da skill: séries antigas deixam de ser comparáveis.

### O que fica fora da v1

Waterfall de preferência de liquidação, modelo completo de option pool criado antes do cheque, pacote de unit economics (CAC, LTV, NRR, burn multiple, Rule of 40) e uma base viva de rodadas comparáveis. Tabelas didáticas de tamanho de rodada só entram quando você as cola com ano, país e moeda.

### Mapa deste repositório

| Caminho | Papel |
|---------|--------|
| `SKILL.md` | Procedimento que o agente segue |
| `references/cost.md` | Commits elegíveis, fórmula, CLI |
| `references/market-sizing.md` | TAM / SAM / SOM |
| `references/market.md` | Métodos de rodada e prontidão de estágio |
| `references/income.md` | Múltiplo e DCF |
| `references/round-math.md` | Pre-money, post-money, diluição |
| `templates/cash-flow.md` | Semente de um fluxo de caixa novo |
| `scripts/calculate.py` | CLI de custo |
| `scripts/market_sizing.py`, `scripts/round_math.py` | Fórmulas verificadas (stdlib) |
| `scripts/test_*.py` | `python3 scripts/test_calculate.py` (e os outros dois) |

Licença: estilo MIT, sem amarrar empresa ou projeto.

<template>
  <q-card flat class="carbon-ai-bar">
    <!-- Header Horizontal do Copilot -->
    <q-card-section class="q-pb-xs">
      <div class="row items-center justify-between no-wrap">
        <div class="row items-center no-wrap">
          <div class="carbon-ai-icon-wrap q-mr-sm">
            <q-icon name="auto_awesome" class="text-primary-token" size="20px" />
          </div>
          <div>
            <div class="row items-center">
              <span class="carbon-ai-title">IA Analyst Co-pilot</span>
              <span class="carbon-status-pill q-ml-sm">
                <span class="carbon-status-dot"></span>
                Online & Analítico
              </span>
            </div>
            <div class="carbon-ai-sub">
              Assistente de Inteligência Executiva & Modelagem Preditiva Olist
            </div>
          </div>
        </div>

        <div class="row items-center q-gutter-x-sm">
          <span class="carbon-tag carbon-tag--neutral">GPT-OSS 120B</span>
          <q-btn
            v-if="insight"
            flat
            dense
            square
            no-caps
            size="sm"
            icon="clear"
            label="Limpar Consulta"
            class="carbon-clear-btn"
            @click="clearAnswer"
          />
        </div>
      </div>
    </q-card-section>

    <!-- Linha de Ação: Input Amplo estilo Watsonx Command Bar -->
    <q-card-section class="q-pt-xs q-pb-sm">
      <div class="row items-center q-col-gutter-sm">
        <div class="col">
          <q-input
            v-model="question"
            outlined
            dense
            square
            maxlength="500"
            placeholder="Faça uma pergunta sobre faturamento, logística, gargalos, causas de cancelamento ou simulações..."
            :disable="loading"
            @keyup.enter="askFree"
            class="carbon-command-input"
          >
            <template #prepend>
              <q-icon name="psychology" size="20px" class="text-primary-token" />
            </template>
          </q-input>
        </div>

        <div class="col-auto">
          <q-btn
            unelevated
            square
            no-caps
            color="primary"
            icon="send"
            label="Analisar"
            class="carbon-submit-btn"
            :loading="loading"
            :disable="loading || !question.trim()"
            @click="askFree"
          />
        </div>
      </div>

      <!-- Sugestões Rápidas em Linha Horizontal (Chips Carbon) -->
      <div class="row items-center q-mt-sm carbon-presets-row">
        <span class="carbon-presets-label q-mr-sm">Perguntas Frequentes:</span>
        <div class="row items-center q-gutter-xs col">
          <q-btn
            v-for="p in presets"
            :key="p.key"
            :disable="loading"
            flat
            dense
            square
            no-caps
            class="carbon-preset-chip"
            @click="ask({ preset: p.key }, p.label)"
          >
            <q-icon :name="p.icon" size="14px" class="q-mr-xs text-primary-token" />
            <span>{{ p.label }}</span>
          </q-btn>
        </div>
      </div>
    </q-card-section>

    <!-- Área de Resposta Expandida da IA (quando ativa ou carregando) -->
    <template v-if="loading || error || insight">
      <q-separator />

      <q-card-section class="carbon-ai-output-section">
        <!-- Estado de Carregamento -->
        <div v-if="loading" class="row items-center justify-center q-py-lg carbon-loading-state">
          <q-spinner-orbit color="primary" size="36px" class="q-mr-md" />
          <div>
            <div class="text-body2 text-weight-medium">Processando métricas e gerando insight executivo...</div>
            <div class="text-caption text-helper-token">Cruzando séries temporais, matriz de frete e causas de insatisfação</div>
          </div>
        </div>

        <!-- Banner de Erro -->
        <q-banner v-else-if="error" class="carbon-banner-danger q-my-sm" dense>
          <template #avatar>
            <q-icon name="error_outline" class="text-danger-token" />
          </template>
          {{ error }}
        </q-banner>

        <!-- Conteúdo do Parecer Executivo Rico -->
        <div v-else-if="insight" class="carbon-insight-container">
          <!-- Cabeçalho da Pergunta com Badge -->
          <div class="row items-center justify-between carbon-asked-header q-mb-md">
            <div class="row items-center">
              <span class="carbon-consult-icon q-mr-sm">
                <q-icon name="chat_bubble_outline" size="14px" />
              </span>
              <span class="text-weight-bold text-caption text-uppercase tracking-wider">Consulta do Gestor:</span>
              <span class="q-ml-sm text-body2 text-weight-medium text-primary-token">{{ asked }}</span>
            </div>
            <div class="row items-center q-gutter-x-xs">
              <span class="carbon-tag carbon-tag--primary">Parecer Executivo</span>
              <span class="carbon-tag carbon-tag--neutral">Olist Data Engine</span>
            </div>
          </div>

          <!-- Markdown Enriquecido -->
          <div class="carbon-rich-markdown" v-html="renderedInsight"></div>
        </div>
      </q-card-section>
    </template>
  </q-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import axios from 'axios'
import { api } from '../api'
import type { InsightPayload, InsightResponse, PresetKey } from '../types'

interface Preset {
  key: PresetKey
  label: string
  icon: string
}

const presets: Preset[] = [
  { key: 'customer_complaints', label: 'Causas de insatisfação (1-2★)', icon: 'rate_review' },
  { key: 'delivery_bottlenecks', label: 'Gargalos no prazo por estado', icon: 'local_shipping' },
  { key: 'cancellation_peak', label: 'Picos de cancelamentos', icon: 'cancel' },
  { key: 'increase_ticket', label: 'Estratégias para alavancar ticket', icon: 'price_check' }
]

const question = ref('')
const insight = ref('')
const asked = ref('')
const error = ref('')
const loading = ref(false)

function clearAnswer(): void {
  insight.value = ''
  asked.value = ''
  error.value = ''
}

function renderMarkdown(md: string): string {
  const escape = (s: string) =>
    s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

  const inline = (text: string): string => {
    let s = escape(text)

    // Formatação rica de negritos com métricas e sinais
    s = s.replace(/\*\*(.+?)\*\*/g, (_match, p1: string) => {
      // Destaque semântico sutil para números, moedas e porcentagens
      if (/R\$\s?[\d.,]+/.test(p1) || /[-+]?\d+([.,]\d+)?%/.test(p1) || /\d+([.,]\d+)?\s?(dias?|pedidos?|estrelas?)/i.test(p1)) {
        return `<strong class="metric-pill">${p1}</strong>`
      }
      return `<strong class="text-highlight">${p1}</strong>`
    })

    s = s.replace(/\*(.+?)\*/g, '<em class="text-emphasis">$1</em>')
    s = s.replace(/`(.+?)`/g, '<code class="carbon-code">$1</code>')
    return s
  }

  const lines = md.split('\n')
  const out: string[] = []
  let i = 0

  while (i < lines.length) {
    const line = lines[i]
    if (line === undefined) {
      i++
      continue
    }

    // Título Principal ##
    if (line.startsWith('## ')) {
      const titleText = line.slice(3)
      out.push(`
        <div class="carbon-h2-wrap">
          <span class="carbon-h2-icon"><svg width="18" height="18" viewBox="0 0 32 32" fill="currentColor"><path d="M16 2a14 14 0 1 0 14 14A14 14 0 0 0 16 2zm0 26a12 12 0 1 1 12-12 12 12 0 0 1-12 12z"/><path d="M11 15h10v2H11z"/></svg></span>
          <h2>${inline(titleText)}</h2>
        </div>
      `)
      i++
      continue
    }

    // Subtítulos ### com ícones contextuais e badges de seção
    if (line.startsWith('### ')) {
      const subText = line.slice(4)
      let sectionClass = 'carbon-h3-general'
      let badgeLabel = ''
      let badgeClass = 'carbon-tag--neutral'

      if (/recomenda[çc][õo]es|a[çc][õo]es|💡/i.test(subText)) {
        sectionClass = 'carbon-h3-recommendations'
        badgeLabel = 'Plano de Ação'
        badgeClass = 'carbon-tag--success'
      } else if (/diagn[óo]stico|causas|an[áa]lise/i.test(subText)) {
        sectionClass = 'carbon-h3-diagnostic'
        badgeLabel = 'Diagnóstico'
        badgeClass = 'carbon-tag--primary'
      } else if (/aten[çc][ãa]o|gargalo|risco|cr[íi]tico/i.test(subText)) {
        sectionClass = 'carbon-h3-warning'
        badgeLabel = 'Ponto Crítico'
        badgeClass = 'carbon-tag--warning'
      }

      out.push(`
        <div class="carbon-h3-wrap ${sectionClass}">
          <h3>${inline(subText)}</h3>
          ${badgeLabel ? `<span class="carbon-tag ${badgeClass} q-ml-sm">${badgeLabel}</span>` : ''}
        </div>
      `)
      i++
      continue
    }

    // Tabelas Formatadas Ricamente
    const nextLine = lines[i + 1]
    if (line.includes('|') && nextLine !== undefined && /^\s*\|?\s*[-:]+/.test(nextLine)) {
      const tableLines: string[] = []
      while (i < lines.length && (lines[i]?.includes('|') ?? false)) {
        const cur = lines[i]
        if (cur !== undefined) {
          tableLines.push(cur)
        }
        i++
      }
      if (tableLines.length >= 2 && tableLines[0] !== undefined) {
        const parseRow = (r: string) =>
          r.split('|').map(c => c.trim()).filter(c => c.length > 0)
        const headers = parseRow(tableLines[0])
        out.push('<div class="carbon-table-wrapper"><table class="carbon-rich-table">')
        out.push('<thead><tr>' + headers.map(h => `<th>${inline(h)}</th>`).join('') + '</tr></thead>')
        out.push('<tbody>')
        for (let j = 2; j < tableLines.length; j++) {
          const rowLine = tableLines[j]
          if (rowLine !== undefined) {
            const cells = parseRow(rowLine)
            out.push('<tr>' + cells.map(c => {
              // Realce de status em células
              let cellClass = ''
              if (/cr[íi]tico|grave|alto|atraso/i.test(c)) cellClass = 'cell--danger'
              else if (/positivo|ótimo|bom|redução/i.test(c)) cellClass = 'cell--success'
              else if (/médio|alerta|atenção/i.test(c)) cellClass = 'cell--warning'
              return `<td class="${cellClass}">${inline(c)}</td>`
            }).join('') + '</tr>')
          }
        }
        out.push('</tbody></table></div>')
      }
      continue
    }

    // Callout Box (Blockquote > )
    if (line.startsWith('> ')) {
      const quoteLines: string[] = []
      while (i < lines.length && (lines[i]?.startsWith('> ') ?? false)) {
        const cur = lines[i]
        if (cur !== undefined) {
          quoteLines.push(cur.slice(2))
        }
        i++
      }
      out.push(`
        <div class="carbon-callout-card">
          <div class="carbon-callout-badge">
            <span class="callout-dot"></span>
            <strong>Destaque Executivo</strong>
          </div>
          <div class="carbon-callout-text">${quoteLines.map(inline).join('<br>')}</div>
        </div>
      `)
      continue
    }

    // Listas com Marcadores Estilizados (- ou *)
    if (/^[-*]\s/.test(line)) {
      out.push('<ul class="carbon-rich-ul">')
      while (i < lines.length && /^[-*]\s/.test(lines[i] ?? '')) {
        const cur = lines[i]
        if (cur !== undefined) {
          out.push(`<li><span class="carbon-bullet-point"></span><div class="carbon-li-content">${inline(cur.replace(/^[-*]\s+/, ''))}</div></li>`)
        }
        i++
      }
      out.push('</ul>')
      continue
    }

    // Listas Ordenadas / Processos Numerados (1. 2. 3.)
    if (/^\d+\.\s/.test(line)) {
      out.push('<ol class="carbon-step-list">')
      let stepNum = 1
      while (i < lines.length && (/^\d+\.\s/.test(lines[i] ?? ''))) {
        const cur = lines[i]
        if (cur !== undefined) {
          out.push(`
            <li class="carbon-step-item">
              <span class="carbon-step-badge">${stepNum}</span>
              <div class="carbon-step-content">${inline(cur.replace(/^\d+\.\s+/, ''))}</div>
            </li>
          `)
          stepNum++
        }
        i++
      }
      out.push('</ol>')
      continue
    }

    if (line.trim() === '') {
      i++
      continue
    }

    out.push(`<p class="carbon-para">${inline(line)}</p>`)
    i++
  }

  return out.join('\n')
}

const renderedInsight = computed(() => renderMarkdown(insight.value))

async function ask(payload: InsightPayload, label: string): Promise<void> {
  loading.value = true
  error.value = ''
  insight.value = ''
  asked.value = label
  try {
    const { data } = await api.post<InsightResponse>('/ai-insight', payload)
    insight.value = data.insight
  } catch (e: unknown) {
    if (axios.isAxiosError<{ error?: string }>(e)) {
      error.value = e.response?.data?.error ?? 'Não foi possível conectar ao servidor.'
    } else {
      error.value = 'Erro inesperado ao consultar a IA.'
    }
  } finally {
    loading.value = false
  }
}

function askFree(): void {
  const q = question.value.trim()
  if (!q) return
  void ask({ question: q }, q)
  question.value = ''
}

defineExpose({
  askDirect: (q: string) => {
    void ask({ question: q }, 'Parecer Executivo sobre Cenário Simulado')
  }
})
</script>

<style scoped>
.carbon-ai-bar {
  border-radius: var(--radius-none);
  border: 1px solid var(--color-border-subtle);
  border-left: 3px solid var(--color-primary);
  background-color: var(--color-layer-01);
  box-shadow: none;
  transition: border-color 0.15s ease, background-color 0.2s ease;
}

.carbon-ai-bar:hover {
  border-color: var(--color-border-strong);
}

.carbon-ai-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
}

.carbon-ai-title {
  font-size: 0.9375rem;
  font-weight: 600;
  letter-spacing: 0.16px;
  color: var(--color-text-primary);
}

.carbon-ai-sub {
  font-size: 0.75rem;
  color: var(--color-text-helper);
}

.carbon-status-pill {
  display: inline-flex;
  align-items: center;
  font-size: 0.6875rem;
  font-weight: 500;
  color: var(--color-success);
  background-color: var(--color-success-bg);
  padding: 1px 6px;
  border-radius: var(--radius-none);
  letter-spacing: 0.32px;
}

.carbon-status-dot {
  width: 5px;
  height: 5px;
  background-color: var(--color-success);
  border-radius: 50%;
  margin-right: 4px;
}

.carbon-command-input :deep(.q-field__control) {
  background-color: var(--color-layer-02);
  border-radius: var(--radius-none);
  height: 40px;
}

.carbon-submit-btn {
  height: 40px;
  padding: 0 var(--spacing-05);
  font-size: 0.8125rem;
  font-weight: 500;
  border-radius: var(--radius-none);
}

.carbon-clear-btn {
  color: var(--color-text-secondary);
}

.carbon-presets-row {
  font-size: 0.75rem;
}

.carbon-presets-label {
  font-weight: 500;
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.carbon-preset-chip {
  border: 1px solid var(--color-border-subtle);
  background-color: var(--color-layer-02);
  color: var(--color-text-primary);
  border-radius: var(--radius-none);
  font-size: 0.6875rem;
  padding: 3px 8px;
  transition: background-color 0.15s ease, border-color 0.15s ease;
}

.carbon-preset-chip:hover {
  background-color: var(--color-layer-hover);
  border-color: var(--color-border-strong);
}

.carbon-ai-output-section {
  background-color: var(--color-layer-01);
  max-height: 600px;
  overflow-y: auto;
  padding: var(--spacing-05);
}

.carbon-asked-header {
  font-size: 0.8125rem;
  color: var(--color-text-primary);
  padding: 8px 14px;
  background-color: var(--color-layer-02);
  border-left: 2px solid var(--color-primary);
  border-radius: var(--radius-none);
}

.carbon-consult-icon {
  display: inline-flex;
  align-items: center;
  color: var(--color-primary);
}

.text-primary-token {
  color: var(--color-primary);
}

.text-secondary-token {
  color: var(--color-text-secondary);
}

.text-helper-token {
  color: var(--color-text-helper);
}

.text-danger-token {
  color: var(--color-danger);
}

.carbon-tag {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  font-size: 0.6875rem;
  font-weight: 500;
  letter-spacing: 0.32px;
  border-radius: var(--radius-none);
}

.carbon-tag--neutral {
  background-color: var(--color-layer-02);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border-subtle);
}

.carbon-tag--primary {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

.carbon-tag--success {
  background-color: var(--color-success-bg);
  color: var(--color-success);
}

.carbon-tag--warning {
  background-color: var(--color-warning-bg);
  color: var(--color-warning-text);
}

.carbon-loading-state {
  color: var(--color-text-secondary);
}

.carbon-banner-danger {
  background-color: var(--color-danger-bg);
  color: var(--color-danger);
  border-left: 3px solid var(--color-danger);
  border-radius: var(--radius-none);
}

/* ── IBM Carbon Rich Markdown Styling ── */
.carbon-rich-markdown {
  font-family: var(--font-sans);
  color: var(--color-text-primary);
  line-height: 1.6;
}

/* Título H2 com Ícone e Barra de Destaque */
.carbon-rich-markdown :deep(.carbon-h2-wrap) {
  display: flex;
  align-items: center;
  margin: 16px 0 12px 0;
  padding-bottom: 6px;
  border-bottom: 1.5px solid var(--color-border-subtle);
}

.carbon-rich-markdown :deep(.carbon-h2-icon) {
  color: var(--color-primary);
  display: flex;
  align-items: center;
  margin-right: 8px;
}

.carbon-rich-markdown :deep(h2) {
  font-size: 1.0625rem;
  font-weight: 600;
  color: var(--color-primary);
  margin: 0;
  letter-spacing: -0.01em;
}

/* Subtítulos H3 com Badges de Seção */
.carbon-rich-markdown :deep(.carbon-h3-wrap) {
  display: flex;
  align-items: center;
  margin: 18px 0 8px 0;
}

.carbon-rich-markdown :deep(h3) {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

/* Parágrafos */
.carbon-rich-markdown :deep(.carbon-para) {
  margin: 8px 0;
  font-size: 0.875rem;
  line-height: 1.65;
  color: var(--color-text-primary);
}

/* Destaque nos Negritos e Métricas (Cores Inteligentes) */
.carbon-rich-markdown :deep(.metric-pill) {
  font-weight: 600;
  color: var(--color-primary);
  background-color: var(--color-primary-light);
  padding: 1px 6px;
  border-radius: var(--radius-none);
  font-size: 0.8125rem;
  display: inline-block;
  margin: 0 2px;
}

.carbon-rich-markdown :deep(.text-highlight) {
  font-weight: 600;
  color: var(--color-text-primary);
}

.carbon-rich-markdown :deep(.text-emphasis) {
  font-style: italic;
  color: var(--color-text-secondary);
}

.carbon-rich-markdown :deep(.carbon-code) {
  font-family: var(--font-mono);
  background-color: var(--color-layer-02);
  border: 1px solid var(--color-border-subtle);
  padding: 2px 5px;
  font-size: 0.8125rem;
  border-radius: var(--radius-none);
}

/* Callout Box Executivo (Blockquote) */
.carbon-rich-markdown :deep(.carbon-callout-card) {
  background-color: var(--color-layer-02);
  border: 1px solid var(--color-border-subtle);
  border-left: 3px solid var(--color-primary);
  padding: 12px 16px;
  margin: 14px 0;
  border-radius: var(--radius-none);
}

.carbon-rich-markdown :deep(.carbon-callout-badge) {
  display: flex;
  align-items: center;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.32px;
  color: var(--color-primary);
  margin-bottom: 6px;
}

.carbon-rich-markdown :deep(.callout-dot) {
  width: 6px;
  height: 6px;
  background-color: var(--color-primary);
  border-radius: 50%;
  margin-right: 6px;
}

.carbon-rich-markdown :deep(.carbon-callout-text) {
  font-size: 0.875rem;
  line-height: 1.55;
  color: var(--color-text-primary);
}

/* Listas com Marcadores Estilizados (Bullet Points Carbon) */
.carbon-rich-markdown :deep(.carbon-rich-ul) {
  list-style: none;
  padding: 0;
  margin: 10px 0;
}

.carbon-rich-markdown :deep(.carbon-rich-ul li) {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8px;
  font-size: 0.875rem;
  line-height: 1.55;
}

.carbon-rich-markdown :deep(.carbon-bullet-point) {
  width: 6px;
  height: 6px;
  background-color: var(--color-primary);
  margin-top: 8px;
  margin-right: 10px;
  flex-shrink: 0;
}

.carbon-rich-markdown :deep(.carbon-li-content) {
  flex: 1;
}

/* Lista de Ações / Steps Numerados (Plano de Ação) */
.carbon-rich-markdown :deep(.carbon-step-list) {
  list-style: none;
  padding: 0;
  margin: 12px 0;
}

.carbon-rich-markdown :deep(.carbon-step-item) {
  display: flex;
  align-items: flex-start;
  background-color: var(--color-layer-02);
  border: 1px solid var(--color-border-subtle);
  padding: 10px 14px;
  margin-bottom: 8px;
  border-radius: var(--radius-none);
  transition: border-color 0.15s ease;
}

.carbon-rich-markdown :deep(.carbon-step-item:hover) {
  border-color: var(--color-border-strong);
}

.carbon-rich-markdown :deep(.carbon-step-badge) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background-color: var(--color-primary);
  color: var(--color-text-on-color);
  font-size: 0.75rem;
  font-weight: 600;
  margin-right: 12px;
  margin-top: 2px;
  flex-shrink: 0;
}

.carbon-rich-markdown :deep(.carbon-step-content) {
  flex: 1;
  font-size: 0.875rem;
  line-height: 1.5;
}

/* Tabelas de Dados Corporativas Carbon */
.carbon-rich-markdown :deep(.carbon-table-wrapper) {
  overflow-x: auto;
  margin: 14px 0;
  border: 1px solid var(--color-border-subtle);
}

.carbon-rich-markdown :deep(.carbon-rich-table) {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.carbon-rich-markdown :deep(.carbon-rich-table th) {
  background-color: var(--color-layer-02);
  color: var(--color-text-secondary);
  font-weight: 600;
  padding: 8px 12px;
  text-align: left;
  border-bottom: 1.5px solid var(--color-border-subtle);
  text-transform: uppercase;
  font-size: 0.6875rem;
  letter-spacing: 0.32px;
}

.carbon-rich-markdown :deep(.carbon-rich-table td) {
  padding: 8px 12px;
  border-bottom: 1px solid var(--color-border-subtle);
  color: var(--color-text-primary);
}

.carbon-rich-markdown :deep(.carbon-rich-table tr:hover td) {
  background-color: var(--color-layer-hover);
}

.carbon-rich-markdown :deep(.cell--danger) {
  color: var(--color-danger);
  font-weight: 600;
}

.carbon-rich-markdown :deep(.cell--success) {
  color: var(--color-success);
  font-weight: 600;
}

.carbon-rich-markdown :deep(.cell--warning) {
  color: var(--color-warning-text);
  font-weight: 600;
}
</style>

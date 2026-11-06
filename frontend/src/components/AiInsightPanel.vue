<template>
  <q-card flat class="ai-panel" :class="{ 'ai-panel--dark': $q.dark.isActive }">
    <q-card-section class="q-pb-sm">
      <div class="row items-center justify-between no-wrap q-mb-sm">
        <div class="row items-center no-wrap">
          <div class="ai-icon-bubble q-mr-sm">
            <q-icon name="auto_awesome" color="white" size="18px" />
          </div>
          <div>
            <div class="text-subtitle1 text-weight-bold">IA Analyst Co-pilot</div>
            <div class="text-caption" style="opacity: 0.65">Insights estratégicos via LLM</div>
          </div>
        </div>
        <q-badge color="purple-7" rounded label="GPT-OSS 120B" />
      </div>

      <!-- Presets / Quick prompts -->
      <div class="text-caption text-weight-medium q-mb-xs" style="opacity: 0.7">Perguntas Rápidas:</div>
      <div class="column q-gutter-xs q-mb-md">
        <q-btn
          v-for="p in presets"
          :key="p.key"
          :disable="loading"
          flat
          dense
          no-caps
          align="left"
          class="preset-btn"
          :class="{ 'preset-btn--dark': $q.dark.isActive }"
          @click="ask({ preset: p.key }, p.label)"
        >
          <q-icon :name="p.icon" size="16px" class="q-mr-sm text-primary" />
          <span class="text-caption ellipsis">{{ p.label }}</span>
        </q-btn>
      </div>

      <!-- Freeform question input -->
      <q-input
        v-model="question"
        outlined
        dense
        maxlength="500"
        placeholder="Faça uma pergunta sobre o negócio..."
        :disable="loading"
        :dark="$q.dark.isActive"
        @keyup.enter="askFree"
        class="custom-input"
      >
        <template #append>
          <q-btn
            flat
            round
            dense
            icon="send"
            color="primary"
            :disable="loading || !question.trim()"
            @click="askFree"
          />
        </template>
      </q-input>
    </q-card-section>

    <q-separator :dark="$q.dark.isActive" />

    <q-card-section class="answer-area">
      <div v-if="loading" class="column items-center justify-center q-pa-xl text-grey-6" style="min-height: 200px">
        <q-spinner-orbit color="primary" size="48px" />
        <div class="text-body2 q-mt-md text-weight-medium">Processando métricas e gerando insight...</div>
        <div class="text-caption text-grey-5 q-mt-xs">Analisando padrões e correlações</div>
      </div>

      <q-banner v-else-if="error" class="bg-negative text-white q-my-sm" rounded dense>
        <template #avatar>
          <q-icon name="error_outline" color="white" />
        </template>
        {{ error }}
      </q-banner>

      <div v-else-if="insight">
        <div class="asked-label q-mb-md" :class="{ 'asked-label--dark': $q.dark.isActive }">
          <q-icon name="chat_bubble_outline" size="16px" class="q-mr-xs text-primary" />
          <span>{{ asked }}</span>
        </div>
        <div class="insight-markdown" :class="{ 'insight-markdown--dark': $q.dark.isActive }" v-html="renderedInsight"></div>
      </div>

      <div v-else class="column items-center justify-center text-center q-pa-lg empty-state" style="min-height: 220px">
        <div class="empty-icon-bubble q-mb-sm">
          <q-icon name="lightbulb" size="36px" color="amber-7" />
        </div>
        <div class="text-subtitle2 text-weight-medium">Pronto para analisar</div>
        <div class="text-caption text-grey-6 q-mt-xs" style="max-width: 260px">
          Clique em uma das perguntas rápidas acima ou digite uma dúvida específica sobre faturamento, logística ou produtos.
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useQuasar } from 'quasar'
import axios from 'axios'
import { api } from '../api'
import type { InsightPayload, InsightResponse, PresetKey } from '../types'

const $q = useQuasar()

interface Preset {
  key: PresetKey
  label: string
  icon: string
}

const presets: Preset[] = [
  { key: 'customer_complaints', label: 'Causas de insatisfação nos reviews (1-2★)', icon: 'rate_review' },
  { key: 'delivery_bottlenecks', label: 'Gargalos no prazo de entrega por estado', icon: 'local_shipping' },
  { key: 'cancellation_peak', label: 'Causas do pico de cancelamentos', icon: 'cancel' },
  { key: 'increase_ticket', label: 'Estratégias para alavancar o ticket médio', icon: 'price_check' }
]

const question = ref('')
const insight = ref('')
const asked = ref('')
const error = ref('')
const loading = ref(false)

function renderMarkdown(md: string): string {
  const escape = (s: string) =>
    s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

  const inline = (text: string): string => {
    let s = escape(text)
    s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    s = s.replace(/\*(.+?)\*/g, '<em>$1</em>')
    s = s.replace(/`(.+?)`/g, '<code>$1</code>')
    return s
  }

  const lines = md.split('\n')
  const out: string[] = []
  let i = 0

  while (i < lines.length) {
    const line = lines[i]

    if (line.startsWith('## ')) {
      out.push(`<h2>${inline(line.slice(3))}</h2>`)
      i++
      continue
    }
    if (line.startsWith('### ')) {
      out.push(`<h3>${inline(line.slice(4))}</h3>`)
      i++
      continue
    }

    if (line.includes('|') && i + 1 < lines.length && /^\s*\|?\s*[-:]+/.test(lines[i + 1])) {
      const tableLines: string[] = []
      while (i < lines.length && lines[i].includes('|')) {
        tableLines.push(lines[i])
        i++
      }
      if (tableLines.length >= 2) {
        const parseRow = (r: string) =>
          r.split('|').map(c => c.trim()).filter(c => c.length > 0)
        const headers = parseRow(tableLines[0])
        out.push('<div class="table-wrapper"><table>')
        out.push('<thead><tr>' + headers.map(h => `<th>${inline(h)}</th>`).join('') + '</tr></thead>')
        out.push('<tbody>')
        for (let j = 2; j < tableLines.length; j++) {
          const cells = parseRow(tableLines[j])
          out.push('<tr>' + cells.map(c => `<td>${inline(c)}</td>`).join('') + '</tr>')
        }
        out.push('</tbody></table></div>')
      }
      continue
    }

    if (line.startsWith('> ')) {
      const quoteLines: string[] = []
      while (i < lines.length && lines[i].startsWith('> ')) {
        quoteLines.push(lines[i].slice(2))
        i++
      }
      out.push(`<blockquote>${quoteLines.map(inline).join('<br>')}</blockquote>`)
      continue
    }

    if (/^[\-\*]\s/.test(line)) {
      out.push('<ul>')
      while (i < lines.length && /^[\-\*]\s/.test(lines[i])) {
        out.push(`<li>${inline(lines[i].replace(/^[\-\*]\s+/, ''))}</li>`)
        i++
      }
      out.push('</ul>')
      continue
    }

    if (/^\d+\.\s/.test(line)) {
      out.push('<ol>')
      while (i < lines.length && /^\d+\.\s/.test(lines[i])) {
        out.push(`<li>${inline(lines[i].replace(/^\d+\.\s+/, ''))}</li>`)
        i++
      }
      out.push('</ol>')
      continue
    }

    if (line.trim() === '') {
      i++
      continue
    }

    out.push(`<p>${inline(line)}</p>`)
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
.ai-panel {
  border-radius: 14px;
  border: 1px solid #E2E8F0;
  background: #FFFFFF;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.04);
  transition: background 0.3s ease, border-color 0.3s ease;
}

.ai-panel--dark {
  background: #1E1E2F;
  border-color: #2D2D44;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.35);
}

.ai-icon-bubble {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #7C4DFF, #651FFF);
  display: flex;
  align-items: center;
  justify-content: center;
}

.preset-btn {
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  padding: 8px 12px;
  text-align: left;
  background: #F8FAFC;
  transition: all 0.2s ease;
}

.preset-btn:hover {
  background: #EEF2F6;
  border-color: #CBD5E1;
  transform: translateX(2px);
}

.preset-btn--dark {
  border-color: #2D2D44;
  background: #252538;
}

.preset-btn--dark:hover {
  background: #2E2E46;
  border-color: #3E3E5B;
}

.asked-label {
  display: flex;
  align-items: center;
  font-size: 0.82rem;
  color: #475569;
  padding: 8px 12px;
  background: #F1F5F9;
  border-radius: 8px;
  border-left: 3px solid #1976D2;
}

.asked-label--dark {
  background: #252538;
  color: #94A3B8;
  border-left-color: #7C4DFF;
}

.answer-area {
  min-height: 220px;
  max-height: 65vh;
  overflow-y: auto;
}

.empty-icon-bubble {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #FFF8E1;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ── Markdown Styles ── */
.insight-markdown :deep(h2) {
  font-size: 1.12rem;
  font-weight: 700;
  color: #1976D2;
  margin: 0 0 10px 0;
  padding-bottom: 6px;
  border-bottom: 2px solid #E2E8F0;
}

.insight-markdown--dark :deep(h2) {
  color: #82B1FF;
  border-bottom-color: #2D2D44;
}

.insight-markdown :deep(h3) {
  font-size: 0.98rem;
  font-weight: 700;
  color: #334155;
  margin: 14px 0 6px 0;
}

.insight-markdown--dark :deep(h3) {
  color: #E2E8F0;
}

.insight-markdown :deep(p) {
  margin: 6px 0;
  line-height: 1.6;
  font-size: 0.88rem;
  color: #334155;
}

.insight-markdown--dark :deep(p) {
  color: #CBD5E1;
}

.insight-markdown :deep(strong) {
  color: #2E7D32;
  font-weight: 700;
}

.insight-markdown--dark :deep(strong) {
  color: #81C784;
}

.insight-markdown :deep(blockquote) {
  margin: 10px 0;
  padding: 10px 14px;
  background: #FFF8E1;
  border-left: 4px solid #FF9800;
  border-radius: 0 8px 8px 0;
  font-size: 0.86rem;
  color: #B45309;
}

.insight-markdown--dark :deep(blockquote) {
  background: #2D271E;
  color: #FBBF24;
}

.insight-markdown :deep(.table-wrapper) {
  overflow-x: auto;
  margin: 10px 0;
  border-radius: 8px;
  border: 1px solid #E2E8F0;
}

.insight-markdown--dark :deep(.table-wrapper) {
  border-color: #2D2D44;
}

.insight-markdown :deep(table) {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
}

.insight-markdown :deep(th) {
  background: #1976D2;
  color: white;
  font-weight: 600;
  padding: 8px 10px;
  text-align: left;
}

.insight-markdown--dark :deep(th) {
  background: #311B92;
}

.insight-markdown :deep(td) {
  padding: 6px 10px;
  border-bottom: 1px solid #F1F5F9;
  color: #334155;
}

.insight-markdown--dark :deep(td) {
  border-bottom-color: #2D2D44;
  color: #CBD5E1;
}

.insight-markdown :deep(tr:nth-child(even)) {
  background: #F8FAFC;
}

.insight-markdown--dark :deep(tr:nth-child(even)) {
  background: #222235;
}

.insight-markdown :deep(ul),
.insight-markdown :deep(ol) {
  margin: 6px 0;
  padding-left: 20px;
}

.insight-markdown :deep(li) {
  margin-bottom: 4px;
  line-height: 1.5;
  font-size: 0.88rem;
  color: #334155;
}

.insight-markdown--dark :deep(li) {
  color: #CBD5E1;
}
</style>

<template>
  <q-card flat bordered class="ai-panel">
    <q-card-section>
      <div class="row items-center q-mb-sm">
        <q-icon name="auto_awesome" color="primary" size="sm" class="q-mr-sm" />
        <div class="text-h6">IA Analyst</div>
      </div>

      <div class="column q-gutter-sm q-mb-md">
        <q-btn
          v-for="p in presets"
          :key="p.key"
          :label="p.label"
          :disable="loading"
          outline
          color="primary"
          no-caps
          align="left"
          @click="ask({ preset: p.key }, p.label)"
        />
      </div>

      <q-input
        v-model="question"
        outlined
        dense
        maxlength="500"
        placeholder="Pergunte algo sobre os dados..."
        :disable="loading"
        @keyup.enter="askFree"
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

    <q-separator />

    <q-card-section class="answer-area">
      <div v-if="loading" class="row items-center text-grey-7">
        <q-spinner-dots color="primary" size="32px" class="q-mr-sm" /> Analisando os dados...
      </div>
      <q-banner v-else-if="error" class="bg-negative text-white" rounded>{{ error }}</q-banner>
      <div v-else-if="insight">
        <div class="text-caption text-grey-6 q-mb-xs">{{ asked }}</div>
        <div class="insight-text">{{ insight }}</div>
      </div>
      <div v-else class="text-grey-6">Escolha uma pergunta rápida ou digite a sua.</div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import { api } from '../api'
import type { InsightPayload, InsightResponse, PresetKey } from '../types'

interface Preset {
  key: PresetKey
  label: string
}

const presets: Preset[] = [
  { key: 'delivery_bottlenecks', label: 'Identificar gargalos no tempo de entrega' },
  { key: 'cancellation_peak', label: 'Analisar o que causou o pico de cancelamentos' },
  { key: 'increase_ticket', label: 'Gerar recomendação para aumentar o ticket médio' }
]

const question = ref('')
const insight = ref('')
const asked = ref('')
const error = ref('')
const loading = ref(false)

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
      error.value = 'Erro inesperado.'
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
</script>

<style scoped>
.insight-text {
  white-space: pre-wrap;
  line-height: 1.6;
}
.answer-area {
  min-height: 200px;
  max-height: 55vh;
  overflow-y: auto;
}
</style>
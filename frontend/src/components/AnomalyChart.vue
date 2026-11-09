<template>
  <q-card flat class="carbon-chart-card">
    <q-card-section class="q-pb-none">
      <div class="row items-center justify-between no-wrap q-mb-xs">
        <div class="row items-center no-wrap">
          <q-icon name="warning_amber" class="text-warning-token q-mr-sm" size="18px" />
          <div class="carbon-chart-title">{{ title }}</div>
          <span class="carbon-tag carbon-tag--danger q-ml-sm">
            {{ data.anomalies.length }} anomalias
          </span>
        </div>
        <q-btn flat round dense icon="help_outline" size="sm" class="carbon-help-btn">
          <q-tooltip class="carbon-tooltip" max-width="320px" anchor="top middle" self="bottom middle">
            <div class="text-weight-bold q-mb-xs">Como funciona a Detecção?</div>
            <div class="carbon-tooltip-desc">
              Compara cada dia com a janela dos 28 dias anteriores via <strong>z-score</strong>. Se o desvio for maior que 3σ, o dia é destacado como pico incomum ou queda drástica.
            </div>
          </q-tooltip>
        </q-btn>
      </div>

      <!-- Legendas Visuais Carbon -->
      <div class="row items-center q-gutter-x-md q-gutter-y-xs q-mt-xs carbon-legend-bar">
        <div class="row items-center">
          <span class="legend-indicator legend-indicator--primary"></span>
          <span>Pedidos reais</span>
        </div>
        <div class="row items-center">
          <span class="legend-indicator legend-indicator--danger"></span>
          <span>Pico atípico</span>
        </div>
        <div class="row items-center">
          <span class="legend-indicator legend-indicator--warning"></span>
          <span>Queda brusca</span>
        </div>
        <div class="row items-center">
          <span class="legend-line"></span>
          <span>Faixa de controle (±3σ)</span>
        </div>
      </div>
    </q-card-section>

    <q-card-section class="q-pt-sm">
      <apexchart
        v-if="data.dates.length > 0"
        type="line"
        :height="320"
        :options="options"
        :series="series"
      />
      <div v-else class="column items-center justify-center q-pa-xl carbon-loading-state" style="min-height: 240px">
        <q-spinner-puff color="primary" size="40px" />
        <div class="q-mt-md text-caption">Calculando desvios e anomalias...</div>
      </div>
    </q-card-section>

    <!-- Expansível com Tabela Resumo das Anomalias -->
    <q-separator />
    <q-expansion-item
      dense
      icon="table_chart"
      label="Ver lista detalhada dos eventos atípicos"
      header-class="carbon-expansion-header"
      expand-separator
    >
      <div class="q-pa-sm anomaly-table-container">
        <table class="carbon-data-table">
          <thead>
            <tr>
              <th>Data</th>
              <th>Tipo</th>
              <th>Volume Real</th>
              <th>Volume Esperado</th>
              <th>Z-Score</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in sortedAnomalies" :key="a.date">
              <td class="text-weight-bold">{{ formatDate(a.date) }}</td>
              <td>
                <span
                  class="carbon-tag"
                  :class="a.type === 'pico' ? 'carbon-tag--danger' : 'carbon-tag--warning'"
                >
                  <q-icon :name="a.type === 'pico' ? 'arrow_upward' : 'arrow_downward'" size="12px" class="q-mr-xs" />
                  {{ a.type === 'pico' ? 'Pico Incomum' : 'Queda Brusca' }}
                </span>
              </td>
              <td class="text-weight-bold">{{ a.value.toLocaleString('pt-BR') }}</td>
              <td>~{{ a.expected.toLocaleString('pt-BR') }}</td>
              <td>
                <span :class="a.z > 0 ? 'text-danger-token text-weight-bold' : 'text-warning-token text-weight-bold'">
                  {{ a.z > 0 ? '+' : '' }}{{ a.z }}σ
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </q-expansion-item>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useQuasar } from 'quasar'
import type { ApexOptions } from 'apexcharts'
import type { AnomalyChartData } from '../types'
import { getCarbonTokens } from '../tokens'

const $q = useQuasar()

const props = defineProps<{
  title: string
  data: AnomalyChartData
}>()

const formatDate = (d: string) => {
  const parts = d.split('-')
  if (parts.length === 3) {
    return `${parts[2]}/${parts[1]}/${parts[0]}`
  }
  return d
}

const sortedAnomalies = computed(() => {
  return [...props.data.anomalies].sort((a, b) => Math.abs(b.z) - Math.abs(a.z)).slice(0, 10)
})

const toPoints = (values: (number | null)[]) =>
  props.data.dates.map((d, i) => ({
    x: new Date(`${d}T00:00:00`).getTime(),
    y: values[i] ?? null
  }))

const series = computed(() => [
  { name: 'Pedidos Realizados', data: toPoints(props.data.series) },
  { name: 'Limite Superior (+3σ)', data: toPoints(props.data.upper) },
  { name: 'Limite Inferior (-3σ)', data: toPoints(props.data.lower) }
])

const options = computed<ApexOptions>(() => {
  const isDark = $q.dark.isActive
  const tokens = getCarbonTokens(isDark)

  return {
    chart: {
      toolbar: { show: false },
      zoom: { enabled: true, type: 'x' },
      fontFamily: 'var(--font-sans)',
      background: 'transparent',
      foreColor: tokens.chartText
    },
    theme: { mode: isDark ? 'dark' : 'light' },
    colors: [tokens.primary, tokens.borderStrong, tokens.borderStrong],
    stroke: { width: [2.5, 1.2, 1.2], dashArray: [0, 4, 4], curve: 'smooth' },
    dataLabels: { enabled: false },
    legend: { show: false },
    grid: { borderColor: tokens.chartGrid, strokeDashArray: 2 },
    xaxis: {
      type: 'datetime',
      labels: { style: { colors: tokens.chartText, fontSize: '11px', fontFamily: 'var(--font-sans)' } },
      axisBorder: { color: tokens.chartGrid }
    },
    yaxis: {
      labels: {
        formatter: (v: number) => Math.round(v).toLocaleString('pt-BR'),
        style: { colors: tokens.chartText, fontSize: '11px', fontFamily: 'var(--font-sans)' }
      }
    },
    tooltip: {
      theme: isDark ? 'dark' : 'light',
      x: { format: 'dd/MM/yyyy' }
    },
    annotations: {
      points: props.data.anomalies.map((a) => ({
        x: new Date(`${a.date}T00:00:00`).getTime(),
        y: a.value,
        marker: {
          size: 5,
          fillColor: a.type === 'pico' ? tokens.danger : tokens.warning,
          strokeColor: tokens.layer01,
          strokeWidth: 2
        },
        label: {
          text: a.type === 'pico' ? '▲' : '▼',
          style: {
            color: a.type === 'pico' ? tokens.danger : tokens.warningText,
            background: 'transparent',
            fontSize: '11px',
            fontWeight: 'bold'
          },
          offsetY: -6
        }
      }))
    }
  }
})
</script>

<style scoped>
.carbon-chart-card {
  border-radius: var(--radius-none);
  border: 1px solid var(--color-border-subtle);
  background: var(--color-layer-01);
  box-shadow: none;
  transition: border-color 0.15s ease, background-color 0.2s ease;
}

.carbon-chart-card:hover {
  border-color: var(--color-border-strong);
}

.carbon-chart-title {
  font-size: 0.875rem;
  font-weight: 600;
  letter-spacing: 0.16px;
  color: var(--color-text-primary);
}

.text-warning-token {
  color: var(--color-warning-text);
}

.text-danger-token {
  color: var(--color-danger);
}

.carbon-help-btn {
  color: var(--color-text-secondary);
}

.carbon-loading-state {
  color: var(--color-text-secondary);
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

.carbon-tag--warning {
  background-color: var(--color-warning-bg);
  color: var(--color-warning-text);
}

.carbon-tag--danger {
  background-color: var(--color-danger-bg);
  color: var(--color-danger);
}

.carbon-legend-bar {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.legend-indicator {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-none);
  display: inline-block;
  margin-right: 6px;
}

.legend-indicator--primary {
  background-color: var(--color-primary);
}

.legend-indicator--danger {
  background-color: var(--color-danger);
}

.legend-indicator--warning {
  background-color: var(--color-warning);
}

.legend-line {
  width: 14px;
  height: 0;
  border-top: 2px dashed var(--color-border-strong);
  display: inline-block;
  margin-right: 6px;
}

.carbon-expansion-header {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-primary);
}

.anomaly-table-container {
  overflow-x: auto;
  max-height: 220px;
}

.carbon-data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.75rem;
}

.carbon-data-table th {
  text-align: left;
  padding: 8px 12px;
  background-color: var(--color-layer-02);
  color: var(--color-text-secondary);
  font-weight: 600;
  border-bottom: 1px solid var(--color-border-subtle);
}

.carbon-data-table td {
  padding: 6px 12px;
  border-bottom: 1px solid var(--color-border-subtle);
  color: var(--color-text-primary);
}

.carbon-tooltip {
  background-color: var(--color-header-bg);
  color: var(--color-header-text);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-none);
  padding: 8px 12px;
}

.carbon-tooltip-desc {
  font-size: 0.8125rem;
  line-height: 1.4;
  color: var(--color-text-secondary);
}
</style>

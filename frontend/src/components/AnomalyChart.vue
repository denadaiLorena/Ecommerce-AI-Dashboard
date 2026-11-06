<template>
  <q-card flat class="chart-card" :class="{ 'chart-card--dark': $q.dark.isActive }">
    <q-card-section class="q-pb-none">
      <div class="row items-center justify-between no-wrap q-mb-xs">
        <div class="row items-center no-wrap">
          <q-icon name="warning" color="warning" size="20px" class="q-mr-sm" />
          <div class="chart-title">{{ title }}</div>
          <q-badge color="negative" rounded class="q-ml-sm" :label="`${data.anomalies.length} anomalias`" />
        </div>
        <q-btn flat round dense icon="help_outline" size="sm" :color="$q.dark.isActive ? 'grey-4' : 'grey-7'">
          <q-tooltip class="bg-blue-grey-10 text-white shadow-3" max-width="320px" anchor="top middle" self="bottom middle">
            <div class="text-weight-bold q-mb-xs">Como funciona a Detecção?</div>
            <div style="font-size: 0.82rem; line-height: 1.4">
              Compara cada dia com a janela dos 28 dias anteriores via <strong>z-score</strong>. Se o desvio for maior que 3σ, o dia é destacado como pico incomum ou queda drástica.
            </div>
          </q-tooltip>
        </q-btn>
      </div>

      <!-- Legendas Visuais Rápidas -->
      <div class="row items-center q-gutter-x-md q-gutter-y-xs q-mt-xs text-caption legend-bar">
        <div class="row items-center">
          <span class="legend-dot" :style="{ background: $q.dark.isActive ? '#00E5FF' : '#1976D2' }"></span>
          <span>Pedidos reais</span>
        </div>
        <div class="row items-center">
          <span class="legend-dot" style="background: #E53935"></span>
          <span>Pico atípico</span>
        </div>
        <div class="row items-center">
          <span class="legend-dot" style="background: #FFB300"></span>
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
      <div v-else class="column items-center justify-center q-pa-xl text-grey-6" style="min-height: 240px">
        <q-spinner-puff color="primary" size="44px" />
        <div class="q-mt-md text-caption">Calculando desvios e anomalias...</div>
      </div>
    </q-card-section>

    <!-- Drawer Expansível com Tabela Resumo das Anomalias -->
    <q-separator :dark="$q.dark.isActive" />
    <q-expansion-item
      dense
      icon="table_chart"
      label="Ver lista detalhada dos eventos atípicos"
      header-class="text-caption text-weight-medium text-primary"
      expand-separator
    >
      <div class="q-pa-sm anomaly-table-container">
        <table class="anomaly-table" :class="{ 'anomaly-table--dark': $q.dark.isActive }">
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
                <q-chip
                  dense
                  size="sm"
                  :color="a.type === 'pico' ? 'negative' : 'warning'"
                  text-color="white"
                  :icon="a.type === 'pico' ? 'arrow_upward' : 'arrow_downward'"
                >
                  {{ a.type === 'pico' ? 'Pico Incomum' : 'Queda Brusca' }}
                </q-chip>
              </td>
              <td class="text-weight-bold">{{ a.value.toLocaleString('pt-BR') }}</td>
              <td>~{{ a.expected.toLocaleString('pt-BR') }}</td>
              <td>
                <span :class="a.z > 0 ? 'text-negative text-weight-bold' : 'text-warning text-weight-bold'">
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
  const textColor = isDark ? '#B0BEC5' : '#546E7A'
  const gridColor = isDark ? '#2B2D42' : '#ECEFF1'
  const lineColor = isDark ? '#00E5FF' : '#1976D2'

  return {
    chart: {
      toolbar: { show: false },
      zoom: { enabled: true, type: 'x' },
      fontFamily: 'inherit',
      background: 'transparent',
      foreColor: textColor
    },
    theme: { mode: isDark ? 'dark' : 'light' },
    colors: [lineColor, '#78909C', '#78909C'],
    stroke: { width: [2.5, 1.2, 1.2], dashArray: [0, 5, 5], curve: 'smooth' },
    dataLabels: { enabled: false },
    legend: { show: false },
    grid: { borderColor: gridColor, strokeDashArray: 3 },
    xaxis: {
      type: 'datetime',
      labels: { style: { colors: textColor, fontSize: '11px' } },
      axisBorder: { color: gridColor }
    },
    yaxis: {
      labels: {
        formatter: (v: number) => Math.round(v).toLocaleString('pt-BR'),
        style: { colors: textColor, fontSize: '11px' }
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
          size: 6,
          fillColor: a.type === 'pico' ? '#E53935' : '#FFB300',
          strokeColor: isDark ? '#1E1E2F' : '#FFFFFF',
          strokeWidth: 2
        },
        label: {
          text: a.type === 'pico' ? '▲' : '▼',
          style: {
            color: a.type === 'pico' ? '#E53935' : '#FFB300',
            background: 'transparent',
            fontSize: '11px',
            fontWeight: 'bold'
          },
          offsetY: -8
        }
      }))
    }
  }
})
</script>

<style scoped>
.chart-card {
  border-radius: 14px;
  border: 1px solid #E2E8F0;
  background: #FFFFFF;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.3s ease;
}

.chart-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.08);
}

.chart-card--dark {
  background: #1E1E2F;
  border-color: #2D2D44;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.35);
}

.chart-card--dark:hover {
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.6);
}

.chart-title {
  font-size: 0.98rem;
  font-weight: 700;
  letter-spacing: 0.2px;
}

.legend-bar {
  opacity: 0.8;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 6px;
}

.legend-line {
  width: 16px;
  height: 0;
  border-top: 2px dashed #78909C;
  display: inline-block;
  margin-right: 6px;
}

.anomaly-table-container {
  overflow-x: auto;
  max-height: 220px;
}

.anomaly-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
}

.anomaly-table th {
  text-align: left;
  padding: 8px 12px;
  background: #F1F5F9;
  color: #475569;
  font-weight: 600;
}

.anomaly-table td {
  padding: 6px 12px;
  border-bottom: 1px solid #E2E8F0;
}

.anomaly-table--dark th {
  background: #252538;
  color: #94A3B8;
}

.anomaly-table--dark td {
  border-bottom: 1px solid #2D2D44;
}
</style>

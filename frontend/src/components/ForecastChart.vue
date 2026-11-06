<template>
  <q-card flat class="chart-card" :class="{ 'chart-card--dark': $q.dark.isActive }">
    <q-card-section class="q-pb-none">
      <div class="row items-center justify-between no-wrap q-mb-xs">
        <div class="row items-center no-wrap">
          <q-icon name="trending_up" color="secondary" size="22px" class="q-mr-sm" />
          <div class="chart-title">{{ title }}</div>
          <q-badge
            v-if="data.metrics && data.metrics.accuracy > 0"
            color="positive"
            rounded
            class="q-ml-sm cursor-pointer"
          >
            <q-icon name="verified" size="13px" class="q-mr-xs" />
            {{ data.metrics.accuracy }}% Acurácia
            <q-tooltip class="bg-blue-grey-10 text-white shadow-4" max-width="320px">
              <div class="text-weight-bold q-mb-xs">Métricas de Validação (Backtesting 30d):</div>
              <div>• <strong>Modelo:</strong> {{ data.metrics.model_name }}</div>
              <div>• <strong>Acurácia:</strong> {{ data.metrics.accuracy }}%</div>
              <div>• <strong>MAPE:</strong> {{ data.metrics.mape }}% (Erro Percentual Absoluto Médio)</div>
              <div>• <strong>MAE:</strong> {{ isRevenue ? 'R$ ' + data.metrics.mae.toLocaleString('pt-BR') : data.metrics.mae }} (Erro Médio Absoluto)</div>
              <div>• <strong>RMSE:</strong> {{ isRevenue ? 'R$ ' + data.metrics.rmse.toLocaleString('pt-BR') : data.metrics.rmse }}</div>
            </q-tooltip>
          </q-badge>
        </div>

        <!-- Alternador de Métrica: Pedidos vs Faturamento -->
        <div class="row items-center q-gutter-x-sm">
          <q-btn-toggle
            v-model="activeMetric"
            dense
            rounded
            unelevated
            no-caps
            toggle-color="secondary"
            :color="$q.dark.isActive ? 'grey-9' : 'grey-3'"
            :text-color="$q.dark.isActive ? 'grey-4' : 'grey-8'"
            :options="[
              { label: 'Pedidos', value: 'orders', icon: 'local_mall' },
              { label: 'Faturamento', value: 'revenue', icon: 'attach_money' }
            ]"
            @update:model-value="onMetricToggle"
          />

          <q-btn flat round dense icon="help_outline" size="sm" :color="$q.dark.isActive ? 'grey-4' : 'grey-7'">
            <q-tooltip class="bg-blue-grey-10 text-white shadow-3" max-width="320px" anchor="top middle" self="bottom middle">
              <div class="text-weight-bold q-mb-xs">Modelo Holt-Winters com Sazonalidade 7D</div>
              <div style="font-size: 0.82rem; line-height: 1.4">
                Utiliza Suavização Exponencial Tripla com amortecimento de tendência e efeito sazonal para cada dia da semana. Validado com backtest temporal nos últimos 30 dias conhecidos.
              </div>
            </q-tooltip>
          </q-btn>
        </div>
      </div>

      <!-- Métricas Resumo da Previsão -->
      <div
        class="row items-center justify-between q-mt-sm q-pa-sm forecast-meta-box"
        :class="{ 'forecast-meta-box--dark': $q.dark.isActive }"
      >
        <div class="row items-center q-gutter-x-md text-caption">
          <div class="row items-center">
            <span class="legend-dot" :style="{ background: $q.dark.isActive ? '#00E5FF' : '#1976D2' }"></span>
            <span>Histórico Real (90d)</span>
          </div>
          <div class="row items-center">
            <span class="legend-dash" style="border-top-color: #00BFA5"></span>
            <span>Previsão ({{ isRevenue ? 'Receita R$' : 'Pedidos' }})</span>
          </div>
          <div class="row items-center">
            <span class="legend-box" style="background: rgba(0, 191, 165, 0.25)"></span>
            <span>Intervalo de Confiança (95%)</span>
          </div>
        </div>

        <div class="text-caption text-weight-bold" :class="$q.dark.isActive ? 'text-teal-3' : 'text-teal-9'">
          Total projetado: {{ totalLabel }}
        </div>
      </div>
    </q-card-section>

    <q-card-section class="q-pt-sm">
      <apexchart
        v-if="data.history_dates.length > 0"
        type="rangeArea"
        :height="320"
        :options="options"
        :series="series"
      />
      <div v-else class="column items-center justify-center q-pa-xl text-grey-6" style="min-height: 240px">
        <q-spinner-puff color="secondary" size="44px" />
        <div class="q-mt-md text-caption">Ajustando modelo preditivo Holt-Winters...</div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useQuasar } from 'quasar'
import type { ApexOptions } from 'apexcharts'
import type { ForecastChartData } from '../types'

const $q = useQuasar()

const props = defineProps<{
  title: string
  data: ForecastChartData
}>()

const emit = defineEmits<{
  (e: 'metric-change', metric: 'orders' | 'revenue'): void
}>()

const activeMetric = ref<'orders' | 'revenue'>(props.data.metric || 'orders')

watch(
  () => props.data.metric,
  (newVal) => {
    if (newVal) activeMetric.value = newVal
  }
)

function onMetricToggle(val: 'orders' | 'revenue') {
  emit('metric-change', val)
}

const isRevenue = computed(() => activeMetric.value === 'revenue')

const formatValue = (v: number): string => {
  if (isRevenue.value) {
    return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 })
  }
  return `${Math.round(v).toLocaleString('pt-BR')} pedidos`
}

const totalLabel = computed(() => {
  const total = props.data.total_forecast || 0
  if (isRevenue.value) {
    return total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 })
  }
  return `${Math.round(total).toLocaleString('pt-BR')} pedidos`
})

const toMs = (d: string): number => new Date(`${d}T00:00:00`).getTime()

const series = computed(() => {
  const lastHistDate = props.data.history_dates.at(-1)
  const lastHistValue = props.data.history.at(-1)

  const range = props.data.forecast_dates.map((d, i) => ({
    x: toMs(d),
    y: [props.data.lower[i], props.data.upper[i]]
  }))
  const forecastLine = props.data.forecast_dates.map((d, i) => ({
    x: toMs(d),
    y: props.data.forecast[i]
  }))

  if (lastHistDate !== undefined && lastHistValue !== undefined) {
    const anchor = toMs(lastHistDate)
    range.unshift({ x: anchor, y: [lastHistValue, lastHistValue] })
    forecastLine.unshift({ x: anchor, y: lastHistValue })
  }

  return [
    { name: 'Intervalo de Confiança (95%)', type: 'rangeArea', data: range },
    {
      name: isRevenue.value ? 'Faturamento Histórico' : 'Histórico Real',
      type: 'line',
      data: props.data.history_dates.map((d, i) => ({
        x: toMs(d),
        y: props.data.history[i]
      }))
    },
    {
      name: isRevenue.value ? 'Projeção de Faturamento' : 'Previsão de Pedidos',
      type: 'line',
      data: forecastLine
    }
  ]
})

const options = computed<ApexOptions>(() => {
  const isDark = $q.dark.isActive
  const textColor = isDark ? '#B0BEC5' : '#546E7A'
  const gridColor = isDark ? '#2B2D42' : '#ECEFF1'
  const histColor = isDark ? '#00E5FF' : '#1976D2'
  const forecastColor = '#00BFA5'
  const rangeColor = isDark ? '#26A69A' : '#80CBC4'

  return {
    chart: {
      type: 'rangeArea',
      toolbar: { show: false },
      zoom: { enabled: false },
      fontFamily: 'inherit',
      background: 'transparent',
      foreColor: textColor,
      animations: { enabled: true, speed: 400 }
    },
    theme: { mode: isDark ? 'dark' : 'light' },
    colors: [rangeColor, histColor, forecastColor],
    stroke: { width: [0, 2.5, 2.5], dashArray: [0, 0, 5], curve: 'smooth' },
    fill: { opacity: [isDark ? 0.35 : 0.45, 1, 1] },
    dataLabels: { enabled: false },
    legend: { show: false },
    grid: { borderColor: gridColor, strokeDashArray: 3 },
    xaxis: {
      type: 'datetime',
      labels: { style: { colors: textColor, fontSize: '11px' } },
      axisBorder: { color: gridColor }
    },
    yaxis: {
      min: 0,
      labels: {
        formatter: (v: number) => {
          if (isRevenue.value) {
            return `R$ ${(v / 1000).toFixed(0)}k`
          }
          return Math.round(v).toLocaleString('pt-BR')
        },
        style: { colors: textColor, fontSize: '11px' }
      }
    },
    tooltip: {
      theme: isDark ? 'dark' : 'light',
      shared: true,
      x: { format: 'dd/MM/yyyy' },
      y: {
        formatter: (v: number) => (v == null ? '' : formatValue(v))
      }
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

.forecast-meta-box {
  background: #F8FAFC;
  border-radius: 8px;
  border: 1px solid #E2E8F0;
}

.forecast-meta-box--dark {
  background: #252538;
  border-color: #2D2D44;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 6px;
}

.legend-dash {
  width: 16px;
  height: 0;
  border-top: 2.5px dashed;
  display: inline-block;
  margin-right: 6px;
}

.legend-box {
  width: 14px;
  height: 10px;
  border-radius: 2px;
  display: inline-block;
  margin-right: 6px;
}
</style>

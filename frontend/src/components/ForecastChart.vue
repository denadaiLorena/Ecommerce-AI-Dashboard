<template>
  <q-card flat class="carbon-chart-card">
    <q-card-section class="q-pb-none">
      <div class="row items-center justify-between no-wrap q-mb-xs">
        <div class="row items-center no-wrap">
          <q-icon name="trending_up" class="text-primary-token q-mr-sm" size="20px" />
          <div class="carbon-chart-title">{{ title }}</div>
          <span
            v-if="data.metrics && data.metrics.accuracy > 0"
            class="carbon-tag carbon-tag--success q-ml-sm cursor-pointer"
          >
            <q-icon name="verified" size="13px" class="q-mr-xs" />
            {{ data.metrics.accuracy }}% Acurácia
            <q-tooltip class="carbon-tooltip" max-width="320px">
              <div class="text-weight-bold q-mb-xs">Métricas de Validação (Backtesting 30d):</div>
              <div>• <strong>Modelo:</strong> {{ data.metrics.model_name }}</div>
              <div>• <strong>Acurácia:</strong> {{ data.metrics.accuracy }}%</div>
              <div>• <strong>MAPE:</strong> {{ data.metrics.mape }}% (Erro Percentual Absoluto Médio)</div>
              <div>• <strong>MAE:</strong> {{ isRevenue ? 'R$ ' + data.metrics.mae.toLocaleString('pt-BR') : data.metrics.mae }}</div>
              <div>• <strong>RMSE:</strong> {{ isRevenue ? 'R$ ' + data.metrics.rmse.toLocaleString('pt-BR') : data.metrics.rmse }}</div>
            </q-tooltip>
          </span>
        </div>

        <!-- Alternador de Métrica: Pedidos vs Faturamento (Carbon Content Switcher) -->
        <div class="row items-center q-gutter-x-sm">
          <q-btn-toggle
            v-model="activeMetric"
            dense
            unelevated
            square
            no-caps
            class="carbon-switcher"
            toggle-color="primary"
            :options="[
              { label: 'Pedidos', value: 'orders', icon: 'local_mall' },
              { label: 'Faturamento', value: 'revenue', icon: 'attach_money' }
            ]"
            @update:model-value="onMetricToggle"
          />

          <q-btn flat round dense icon="help_outline" size="sm" class="carbon-help-btn">
            <q-tooltip class="carbon-tooltip" max-width="320px" anchor="top middle" self="bottom middle">
              <div class="text-weight-bold q-mb-xs">Modelo Holt-Winters com Sazonalidade 7D</div>
              <div class="carbon-tooltip-desc">
                Utiliza Suavização Exponencial Tripla com amortecimento de tendência e efeito sazonal para cada dia da semana. Validado com backtest temporal nos últimos 30 dias conhecidos.
              </div>
            </q-tooltip>
          </q-btn>
        </div>
      </div>

      <!-- Métricas Resumo da Previsão -->
      <div class="row items-center justify-between q-mt-sm q-pa-sm carbon-forecast-meta">
        <div class="row items-center q-gutter-x-md text-caption">
          <div class="row items-center">
            <span class="legend-indicator legend-indicator--history"></span>
            <span>Histórico Real (90d)</span>
          </div>
          <div class="row items-center">
            <span class="legend-dash"></span>
            <span>Previsão ({{ isRevenue ? 'Receita R$' : 'Pedidos' }})</span>
          </div>
          <div class="row items-center">
            <span class="legend-box"></span>
            <span>Intervalo de Confiança (95%)</span>
          </div>
        </div>

        <div class="text-caption text-weight-bold text-primary-token">
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
      <div v-else class="column items-center justify-center q-pa-xl carbon-loading-state" style="min-height: 240px">
        <q-spinner-puff color="primary" size="40px" />
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
import { getCarbonTokens } from '../tokens'

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
  const tokens = getCarbonTokens(isDark)

  return {
    chart: {
      type: 'rangeArea',
      toolbar: { show: false },
      zoom: { enabled: false },
      fontFamily: 'var(--font-sans)',
      background: 'transparent',
      foreColor: tokens.chartText,
      animations: { enabled: true, speed: 300 }
    },
    theme: { mode: isDark ? 'dark' : 'light' },
    colors: [tokens.chartConfidence, tokens.textSecondary, tokens.primary],
    stroke: { width: [0, 2, 2.5], dashArray: [0, 0, 4], curve: 'smooth' },
    fill: { opacity: [1, 1, 1] },
    dataLabels: { enabled: false },
    legend: { show: false },
    grid: { borderColor: tokens.chartGrid, strokeDashArray: 2 },
    xaxis: {
      type: 'datetime',
      labels: { style: { colors: tokens.chartText, fontSize: '11px', fontFamily: 'var(--font-sans)' } },
      axisBorder: { color: tokens.chartGrid }
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
        style: { colors: tokens.chartText, fontSize: '11px', fontFamily: 'var(--font-sans)' }
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

.text-primary-token {
  color: var(--color-primary);
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

.carbon-tag--success {
  background-color: var(--color-success-bg);
  color: var(--color-success);
}

.carbon-switcher {
  border: 1px solid var(--color-border-subtle);
  background-color: var(--color-layer-02);
  border-radius: var(--radius-none);
  font-size: 0.75rem;
}

.carbon-help-btn {
  color: var(--color-text-secondary);
}

.carbon-forecast-meta {
  background-color: var(--color-layer-02);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-none);
  color: var(--color-text-secondary);
}

.legend-indicator {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-none);
  display: inline-block;
  margin-right: 6px;
}

.legend-indicator--history {
  background-color: var(--color-text-secondary);
}

.legend-dash {
  width: 14px;
  height: 0;
  border-top: 2.5px dashed var(--color-primary);
  display: inline-block;
  margin-right: 6px;
}

.legend-box {
  width: 12px;
  height: 10px;
  background-color: var(--color-primary-light);
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-none);
  display: inline-block;
  margin-right: 6px;
}

.carbon-loading-state {
  color: var(--color-text-secondary);
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

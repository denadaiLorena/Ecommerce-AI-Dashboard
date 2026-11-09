<template>
  <q-card flat class="carbon-chart-card">
    <q-card-section class="q-pb-none">
      <div class="row items-center no-wrap justify-between">
        <div class="row items-center no-wrap">
          <div class="carbon-chart-title">{{ title }}</div>
          <span v-if="badge" class="carbon-tag q-ml-sm" :class="badgeClass">{{ badge }}</span>
        </div>
        <q-btn v-if="description" flat round dense icon="help_outline" size="sm" class="carbon-help-btn">
          <q-tooltip class="carbon-tooltip" max-width="320px" anchor="top middle" self="bottom middle">
            <div class="text-weight-bold q-mb-xs">{{ title }}</div>
            <div class="carbon-tooltip-desc">{{ description }}</div>
          </q-tooltip>
        </q-btn>
      </div>
      <div v-if="caption" class="carbon-chart-caption q-mt-xs">
        {{ caption }}
      </div>
    </q-card-section>

    <q-card-section class="q-pt-sm">
      <apexchart v-if="hasData" :type="type" :height="height" :options="options" :series="chartSeries" />
      <div v-else class="column items-center justify-center q-pa-xl carbon-loading-state" style="min-height: 220px">
        <q-spinner-puff color="primary" size="40px" />
        <div class="q-mt-md text-caption">Carregando métricas...</div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useQuasar } from 'quasar'
import type { ApexOptions } from 'apexcharts'
import { getCarbonTokens } from '../tokens'

const $q = useQuasar()

const props = withDefaults(
  defineProps<{
    title: string
    type?: 'area' | 'bar' | 'donut'
    labels?: string[]
    data?: number[]
    seriesName?: string
    height?: number | string
    horizontal?: boolean
    currency?: boolean
    percentage?: boolean
    unit?: string
    yMin?: number
    yMax?: number
    description?: string
    caption?: string
    badge?: string
    badgeColor?: string
  }>(),
  {
    type: 'bar',
    labels: () => [],
    data: () => [],
    seriesName: 'Valor',
    height: 300,
    horizontal: false,
    currency: false,
    percentage: false,
    unit: '',
    description: '',
    caption: '',
    badge: '',
    badgeColor: 'primary'
  }
)

const hasData = computed(() => props.data && props.data.length > 0)

const badgeClass = computed(() => {
  if (props.badgeColor === 'negative') return 'carbon-tag--danger'
  if (props.badgeColor === 'positive') return 'carbon-tag--success'
  if (props.badgeColor?.includes('amber')) return 'carbon-tag--warning'
  return 'carbon-tag--neutral'
})

const fmt = (v: number): string => {
  if (props.currency) {
    return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 })
  }
  if (props.percentage) {
    return `${v.toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%`
  }
  if (props.unit) {
    return `${v.toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })} ${props.unit}`
  }
  return v.toLocaleString('pt-BR')
}

const chartSeries = computed(() =>
  props.type === 'donut' ? props.data : [{ name: props.seriesName, data: props.data }]
)

const options = computed<ApexOptions>(() => {
  const isDark = $q.dark.isActive
  const tokens = getCarbonTokens(isDark)

  const colors = props.type === 'donut' ? tokens.chartSeries : [tokens.primary]

  const base: ApexOptions = {
    chart: {
      toolbar: { show: false },
      fontFamily: 'var(--font-sans)',
      background: 'transparent',
      foreColor: tokens.chartText,
      animations: {
        enabled: true,
        speed: 350,
        dynamicAnimation: { enabled: true, speed: 250 }
      }
    },
    theme: { mode: isDark ? 'dark' : 'light' },
    dataLabels: { enabled: false },
    colors,
    grid: {
      borderColor: tokens.chartGrid,
      strokeDashArray: 2,
      xaxis: { lines: { show: false } },
      yaxis: { lines: { show: true } }
    },
    legend: {
      position: 'bottom',
      labels: { colors: tokens.chartText }
    }
  }

  if (props.type === 'donut') {
    return {
      ...base,
      labels: props.labels,
      plotOptions: {
        pie: {
          donut: {
            size: '72%',
            labels: {
              show: true,
              name: { color: tokens.chartText, fontSize: '13px', fontWeight: 500 },
              value: {
                color: tokens.textPrimary,
                fontSize: '18px',
                fontWeight: 600,
                formatter: (val: string) => fmt(Number(val))
              },
              total: {
                show: true,
                label: 'Total',
                color: tokens.chartText,
                fontSize: '12px',
                fontWeight: 500,
                formatter: (w: { globals: { seriesTotals: number[] } }) =>
                  fmt(w.globals.seriesTotals.reduce((a: number, b: number) => a + b, 0))
              }
            }
          }
        }
      },
      stroke: { show: true, width: 2, colors: [tokens.layer01] }
    }
  }

  return {
    ...base,
    xaxis: {
      categories: props.labels,
      labels: {
        rotate: props.labels.length > 8 ? -35 : 0,
        hideOverlappingLabels: true,
        style: { colors: tokens.chartText, fontSize: '11px', fontFamily: 'var(--font-sans)' }
      },
      axisBorder: { color: tokens.chartGrid },
      axisTicks: { color: tokens.chartGrid }
    },
    yaxis: {
      ...(props.yMin !== undefined && { min: props.yMin }),
      ...(props.yMax !== undefined && { max: props.yMax }),
      labels: {
        formatter: (v: number) => fmt(v),
        style: { colors: tokens.chartText, fontSize: '11px', fontFamily: 'var(--font-sans)' }
      }
    },
    stroke: {
      curve: 'smooth',
      width: props.type === 'area' ? 2.5 : 0
    },
    fill:
      props.type === 'area'
        ? {
            type: 'gradient',
            gradient: {
              shadeIntensity: 1,
              opacityFrom: isDark ? 0.45 : 0.35,
              opacityTo: 0.02,
              stops: [0, 95, 100]
            }
          }
        : {},
    plotOptions: {
      bar: {
        horizontal: props.horizontal,
        borderRadius: 0,
        columnWidth: '48%'
      }
    },
    tooltip: {
      theme: isDark ? 'dark' : 'light',
      y: { formatter: (v: number) => fmt(v) }
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

.carbon-chart-caption {
  font-size: 0.75rem;
  color: var(--color-text-helper);
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

.carbon-tag--neutral {
  background-color: var(--color-layer-02);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border-subtle);
}

.carbon-tag--success {
  background-color: var(--color-success-bg);
  color: var(--color-success);
}

.carbon-tag--warning {
  background-color: var(--color-warning-bg);
  color: var(--color-warning-text);
}

.carbon-tag--danger {
  background-color: var(--color-danger-bg);
  color: var(--color-danger);
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

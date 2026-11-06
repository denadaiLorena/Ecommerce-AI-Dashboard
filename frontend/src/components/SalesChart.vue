<template>
  <q-card flat class="chart-card" :class="{ 'chart-card--dark': $q.dark.isActive }">
    <q-card-section class="q-pb-none">
      <div class="row items-center no-wrap justify-between">
        <div class="row items-center no-wrap">
          <div class="chart-title">{{ title }}</div>
          <q-badge v-if="badge" :color="badgeColor" rounded class="q-ml-sm" :label="badge" />
        </div>
        <q-btn v-if="description" flat round dense icon="help_outline" size="sm" :color="$q.dark.isActive ? 'grey-4' : 'grey-7'">
          <q-tooltip class="bg-blue-grey-10 text-white shadow-3" max-width="300px" anchor="top middle" self="bottom middle">
            <div class="text-weight-bold q-mb-xs">{{ title }}</div>
            <div style="font-size: 0.82rem; line-height: 1.4">{{ description }}</div>
          </q-tooltip>
        </q-btn>
      </div>
      <div v-if="caption" class="text-caption chart-caption q-mt-xs">
        {{ caption }}
      </div>
    </q-card-section>

    <q-card-section class="q-pt-sm">
      <apexchart v-if="hasData" :type="type" :height="height" :options="options" :series="chartSeries" />
      <div v-else class="column items-center justify-center q-pa-xl text-grey-6" style="min-height: 220px">
        <q-spinner-puff color="primary" size="44px" />
        <div class="q-mt-md text-caption">Carregando métricas...</div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useQuasar } from 'quasar'
import type { ApexOptions } from 'apexcharts'

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
    description: '',
    caption: '',
    badge: '',
    badgeColor: 'primary'
  }
)

const hasData = computed(() => props.data && props.data.length > 0)

const fmt = (v: number): string =>
  props.currency
    ? v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 })
    : v.toLocaleString('pt-BR')

const chartSeries = computed(() =>
  props.type === 'donut' ? props.data : [{ name: props.seriesName, data: props.data }]
)

const darkPalette = ['#7C4DFF', '#00E5FF', '#00E676', '#FFAB00', '#FF5252', '#FF4081']
const lightPalette = ['#1976D2', '#00897B', '#FB8C00', '#E53935', '#8E24AA', '#3949AB']

const options = computed<ApexOptions>(() => {
  const isDark = $q.dark.isActive
  const textColor = isDark ? '#B0BEC5' : '#546E7A'
  const gridColor = isDark ? '#2B2D42' : '#ECEFF1'
  const colors = isDark ? darkPalette : lightPalette

  const base: ApexOptions = {
    chart: {
      toolbar: { show: false },
      fontFamily: 'inherit',
      background: 'transparent',
      foreColor: textColor,
      animations: {
        enabled: true,
        speed: 500,
        dynamicAnimation: { enabled: true, speed: 350 }
      }
    },
    theme: { mode: isDark ? 'dark' : 'light' },
    dataLabels: { enabled: false },
    colors,
    grid: {
      borderColor: gridColor,
      strokeDashArray: 3,
      xaxis: { lines: { show: false } },
      yaxis: { lines: { show: true } }
    },
    legend: {
      position: 'bottom',
      labels: { colors: textColor }
    }
  }

  if (props.type === 'donut') {
    return {
      ...base,
      labels: props.labels,
      plotOptions: {
        pie: {
          donut: {
            size: '68%',
            labels: {
              show: true,
              name: { color: textColor, fontSize: '13px', fontWeight: 600 },
              value: {
                color: textColor,
                fontSize: '18px',
                fontWeight: 700,
                formatter: (val: string) => fmt(Number(val))
              },
              total: {
                show: true,
                label: 'Total',
                color: textColor,
                fontSize: '12px',
                fontWeight: 600,
                formatter: (w: { globals: { seriesTotals: number[] } }) =>
                  fmt(w.globals.seriesTotals.reduce((a: number, b: number) => a + b, 0))
              }
            }
          }
        }
      },
      stroke: { show: true, width: 2, colors: [isDark ? '#1E1E2F' : '#FFFFFF'] }
    }
  }

  return {
    ...base,
    xaxis: {
      categories: props.labels,
      labels: {
        rotate: props.labels.length > 8 ? -35 : 0,
        hideOverlappingLabels: true,
        style: { colors: textColor, fontSize: '11px' }
      },
      axisBorder: { color: gridColor },
      axisTicks: { color: gridColor }
    },
    yaxis: {
      ...(props.yMin !== undefined && { min: props.yMin }),
      ...(props.yMax !== undefined && { max: props.yMax }),
      labels: {
        formatter: (v: number) => fmt(v),
        style: { colors: textColor, fontSize: '11px' }
      }
    },
    stroke: {
      curve: 'smooth',
      width: props.type === 'area' ? 3 : 0
    },
    fill:
      props.type === 'area'
        ? {
            type: 'gradient',
            gradient: {
              shadeIntensity: 1,
              opacityFrom: isDark ? 0.6 : 0.45,
              opacityTo: 0.05,
              stops: [0, 90, 100]
            }
          }
        : {},
    plotOptions: {
      bar: {
        horizontal: props.horizontal,
        borderRadius: 5,
        columnWidth: '50%'
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

.chart-caption {
  opacity: 0.68;
}
</style>

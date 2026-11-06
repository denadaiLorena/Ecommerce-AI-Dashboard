<template>
    <q-card flat bordered>
        <q-card-section>
            <div class="text-subtitle1 text-weight-medium">{{ title }}</div>
            <apexchart v-if="hasData" :type="type" :height="height" :options="options" :series="chartSeries" />
            <div v-else class="text-grey-6 q-pa-lg text-center">Carregando...</div>
        </q-card-section>
    </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ApexOptions } from 'apexcharts'

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
    }>(),
    {
        type: 'bar',
        labels: () => [],
        data: () => [],
        seriesName: 'Valor',
        height: 300,
        horizontal: false,
        currency: false
    }
)

const hasData = computed(() => props.data.length > 0)

const fmt = (v: number): string =>
    props.currency
        ? v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 })
        : v.toLocaleString('pt-BR')

const chartSeries = computed(() =>
    props.type === 'donut' ? props.data : [{ name: props.seriesName, data: props.data }]
)

const options = computed<ApexOptions>(() => {
    const base: ApexOptions = {
        chart: { toolbar: { show: false }, fontFamily: 'inherit' },
        dataLabels: { enabled: false },
        colors: ['#1976D2', '#26A69A', '#F2C037', '#C10015', '#9C27B0']
    }

    if (props.type === 'donut') {
        return {
            ...base,
            labels: props.labels,
            legend: { position: 'bottom' },
            plotOptions: { pie: { donut: { size: '60%' } } }
        }
    }

      return {
    ...base,
    xaxis: { categories: props.labels, labels: { rotate: -45, hideOverlappingLabels: true } },
    yaxis: {
      ...(props.yMin !== undefined && { min: props.yMin }),
      ...(props.yMax !== undefined && { max: props.yMax }),
      labels: { formatter: (v: number) => fmt(v) }
    },
    stroke: { curve: 'smooth', width: props.type === 'area' ? 3 : 0 },
    fill:
      props.type === 'area'
        ? { type: 'gradient', gradient: { opacityFrom: 0.5, opacityTo: 0.05 } }
        : {},
    plotOptions: { bar: { horizontal: props.horizontal, borderRadius: 4 } },
    tooltip: { y: { formatter: (v: number) => fmt(v) } }
  }
})
</script>
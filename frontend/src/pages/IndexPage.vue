<template>
  <q-page class="q-pa-md bg-grey-2">
    <div class="text-h5 text-weight-bold q-mb-md">AI Metric Pulse</div>

    <q-banner v-if="error" class="bg-negative text-white q-mb-md" rounded>{{ error }}</q-banner>

    <!-- KPIs -->
    <div class="row q-col-gutter-md q-mb-md">
      <div v-for="k in kpiCards" :key="k.title" class="col-12 col-sm-6 col-md-3">
        <KpiCard v-bind="k" />
      </div>
    </div>

    <div class="row q-col-gutter-md">
      <!-- Gráficos -->
      <div class="col-12 col-lg-8">
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-6">
            <SalesChart title="Pedidos por hora do dia" type="area" series-name="Pedidos"
              :labels="hour.hours" :data="hour.series" />
          </div>
          <div class="col-12 col-md-6">
            <SalesChart title="Faturamento por mês" type="area" series-name="Faturamento" currency
              :labels="month.months" :data="month.series" />
          </div>
          <div class="col-12 col-md-6">
            <SalesChart title="Nota média por faixa de entrega" type="bar" series-name="Nota"
              :labels="dvs.faixas" :data="dvs.series" :y-min="0" :y-max="5" />
          </div>
          <div class="col-12 col-md-6">
            <SalesChart title="Formas de pagamento" type="donut"
              :labels="pay.labels" :data="pay.series" />
          </div>
          <div class="col-12 col-md-6">
            <SalesChart title="Top 10 estados por pedidos" type="bar" series-name="Pedidos" horizontal
              :labels="states.states" :data="states.series" />
          </div>
          <div class="col-12 col-md-6">
            <SalesChart title="Top 10 categorias por faturamento" type="bar" series-name="Faturamento"
              horizontal currency :labels="cats.categories" :data="cats.series" />
          </div>
        </div>
      </div>

      <!-- IA -->
      <div class="col-12 col-lg-4">
        <AiInsightPanel />
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import KpiCard from '../components/KpiCard.vue'
import SalesChart from '../components/SalesChart.vue'
import AiInsightPanel from '../components/AiInsightPanel.vue'
import type {
  Kpis,
  HourChart,
  MonthChart,
  DeliveryScoreChart,
  PaymentChart,
  StatesChart,
  CategoriesChart
} from '../types'

interface KpiCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: string
  color: string
}

const kpis = ref<Kpis | null>(null)
const hour = ref<HourChart>({ hours: [], series: [] })
const month = ref<MonthChart>({ months: [], series: [] })
const dvs = ref<DeliveryScoreChart>({ faixas: [], series: [] })
const pay = ref<PaymentChart>({ labels: [], series: [] })
const states = ref<StatesChart>({ states: [], series: [] })
const cats = ref<CategoriesChart>({ categories: [], series: [] })
const error = ref('')

const brl = (v: number): string =>
  v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })

const kpiCards = computed<KpiCardProps[]>(() => {
  const k = kpis.value
  if (!k) return []
  return [
    {
      title: 'Faturamento Total',
      value: brl(k.total_sales),
      subtitle: `${k.total_orders.toLocaleString('pt-BR')} pedidos`,
      icon: 'payments',
      color: 'positive'
    },
    {
      title: 'Tempo Médio de Entrega',
      value: `${k.avg_delivery_days} dias`,
      subtitle: `${k.late_rate}% entregues com atraso`,
      icon: 'local_shipping',
      color: 'primary'
    },
    {
      title: 'Taxa de Cancelamento',
      value: `${k.cancellation_rate}%`,
      icon: 'cancel',
      color: 'negative'
    },
    {
      title: 'Nota Média',
      value: `${k.avg_review_score} / 5`,
      icon: 'star',
      color: 'amber-8'
    }
  ]
})

onMounted(async () => {
  try {
    const [a, b, c, d, e, f, g] = await Promise.all([
      api.get<Kpis>('/kpis'),
      api.get<HourChart>('/charts/orders-by-hour'),
      api.get<MonthChart>('/charts/sales-by-month'),
      api.get<DeliveryScoreChart>('/charts/delivery-vs-score'),
      api.get<PaymentChart>('/charts/payments'),
      api.get<StatesChart>('/charts/top-states'),
      api.get<CategoriesChart>('/charts/top-categories')
    ])
    kpis.value = a.data
    hour.value = b.data
    month.value = c.data
    dvs.value = d.data
    pay.value = e.data
    states.value = f.data
    cats.value = g.data
  } catch {
    error.value = 'Não foi possível carregar os dados. O backend Flask está rodando na porta 5000?'
  }
})
</script>
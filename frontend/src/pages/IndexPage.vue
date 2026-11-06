<template>
  <q-page class="q-pa-lg main-page" :class="{ 'main-page--dark': $q.dark.isActive }">
    <!-- Header de Boas-Vindas & Barra de Ações -->
    <div class="row items-center justify-between q-mb-lg filter-bar-wrap">
      <div>
        <div class="text-h5 text-weight-bolder row items-center">
          <span>Visão Geral & Performance</span>
          <q-badge color="positive" class="q-ml-sm q-py-xs q-px-sm" rounded>
            <q-icon name="fiber_manual_record" size="10px" class="q-mr-xs" />
            Dados em Tempo Real
          </q-badge>
        </div>
        <div class="text-caption text-sub">
          Acompanhamento analítico integrado com Olist E-commerce e IA preditiva.
        </div>
      </div>

      <!-- Controles & Filtros Rápidos -->
      <div class="row items-center q-gutter-sm q-mt-xs">
        <q-btn-toggle
          v-model="periodFilter"
          no-caps
          rounded
          unelevated
          toggle-color="primary"
          :color="$q.dark.isActive ? 'grey-9' : 'grey-3'"
          :text-color="$q.dark.isActive ? 'grey-4' : 'grey-8'"
          :options="[
            { label: 'Todo o Período', value: 'all' },
            { label: 'Ano 2018', value: '2018' },
            { label: 'Ano 2017', value: '2017' }
          ]"
        />

        <q-btn
          outline
          round
          dense
          icon="refresh"
          :color="$q.dark.isActive ? 'grey-4' : 'primary'"
          :loading="refreshing"
          @click="fetchData"
        >
          <q-tooltip>Atualizar Métricas</q-tooltip>
        </q-btn>
      </div>
    </div>

    <!-- Banner de erro -->
    <q-banner v-if="error" class="bg-negative text-white q-mb-md" rounded dense>
      <template #avatar>
        <q-icon name="cloud_off" color="white" />
      </template>
      {{ error }}
    </q-banner>

    <!-- Cards de KPI -->
    <div class="row q-col-gutter-md q-mb-lg">
      <div v-for="k in kpiCards" :key="k.title" class="col-12 col-sm-6 col-md-3">
        <KpiCard v-bind="k" />
      </div>
    </div>

    <!-- Conteúdo Principal Dividido: Gráficos (8 cols) e IA Analyst (4 cols) -->
    <div class="row q-col-gutter-lg">
      <div class="col-12 col-lg-8">
        <div class="row q-col-gutter-md">
          <!-- 1. Inteligência Preditiva & Anomalias (Destaque Topo) -->
          <div class="col-12">
            <div class="section-tag row items-center q-mb-sm">
              <q-icon name="insights" size="18px" class="q-mr-xs text-secondary" />
              <span class="text-weight-bold text-caption text-uppercase">Previsão e Detecção Estatística</span>
            </div>
          </div>

          <div class="col-12">
            <ForecastChart
              title="Previsão de Pedidos para os Próximos 30 Dias"
              :data="forecast"
            />
          </div>

          <div class="col-12">
            <AnomalyChart
              title="Detecção Contínua de Anomalias de Volume"
              :data="anomalies"
            />
          </div>

          <!-- 2. Dinâmica de Vendas e Faturamento -->
          <div class="col-12 q-mt-sm">
            <div class="section-tag row items-center q-mb-sm">
              <q-icon name="point_of_sale" size="18px" class="q-mr-xs text-primary" />
              <span class="text-weight-bold text-caption text-uppercase">Dinâmica Temporal & Receita</span>
            </div>
          </div>

          <div class="col-12 col-md-6">
            <SalesChart
              title="Distribuição de Pedidos por Hora"
              type="area"
              series-name="Pedidos"
              :labels="hour.hours"
              :data="hour.series"
              badge="Pico às 16h"
              badge-color="primary"
              description="Mostra o volume acumulado de pedidos ao longo das 24 horas do dia, essencial para planejamento de campanhas e suporte."
            />
          </div>

          <div class="col-12 col-md-6">
            <SalesChart
              title="Faturamento Mensal Consolidado"
              type="area"
              series-name="Faturamento"
              currency
              :labels="filteredMonth.months"
              :data="filteredMonth.series"
              badge="Histórico"
              badge-color="positive"
              description="Soma da receita bruta gerada por pedidos concluídos a cada mês, descontando pedidos cancelados."
            />
          </div>

          <!-- 3. Satisfação, Pagamentos e Logística -->
          <div class="col-12 q-mt-sm">
            <div class="section-tag row items-center q-mb-sm">
              <q-icon name="local_shipping" size="18px" class="q-mr-xs text-amber-9" />
              <span class="text-weight-bold text-caption text-uppercase">Logística, Pagamentos & Categorias</span>
            </div>
          </div>

          <div class="col-12 col-md-6">
            <SalesChart
              title="Impacto do Prazo de Entrega na Nota"
              type="bar"
              series-name="Nota Média"
              :labels="dvs.faixas"
              :data="dvs.series"
              :y-min="0"
              :y-max="5"
              badge="Sensibilidade"
              badge-color="amber-9"
              description="Correlação entre dias de entrega e nota de avaliação (1 a 5). Prazos acima de 21 dias registram queda acentuada na satisfação."
            />
          </div>

          <div class="col-12 col-md-6">
            <SalesChart
              title="Métodos de Pagamento Utilizados"
              type="donut"
              :labels="pay.labels"
              :data="pay.series"
              badge="Preferência"
              badge-color="purple-7"
              description="Proporção das compras realizadas por cartão de crédito, boleto, voucher e débito."
            />
          </div>

          <div class="col-12 col-md-6">
            <SalesChart
              title="Top 10 Estados por Volume de Pedidos"
              type="bar"
              series-name="Pedidos"
              horizontal
              :labels="states.states"
              :data="states.series"
              badge="Regional"
              badge-color="indigo-7"
              description="Concentração geográfica da base de compradores nos 10 maiores estados brasileiros."
            />
          </div>

          <div class="col-12 col-md-6">
            <SalesChart
              title="Top 10 Categorias por Receita"
              type="bar"
              series-name="Receita"
              horizontal
              currency
              :labels="cats.categories"
              :data="cats.series"
              badge="Rentabilidade"
              badge-color="teal-8"
              description="Classificação dos segmentos de produtos com maior volume monetário faturado."
            />
          </div>
        </div>
      </div>

      <!-- Co-piloto de Inteligência Artificial Lateral -->
      <div class="col-12 col-lg-4">
        <div class="sticky-ai">
          <AiInsightPanel />
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import KpiCard from '../components/KpiCard.vue'
import SalesChart from '../components/SalesChart.vue'
import AnomalyChart from '../components/AnomalyChart.vue'
import ForecastChart from '../components/ForecastChart.vue'
import AiInsightPanel from '../components/AiInsightPanel.vue'
import type {
  Kpis,
  HourChart,
  MonthChart,
  DeliveryScoreChart,
  PaymentChart,
  StatesChart,
  CategoriesChart,
  AnomalyChartData,
  ForecastChartData
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
const anomalies = ref<AnomalyChartData>({
  dates: [],
  series: [],
  upper: [],
  lower: [],
  anomalies: []
})
const forecast = ref<ForecastChartData>({
  history_dates: [],
  history: [],
  forecast_dates: [],
  forecast: [],
  lower: [],
  upper: [],
  horizon_days: 30,
  total_forecast: 0
})

const error = ref('')
const refreshing = ref(false)
const periodFilter = ref<'all' | '2017' | '2018'>('all')

const filteredMonth = computed<MonthChart>(() => {
  if (periodFilter.value === 'all') return month.value
  const indices: number[] = []
  month.value.months.forEach((m, idx) => {
    if (m.startsWith(periodFilter.value)) {
      indices.push(idx)
    }
  })
  return {
    months: indices.map((i) => month.value.months[i]),
    series: indices.map((i) => month.value.series[i])
  }
})

const brl = (v: number): string =>
  v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 })

const kpiCards = computed<KpiCardProps[]>(() => {
  const k = kpis.value
  if (!k) return []
  return [
    {
      title: 'Faturamento Total',
      value: brl(k.total_sales),
      subtitle: `${k.total_orders.toLocaleString('pt-BR')} pedidos processados`,
      icon: 'attach_money',
      color: 'positive'
    },
    {
      title: 'Tempo Médio Entrega',
      value: `${k.avg_delivery_days} dias`,
      subtitle: `${k.late_rate}% entregas em atraso`,
      icon: 'local_shipping',
      color: 'primary'
    },
    {
      title: 'Taxa de Cancelamento',
      value: `${k.cancellation_rate}%`,
      subtitle: 'Meta: abaixo de 1.5%',
      icon: 'cancel',
      color: 'negative'
    },
    {
      title: 'Satisfação do Cliente',
      value: `${k.avg_review_score} / 5.0`,
      subtitle: 'Média de avaliações',
      icon: 'grade',
      color: 'amber-8'
    }
  ]
})

async function fetchData(): Promise<void> {
  refreshing.value = true
  error.value = ''
  try {
    const [a, b, c, d, e, f, g, h, i] = await Promise.all([
      api.get<Kpis>('/kpis'),
      api.get<HourChart>('/charts/orders-by-hour'),
      api.get<MonthChart>('/charts/sales-by-month'),
      api.get<DeliveryScoreChart>('/charts/delivery-vs-score'),
      api.get<PaymentChart>('/charts/payments'),
      api.get<StatesChart>('/charts/top-states'),
      api.get<CategoriesChart>('/charts/top-categories'),
      api.get<AnomalyChartData>('/charts/anomalies'),
      api.get<ForecastChartData>('/charts/forecast')
    ])
    kpis.value = a.data
    hour.value = b.data
    month.value = c.data
    dvs.value = d.data
    pay.value = e.data
    states.value = f.data
    cats.value = g.data
    anomalies.value = h.data
    forecast.value = i.data
  } catch {
    error.value = 'Não foi possível conectar ao backend Flask (porta 5000). Verifique se o serviço está ativo.'
  } finally {
    refreshing.value = false
  }
}

onMounted(() => {
  void fetchData()
})
</script>

<style scoped>
.main-page {
  background-color: #F8FAFC;
  min-height: 100vh;
  transition: background-color 0.3s ease;
}

.main-page--dark {
  background-color: #12121B;
}

.text-sub {
  color: #64748B;
  margin-top: 2px;
}

.section-tag {
  letter-spacing: 0.8px;
  color: #64748B;
  opacity: 0.9;
}

.sticky-ai {
  position: sticky;
  top: 76px;
}
</style>

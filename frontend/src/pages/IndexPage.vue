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

        <!-- Botão de Exportação de Relatórios -->
        <q-btn-dropdown
          outline
          no-caps
          rounded
          dense
          icon="file_download"
          label="Exportar"
          :color="$q.dark.isActive ? 'grey-4' : 'primary'"
          class="q-px-sm"
        >
          <q-list dense>
            <q-item clickable v-close-popup @click="showReportModal = true">
              <q-item-section avatar>
                <q-icon name="picture_as_pdf" color="primary" />
              </q-item-section>
              <q-item-section>
                <q-item-label class="text-weight-bold">Relatório Executivo (PDF / Print)</q-item-label>
                <q-item-label caption>Layout oficial formatado para apresentação</q-item-label>
              </q-item-section>
            </q-item>

            <q-item clickable v-close-popup @click="downloadCsv">
              <q-item-section avatar>
                <q-icon name="table_view" color="positive" />
              </q-item-section>
              <q-item-section>
                <q-item-label class="text-weight-bold">Planilha de Métricas (CSV / Excel)</q-item-label>
                <q-item-label caption>Dados brutos com acentuação UTF-8</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>

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
          <!-- 1. INTELIGÊNCIA PREDITIVA & ANOMALIAS -->
          <div class="col-12">
            <div class="section-tag row items-center q-mb-xs">
              <q-icon name="insights" size="18px" class="q-mr-xs text-secondary" />
              <span class="text-weight-bold text-caption text-uppercase">Previsão e Detecção Estatística</span>
            </div>
          </div>

          <div class="col-12">
            <ForecastChart
              :title="forecast.metric === 'revenue' ? 'Projeção de Faturamento para os Próximos 30 Dias' : 'Previsão de Pedidos para os Próximos 30 Dias'"
              :data="forecast"
              @metric-change="onForecastMetricChange"
            />
          </div>

          <div class="col-12">
            <AnomalyChart
              title="Detecção Contínua de Anomalias de Volume"
              :data="anomalies"
            />
          </div>

          <!-- SIMULADOR WHAT-IF DE DECISÕES ESTRATÉGICAS -->
          <div class="col-12 q-mt-sm">
            <ScenarioSimulator @ask-ai-scenario="onAskAiScenario" />
          </div>

          <!-- 2. CADEIA LOGÍSTICA & EFICIÊNCIA OPERACIONAL -->
          <div class="col-12 q-mt-sm">
            <div class="section-tag row items-center q-mb-xs">
              <q-icon name="local_shipping" size="18px" class="q-mr-xs text-amber-9" />
              <span class="text-weight-bold text-caption text-uppercase">Cadeia Logística & Prazos</span>
            </div>
          </div>

          <div class="col-12 col-md-6">
            <SalesChart
              title="Tempo Médio por Etapa Logística"
              type="bar"
              series-name="Dias Médios"
              unit="dias"
              :labels="leadTime.stages"
              :data="leadTime.series"
              badge="Gargalo"
              badge-color="deep-orange"
              description="Decompõe o prazo total: 1) Aprovação financeira (0.01 dia), 2) Despacho pelo Seller (1.8 dias) e 3) Trânsito com Transportadora (7.1 dias). Revela que 79% do tempo decorre do transporte interestadual."
            />
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
              description="Correlação entre dias de entrega e nota de avaliação (1 a 5). Prazos acima de 21 dias registram queda acentuada na satisfação do consumidor."
            />
          </div>

          <div class="col-12 col-md-6">
            <SalesChart
              title="Peso do Frete sobre o Pedido por Região"
              type="bar"
              series-name="Frete / Receita"
              percentage
              :labels="freightRegion.regions"
              :data="freightRegion.series"
              badge="Regional"
              badge-color="purple-8"
              description="Mediana da razão entre o valor do frete e o preço dos produtos. No Norte e Nordeste, o frete ultrapassa 30-35% do valor da mercadoria, sendo principal causa de desistências."
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
              badge="Concentração"
              badge-color="indigo-7"
              description="Concentração geográfica da base de compradores nos 10 maiores estados brasileiros."
            />
          </div>

          <!-- 3. COMERCIAL, PAGAMENTOS & ALAVANCAGEM DE TICKET -->
          <div class="col-12 q-mt-sm">
            <div class="section-tag row items-center q-mb-xs">
              <q-icon name="point_of_sale" size="18px" class="q-mr-xs text-primary" />
              <span class="text-weight-bold text-caption text-uppercase">Comercial, Meios de Pagamento & Ticket</span>
            </div>
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

          <div class="col-12 col-md-6">
            <SalesChart
              title="Ticket Médio por Número de Parcelas"
              type="bar"
              series-name="Ticket Médio"
              currency
              :labels="installments.installments"
              :data="installments.series"
              badge="Alavancagem"
              badge-color="teal-8"
              description="Analisa como o parcelamento no cartão estimula compras maiores: de R$ 96 em 1x para mais de R$ 330 em 7-10x (+240% de ticket médio)."
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
              badge-color="cyan-8"
              description="Classificação dos segmentos de produtos com maior volume monetário faturado."
            />
          </div>

          <div class="col-12 col-md-6">
            <SalesChart
              title="Distribuição das Avaliações (CSAT)"
              type="donut"
              :labels="reviewsDist.scores"
              :data="reviewsDist.series"
              badge="Satisfação"
              badge-color="amber-8"
              description="Distribuição global das notas deixadas pelos clientes: 57.8% de 5 estrelas e 11.5% de detratores com 1 estrela."
            />
          </div>

          <div class="col-12 col-md-6">
            <SalesChart
              title="Causas de Insatisfação (Reviews 1-2★)"
              type="bar"
              series-name="Menções"
              horizontal
              :labels="reviewTopics.topics"
              :data="reviewTopics.series"
              badge="Causa-Raiz"
              badge-color="negative"
              description="Análise das 10.890 avaliações de detratores. Revela que 58.6% de todas as notas baixas são causadas exclusivamente por atrasos de entrega ou mercadoria não recebida."
            />
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
              title="Métodos de Pagamento Utilizados"
              type="donut"
              :labels="pay.labels"
              :data="pay.series"
              badge="Preferência"
              badge-color="purple-7"
              description="Proporção das compras realizadas por cartão de crédito, boleto bancário, voucher e débito."
            />
          </div>
        </div>
      </div>

      <!-- Co-piloto de Inteligência Artificial Lateral -->
      <div class="col-12 col-lg-4">
        <div class="sticky-ai">
          <AiInsightPanel ref="aiPanel" />
        </div>
      </div>
    </div>

    <!-- Modal de Relatório Executivo Oficial (A4 Print / PDF Ready) -->
    <ExecutiveReportModal
      v-model="showReportModal"
      :kpis="kpis"
      :forecast="forecast"
      :anomalies-count="anomalies.anomalies.length"
    />
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import KpiCard from '../components/KpiCard.vue'
import SalesChart from '../components/SalesChart.vue'
import AnomalyChart from '../components/AnomalyChart.vue'
import ForecastChart from '../components/ForecastChart.vue'
import ScenarioSimulator from '../components/ScenarioSimulator.vue'
import ExecutiveReportModal from '../components/ExecutiveReportModal.vue'
import AiInsightPanel from '../components/AiInsightPanel.vue'
import type {
  Kpis,
  HourChart,
  MonthChart,
  DeliveryScoreChart,
  PaymentChart,
  StatesChart,
  CategoriesChart,
  LeadTimeChart,
  FreightRegionChart,
  InstallmentsTicketChart,
  ReviewsDistributionChart,
  ReviewTopicsChart,
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

const leadTime = ref<LeadTimeChart>({ stages: [], series: [] })
const freightRegion = ref<FreightRegionChart>({ regions: [], series: [] })
const installments = ref<InstallmentsTicketChart>({ installments: [], series: [] })
const reviewsDist = ref<ReviewsDistributionChart>({ scores: [], series: [] })
const reviewTopics = ref<ReviewTopicsChart>({ topics: [], series: [], percentages: [], total_detractors: 0 })

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
  total_forecast: 0,
  metric: 'orders'
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

const aiPanel = ref<{ askDirect: (q: string) => void } | null>(null)
const showReportModal = ref(false)

function downloadCsv(): void {
  window.open('http://localhost:5000/api/export/csv', '_blank')
}

function onAskAiScenario(q: string): void {
  if (aiPanel.value) {
    aiPanel.value.askDirect(q)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

async function onForecastMetricChange(metric: 'orders' | 'revenue'): Promise<void> {
  try {
    const res = await api.get<ForecastChartData>(`/charts/forecast?metric=${metric}`)
    forecast.value = res.data
  } catch (err) {
    console.error('Falha ao alternar métrica de previsão:', err)
  }
}

async function fetchData(): Promise<void> {
  refreshing.value = true
  error.value = ''
  try {
    const [a, b, c, d, e, f, g, h, i, j, l, m, n, o] = await Promise.all([
      api.get<Kpis>('/kpis'),
      api.get<HourChart>('/charts/orders-by-hour'),
      api.get<MonthChart>('/charts/sales-by-month'),
      api.get<DeliveryScoreChart>('/charts/delivery-vs-score'),
      api.get<PaymentChart>('/charts/payments'),
      api.get<StatesChart>('/charts/top-states'),
      api.get<CategoriesChart>('/charts/top-categories'),
      api.get<AnomalyChartData>('/charts/anomalies'),
      api.get<ForecastChartData>('/charts/forecast?metric=orders'),
      api.get<LeadTimeChart>('/charts/lead-time'),
      api.get<FreightRegionChart>('/charts/freight-by-region'),
      api.get<InstallmentsTicketChart>('/charts/installments-ticket'),
      api.get<ReviewsDistributionChart>('/charts/reviews-distribution'),
      api.get<ReviewTopicsChart>('/charts/review-topics')
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
    leadTime.value = j.data
    freightRegion.value = l.data
    installments.value = m.data
    reviewsDist.value = n.data
    reviewTopics.value = o.data
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

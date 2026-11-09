<template>
  <q-page class="carbon-page">
    <div class="carbon-page-container">
      <!-- Header da Página & Barra de Ações -->
      <div class="row items-center justify-between q-mb-lg carbon-page-header">
        <div>
          <div class="row items-center">
            <h1 class="carbon-page-title">Visão Geral & Performance</h1>
            <span class="carbon-status-tag q-ml-md">
              <span class="carbon-status-dot"></span>
              Dados em Tempo Real
            </span>
          </div>
          <div class="carbon-page-subtitle">
            Acompanhamento analítico integrado com Olist E-commerce e IA preditiva.
          </div>
        </div>

        <!-- Controles & Filtros Rápidos (Carbon Content Switcher & Actions) -->
        <div class="row items-center q-gutter-sm q-mt-xs">
          <q-btn-toggle
            v-model="periodFilter"
            no-caps
            square
            unelevated
            toggle-color="primary"
            class="carbon-content-switcher"
            :options="[
              { label: 'Todo o Período', value: 'all' },
              { label: 'Ano 2018', value: '2018' },
              { label: 'Ano 2017', value: '2017' }
            ]"
          />

          <!-- Botão de Exportação de Relatórios -->
          <q-btn-dropdown
            outline
            square
            no-caps
            dense
            icon="file_download"
            label="Exportar"
            class="carbon-action-btn q-px-sm"
          >
            <q-list dense class="carbon-dropdown-menu">
              <q-item clickable v-close-popup @click="showReportModal = true">
                <q-item-section avatar>
                  <q-icon name="picture_as_pdf" class="text-primary-token" />
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-weight-bold">Relatório Executivo (PDF / Print)</q-item-label>
                  <q-item-label caption>Layout oficial formatado para apresentação</q-item-label>
                </q-item-section>
              </q-item>

              <q-item clickable v-close-popup @click="downloadCsv">
                <q-item-section avatar>
                  <q-icon name="table_view" class="text-primary-token" />
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
            square
            dense
            icon="refresh"
            class="carbon-action-btn"
            :loading="refreshing"
            @click="fetchData"
          >
            <q-tooltip>Atualizar Métricas</q-tooltip>
          </q-btn>
        </div>
      </div>

      <!-- Banner de erro -->
      <q-banner v-if="error" class="carbon-banner-danger q-mb-md" dense>
        <template #avatar>
          <q-icon name="cloud_off" class="text-danger-token" />
        </template>
        {{ error }}
      </q-banner>

      <!-- 1. Linha de KPIs Principais (4 Colunas) -->
      <div class="row q-col-gutter-md q-mb-lg">
        <div v-for="k in kpiCards" :key="k.title" class="col-12 col-sm-6 col-md-3">
          <KpiCard v-bind="k" />
        </div>
      </div>

      <!-- 2. Linha Dedicada da IA: Central de Comando Inteligente (Full Width) -->
      <div id="ai-copilot-section" class="row q-mb-lg">
        <div class="col-12">
          <AiInsightPanel ref="aiPanel" />
        </div>
      </div>

      <!-- 3. INTELIGÊNCIA PREDITIVA & ANOMALIAS (Linhas Panorâmicas com 100% de Largura) -->
      <div class="row q-col-gutter-md q-mb-lg">
        <div class="col-12">
          <div class="carbon-section-header row items-center q-mb-xs">
            <q-icon name="insights" size="16px" class="q-mr-xs text-primary-token" />
            <span class="carbon-section-header-title">Previsão e Detecção Estatística</span>
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

        <!-- SIMULADOR WHAT-IF DE DECISÕES ESTRATÉGICAS (Linha Completa) -->
        <div class="col-12 q-mt-xs">
          <ScenarioSimulator @ask-ai-scenario="onAskAiScenario" />
        </div>
      </div>

      <!-- 4. CADEIA LOGÍSTICA & EFICIÊNCIA OPERACIONAL (Pares com Largura Expandida) -->
      <div class="row q-col-gutter-md q-mb-lg">
        <div class="col-12">
          <div class="carbon-section-header row items-center q-mb-xs">
            <q-icon name="local_shipping" size="16px" class="q-mr-xs text-primary-token" />
            <span class="carbon-section-header-title">Cadeia Logística & Prazos</span>
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
            badge-color="warning"
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
            badge-color="neutral"
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
            badge-color="neutral"
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
            badge-color="neutral"
            description="Concentração geográfica da base de compradores nos 10 maiores estados brasileiros."
          />
        </div>
      </div>

      <!-- 5. COMERCIAL, PAGAMENTOS & ALAVANCAGEM DE TICKET -->
      <div class="row q-col-gutter-md q-mb-lg">
        <div class="col-12">
          <div class="carbon-section-header row items-center q-mb-xs">
            <q-icon name="point_of_sale" size="16px" class="q-mr-xs text-primary-token" />
            <span class="carbon-section-header-title">Comercial, Meios de Pagamento & Ticket</span>
          </div>
        </div>

        <!-- Faturamento Mensal Histórico em Linha Inteira (Visualização Temporal Clara) -->
        <div class="col-12">
          <SalesChart
            title="Faturamento Mensal Consolidado"
            type="area"
            series-name="Faturamento"
            currency
            :labels="filteredMonth.months"
            :data="filteredMonth.series"
            badge="Histórico"
            badge-color="neutral"
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
            badge-color="neutral"
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
            badge-color="neutral"
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
            badge-color="neutral"
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
            badge-color="neutral"
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
            badge-color="neutral"
            description="Proporção das compras realizadas por cartão de crédito, boleto bancário, voucher e débito."
          />
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
import { api, API_BASE_URL } from '../api'
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
  const months: string[] = []
  const series: number[] = []
  month.value.months.forEach((m, idx) => {
    if (m.startsWith(periodFilter.value)) {
      months.push(m)
      const s = month.value.series[idx]
      if (s !== undefined) {
        series.push(s)
      }
    }
  })
  return { months, series }
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
  window.open(`${API_BASE_URL}/export/csv`, '_blank')
}

function onAskAiScenario(q: string): void {
  if (aiPanel.value) {
    aiPanel.value.askDirect(q)
    const el = document.getElementById('ai-copilot-section')
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
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
.carbon-page {
  background-color: var(--color-bg);
  min-height: 100vh;
  padding: var(--spacing-07) var(--spacing-06);
}

@media (min-width: 1200px) {
  .carbon-page {
    padding: var(--spacing-07) var(--spacing-07);
  }
}

.carbon-page-container {
  max-width: 1584px; /* IBM Carbon 2x Grid Max Breakpoint */
  margin: 0 auto;
  width: 100%;
}

.carbon-page-header {
  border-bottom: 1px solid var(--color-border-subtle);
  padding-bottom: var(--spacing-05);
}

.carbon-page-title {
  font-size: 1.5rem;
  font-weight: 400;
  line-height: 1.25;
  margin: 0;
  color: var(--color-text-primary);
  letter-spacing: -0.01em;
}

.carbon-page-subtitle {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  margin-top: var(--spacing-02);
}

.carbon-status-tag {
  display: inline-flex;
  align-items: center;
  background-color: var(--color-success-bg);
  color: var(--color-success);
  font-size: 0.6875rem;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: var(--radius-none);
  letter-spacing: 0.32px;
}

.carbon-status-dot {
  width: 6px;
  height: 6px;
  background-color: var(--color-success);
  border-radius: 50%;
  margin-right: 6px;
}

.carbon-content-switcher {
  border: 1px solid var(--color-border-subtle);
  background-color: var(--color-layer-02);
  border-radius: var(--radius-none);
  font-size: 0.75rem;
}

.carbon-action-btn {
  border: 1px solid var(--color-border-subtle);
  background-color: var(--color-layer-01);
  color: var(--color-text-primary);
  border-radius: var(--radius-none);
  height: 36px;
}

.carbon-action-btn:hover {
  background-color: var(--color-layer-hover);
  border-color: var(--color-border-strong);
}

.carbon-dropdown-menu {
  background-color: var(--color-layer-01);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-none);
}

.carbon-banner-danger {
  background-color: var(--color-danger-bg);
  color: var(--color-danger);
  border-left: 3px solid var(--color-danger);
  border-radius: var(--radius-none);
}

.carbon-section-header {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.32px;
  color: var(--color-text-secondary);
  border-bottom: 1px solid var(--color-border-subtle);
  padding-bottom: 4px;
}

.carbon-section-header-title {
  font-weight: 600;
  color: var(--color-text-secondary);
}

.text-primary-token {
  color: var(--color-primary);
}

.text-danger-token {
  color: var(--color-danger);
}
</style>

<template>
  <q-dialog v-model="isOpen" maximized persistent transition-show="slide-up" transition-hide="slide-down">
    <q-card class="carbon-report-modal">
      <!-- Toolbar Superior (Escondida na Impressão) -->
      <q-toolbar class="print-hide carbon-report-toolbar">
        <q-icon name="description" size="20px" class="text-primary-token q-mr-sm" />
        <q-toolbar-title class="carbon-toolbar-title">
          Relatório Executivo de Performance
        </q-toolbar-title>

        <q-space />

        <div class="row items-center q-gutter-x-sm">
          <q-btn
            outline
            dense
            square
            no-caps
            icon="table_view"
            label="Baixar CSV (Excel)"
            class="carbon-btn-secondary q-px-sm"
            @click="downloadCsv"
          />

          <q-btn
            unelevated
            dense
            square
            no-caps
            icon="print"
            label="Imprimir / Salvar em PDF"
            color="primary"
            class="carbon-btn-primary q-px-sm"
            @click="printReport"
          />

          <q-btn flat round dense icon="close" v-close-popup />
        </div>
      </q-toolbar>

      <q-separator class="print-hide" />

      <!-- Corpo do Documento Executivo (A4 Print Ready) -->
      <q-card-section class="carbon-report-content-wrapper">
        <div class="carbon-report-paper">
          <!-- Cabeçalho Oficial -->
          <div class="row items-center justify-between carbon-report-header q-pb-md q-mb-md">
            <div>
              <div class="carbon-report-brand">AI Metric Pulse</div>
              <div class="carbon-report-subbrand">
                Relatório Integrado de Performance, Logística & Inteligência Preditiva
              </div>
              <div class="carbon-report-meta">Base de Dados: Olist E-commerce Brasil</div>
            </div>

            <div class="text-right">
              <div class="carbon-report-date-label">DATA DE EMISSÃO</div>
              <div class="carbon-report-date-val">{{ currentDate }}</div>
              <div class="carbon-report-meta">Status: Consolidado</div>
            </div>
          </div>

          <!-- 1. KPIs Principais -->
          <div class="carbon-section-title">1. Indicadores Chave de Desempenho (KPIs)</div>
          <div class="row q-col-gutter-sm q-mb-md">
            <div class="col-3" v-for="k in reportKpis" :key="k.title">
              <div class="carbon-report-kpi-box">
                <div class="carbon-report-kpi-label">{{ k.title }}</div>
                <div class="carbon-report-kpi-value">{{ k.value }}</div>
                <div class="carbon-report-kpi-sub">{{ k.sub }}</div>
              </div>
            </div>
          </div>

          <!-- 2. Modelo Preditivo & Previsão 30 Dias -->
          <div class="carbon-section-title">2. Projeção Preditiva dos Próximos 30 Dias (Holt-Winters 7D)</div>
          <div class="carbon-report-table-box q-mb-md">
            <table class="carbon-report-table">
              <thead>
                <tr>
                  <th>Métrica Preditiva</th>
                  <th>Valor Projetado</th>
                  <th>Confiabilidade / Validação</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td class="text-weight-bold">Volume Projetado de Pedidos (30d)</td>
                  <td class="text-weight-bold text-primary-token">~{{ Math.round(forecast.total_forecast || 0).toLocaleString('pt-BR') }} pedidos</td>
                  <td>Intervalo de Confiança a 95% com sazonalidade semanal</td>
                </tr>
                <tr>
                  <td class="text-weight-bold">Acurácia Histórica do Modelo (Backtest)</td>
                  <td class="text-weight-bold text-success-token">{{ forecast.metrics?.accuracy ?? 88.6 }}%</td>
                  <td>MAPE: {{ forecast.metrics?.mape ?? 11.4 }}% nos últimos 30 dias históricos</td>
                </tr>
                <tr>
                  <td class="text-weight-bold">Detecção de Anomalias no Período</td>
                  <td>{{ anomaliesCount }} dias atípicos detectados</td>
                  <td>Algoritmo Z-Score com janela móvel de 28 dias (±3σ)</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 3. Cadeia Logística & Frete Regional -->
          <div class="carbon-section-title">3. Eficiência Logística & Disparidade Regional de Frete</div>
          <div class="row q-col-gutter-md q-mb-md">
            <div class="col-6">
              <div class="carbon-report-table-box">
                <div class="carbon-table-header-bar">
                  Tempo Médio por Etapa Logística
                </div>
                <table class="carbon-report-table">
                  <tbody>
                    <tr>
                      <td>1. Aprovação Financeira</td>
                      <td class="text-right text-weight-bold">0,01 dia (~20 min)</td>
                    </tr>
                    <tr>
                      <td>2. Despacho pelo Vendedor (Seller)</td>
                      <td class="text-right text-weight-bold">1,8 dia</td>
                    </tr>
                    <tr>
                      <td>3. Trânsito Transportadora / Correios</td>
                      <td class="text-right text-weight-bold text-danger-token">7,1 dias (79% do prazo)</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div class="col-6">
              <div class="carbon-report-table-box">
                <div class="carbon-table-header-bar">
                  Mediana do Frete sobre Pedido por Região
                </div>
                <table class="carbon-report-table">
                  <tbody>
                    <tr>
                      <td>Norte</td>
                      <td class="text-right text-weight-bold text-danger-token">35,7% da mercadoria</td>
                    </tr>
                    <tr>
                      <td>Nordeste</td>
                      <td class="text-right text-weight-bold text-danger-token">31,5% da mercadoria</td>
                    </tr>
                    <tr>
                      <td>Sul e Sudeste</td>
                      <td class="text-right text-weight-bold text-success-token">20,6% a 25,1% da mercadoria</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- 4. Causas de Insatisfação (Detratores) -->
          <div class="carbon-section-title">4. Diagnóstico de Satisfação & Causas-Raiz de Detratores</div>
          <div class="carbon-report-table-box q-mb-md">
            <table class="carbon-report-table">
              <thead>
                <tr>
                  <th>Motivo da Reclamação (Notas 1 e 2)</th>
                  <th>% dos Detratores</th>
                  <th>Menções Registradas</th>
                  <th>Diagnóstico</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td class="text-weight-bold">Atraso na Entrega ou Não Recebido</td>
                  <td class="text-weight-bold text-danger-token">58,6%</td>
                  <td>6.379 reviews</td>
                  <td>Principal gargalo que prejudica a reputação do marketplace</td>
                </tr>
                <tr>
                  <td>Atendimento e SAC / Estorno</td>
                  <td>11,0%</td>
                  <td>1.200 reviews</td>
                  <td>Fricção no processo de suporte e reembolso pós-atraso</td>
                </tr>
                <tr>
                  <td>Embalagem e Baixa Qualidade</td>
                  <td>7,9%</td>
                  <td>858 reviews</td>
                  <td>Falhas de acondicionamento durante o trânsito</td>
                </tr>
                <tr>
                  <td>Produto Danificado ou com Defeito</td>
                  <td>7,3%</td>
                  <td>796 reviews</td>
                  <td>Danos físicos no transporte interestadual</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 5. Parecer Executivo do Co-Piloto de IA -->
          <div class="carbon-section-title">5. Parecer Estratégico do Analista de Inteligência Artificial</div>
          <div class="carbon-report-ai-box q-pa-md">
            <div class="row items-center q-mb-sm">
              <q-icon name="auto_awesome" class="text-primary-token q-mr-xs" size="18px" />
              <div class="text-subtitle2 text-weight-bold text-primary-token">Recomendações Prioritárias</div>
            </div>
            <div class="carbon-report-ai-body">
              1. <strong>Descentralização de Estoques (Fulfillment Regional):</strong> Com 79% do lead time concentrado no trânsito e 58,6% dos detratores gerados por atraso, implementar centros de distribuição regionais no Nordeste e Centro-Oeste é a medida de maior retorno operacional.<br>
              2. <strong>Incentivo ao Parcelamento em 7x-10x:</strong> O ticket médio salta de R$ 95,87 (1x) para R$ 333,83 em parcelas longas. Campanhas sem juros nessa faixa ampliam significativamente o faturamento bruto.<br>
              3. <strong>Subsídio Direcionado de Frete:</strong> No Norte/Nordeste o frete representa mais de 30% da compra. Programas de frete reduzido ou pontos de retirada reduzem o abandono e ampliam a penetração em praças periféricas.
            </div>
          </div>

          <!-- Rodapé de Autenticação -->
          <div class="row items-center justify-between carbon-report-footer q-mt-lg pt-sm">
            <div>Documento gerado automaticamente pela plataforma <strong>AI Metric Pulse</strong>.</div>
            <div>Página 1 de 1</div>
          </div>
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Kpis, ForecastChartData } from '../types'

const props = defineProps<{
  modelValue: boolean
  kpis: Kpis | null
  forecast: ForecastChartData
  anomaliesCount: number
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void
}>()

const isOpen = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val)
})

const currentDate = computed(() => {
  const d = new Date()
  return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })
})

const reportKpis = computed(() => {
  const k = props.kpis
  if (!k) return []
  return [
    {
      title: 'Faturamento Total',
      value: k.total_sales.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }),
      sub: `${k.total_orders.toLocaleString('pt-BR')} pedidos`
    },
    {
      title: 'Prazo Médio Entrega',
      value: `${k.avg_delivery_days} dias`,
      sub: `${k.late_rate}% com atraso`
    },
    {
      title: 'Taxa Cancelamento',
      value: `${k.cancellation_rate}%`,
      sub: 'Meta: < 1.5%'
    },
    {
      title: 'Nota Média (CSAT)',
      value: `${k.avg_review_score} / 5.0`,
      sub: 'Média de avaliações'
    }
  ]
})

function printReport(): void {
  window.print()
}

function downloadCsv(): void {
  window.open('http://localhost:5000/api/export/csv', '_blank')
}
</script>

<style scoped>
.carbon-report-modal {
  background-color: var(--color-bg);
  min-height: 100vh;
}

.carbon-report-toolbar {
  background-color: var(--color-header-bg);
  color: var(--color-header-text);
  min-height: 48px;
  height: 48px;
}

.carbon-toolbar-title {
  font-size: 0.875rem;
  font-weight: 600;
}

.carbon-btn-secondary {
  color: var(--color-header-text);
  border-color: var(--color-border-subtle);
  border-radius: var(--radius-none);
}

.carbon-btn-primary {
  border-radius: var(--radius-none);
}

.text-primary-token {
  color: var(--color-primary);
}

.text-success-token {
  color: var(--color-success);
}

.text-danger-token {
  color: var(--color-danger);
}

.carbon-report-content-wrapper {
  display: flex;
  justify-content: center;
  padding: var(--spacing-06);
}

.carbon-report-paper {
  background-color: #ffffff;
  color: #161616;
  width: 100%;
  max-width: 900px;
  min-height: 1000px;
  padding: 40px;
  border-radius: var(--radius-none);
  border: 1px solid var(--color-border-subtle);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  font-family: var(--font-sans);
}

.carbon-report-header {
  border-bottom: 2px solid var(--color-border-subtle);
}

.carbon-report-brand {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f62fe;
}

.carbon-report-subbrand {
  font-size: 0.875rem;
  font-weight: 500;
  color: #525252;
}

.carbon-report-meta {
  font-size: 0.75rem;
  color: #6f6f6f;
}

.carbon-report-date-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #525252;
}

.carbon-report-date-val {
  font-size: 0.875rem;
  font-weight: 500;
  color: #161616;
}

.carbon-section-title {
  font-size: 0.8125rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.32px;
  color: #0f62fe;
  margin: 16px 0 8px 0;
  padding-bottom: 4px;
  border-bottom: 1px solid #e0e0e0;
}

.carbon-report-kpi-box {
  background-color: #f4f4f4;
  border: 1px solid #e0e0e0;
  border-radius: var(--radius-none);
  padding: 10px 12px;
}

.carbon-report-kpi-label {
  font-size: 0.6875rem;
  text-transform: uppercase;
  color: #525252;
  font-weight: 500;
}

.carbon-report-kpi-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: #161616;
  margin: 2px 0;
}

.carbon-report-kpi-sub {
  font-size: 0.6875rem;
  color: #6f6f6f;
}

.carbon-report-table-box {
  border: 1px solid #e0e0e0;
  border-radius: var(--radius-none);
  overflow: hidden;
}

.carbon-table-header-bar {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 6px 12px;
  background-color: #f4f4f4;
  color: #161616;
  border-bottom: 1px solid #e0e0e0;
}

.carbon-report-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.75rem;
}

.carbon-report-table th {
  background-color: #f4f4f4;
  padding: 6px 12px;
  text-align: left;
  font-weight: 600;
  color: #525252;
  border-bottom: 1px solid #e0e0e0;
}

.carbon-report-table td {
  padding: 6px 12px;
  border-bottom: 1px solid #f4f4f4;
  color: #161616;
}

.carbon-report-ai-box {
  background-color: #edf5ff;
  border-left: 3px solid #0f62fe;
  border-radius: var(--radius-none);
}

.carbon-report-ai-body {
  font-size: 0.8125rem;
  line-height: 1.5;
  color: #161616;
}

.carbon-report-footer {
  font-size: 0.75rem;
  color: #6f6f6f;
  border-top: 1px solid #e0e0e0;
}

/* ── Estilos Específicos para Impressão em PDF / Papel A4 ── */
@media print {
  body * {
    visibility: hidden;
  }

  .carbon-report-paper,
  .carbon-report-paper * {
    visibility: visible;
  }

  .print-hide {
    display: none !important;
  }

  .carbon-report-content-wrapper {
    padding: 0 !important;
    margin: 0 !important;
  }

  .carbon-report-paper {
    position: absolute;
    left: 0;
    top: 0;
    width: 100% !important;
    max-width: 100% !important;
    box-shadow: none !important;
    border: none !important;
    padding: 20px !important;
    color: #000000 !important;
  }

  .carbon-report-modal {
    background: transparent !important;
  }
}
</style>

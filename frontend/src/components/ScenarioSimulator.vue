<template>
  <q-card flat class="carbon-simulator-card">
    <q-card-section class="q-pb-sm">
      <div class="row items-center justify-between no-wrap q-mb-xs">
        <div class="row items-center no-wrap">
          <q-icon name="tune" class="text-primary-token q-mr-sm" size="20px" />
          <div>
            <div class="carbon-sim-title">Simulador de Decisões Estratégicas (What-If)</div>
            <div class="carbon-sim-sub">Simule o impacto de alavancas operacionais na receita e satisfação</div>
          </div>
        </div>

        <div class="row items-center q-gutter-x-sm">
          <q-btn
            flat
            dense
            no-caps
            size="sm"
            icon="restart_alt"
            label="Redefinir"
            class="carbon-reset-btn"
            @click="resetSliders"
          />
          <span class="carbon-tag carbon-tag--neutral">Olist Elasticity Model</span>
        </div>
      </div>
    </q-card-section>

    <q-separator />

    <q-card-section class="q-py-md">
      <!-- Sliders de Decisão (Carbon Sliders com Cor Primária Única) -->
      <div class="row q-col-gutter-md q-mb-md">
        <!-- 1. Redução de Prazo -->
        <div class="col-12 col-md-4">
          <div class="carbon-slider-tile">
            <div class="row items-center justify-between q-mb-xs">
              <div class="row items-center">
                <q-icon name="speed" class="text-primary-token q-mr-xs" size="16px" />
                <span class="text-caption text-weight-medium">Redução no Prazo de Entrega</span>
              </div>
              <span class="carbon-tag carbon-tag--primary">-{{ deliveryReduction }} dias</span>
            </div>
            <div class="carbon-slider-hint q-mb-sm">A cada 1 dia reduzido: +0.045 estrelas no review</div>
            <q-slider
              v-model="deliveryReduction"
              :min="0"
              :max="7"
              :step="0.5"
              color="primary"
              label
              :label-value="`-${deliveryReduction}d`"
              @change="triggerSimulation"
            />
          </div>
        </div>

        <!-- 2. Parcelamento Longo -->
        <div class="col-12 col-md-4">
          <div class="carbon-slider-tile">
            <div class="row items-center justify-between q-mb-xs">
              <div class="row items-center">
                <q-icon name="credit_score" class="text-primary-token q-mr-xs" size="16px" />
                <span class="text-caption text-weight-medium">Incentivo a Parcelamento (7x-10x)</span>
              </div>
              <span class="carbon-tag carbon-tag--primary">+{{ installmentsBoost }}%</span>
            </div>
            <div class="carbon-slider-hint q-mb-sm">Migração de compras 1x (R$ 96) para 7x+ (R$ 334)</div>
            <q-slider
              v-model="installmentsBoost"
              :min="0"
              :max="30"
              :step="5"
              color="primary"
              label
              :label-value="`+${installmentsBoost}%`"
              @change="triggerSimulation"
            />
          </div>
        </div>

        <!-- 3. Subsídio Frete Norte/Nordeste -->
        <div class="col-12 col-md-4">
          <div class="carbon-slider-tile">
            <div class="row items-center justify-between q-mb-xs">
              <div class="row items-center">
                <q-icon name="local_shipping" class="text-primary-token q-mr-xs" size="16px" />
                <span class="text-caption text-weight-medium">Desconto de Frete (Norte/Nordeste)</span>
              </div>
              <span class="carbon-tag carbon-tag--primary">-{{ freightDiscount }}% frete</span>
            </div>
            <div class="carbon-slider-hint q-mb-sm">Regiões onde o frete corrói >30% do pedido</div>
            <q-slider
              v-model="freightDiscount"
              :min="0"
              :max="40"
              :step="5"
              color="primary"
              label
              :label-value="`-${freightDiscount}%`"
              @change="triggerSimulation"
            />
          </div>
        </div>
      </div>

      <!-- Resultados Projetados em Tiles Carbon -->
      <div class="row q-col-gutter-md q-mt-xs">
        <!-- Tile 1: Faturamento Adicional -->
        <div class="col-12 col-sm-6 col-md-3">
          <div class="carbon-result-tile">
            <div class="carbon-tile-label">Faturamento Adicional Estimado</div>
            <div class="carbon-tile-value text-success-token q-my-xs">
              {{ sim ? '+ ' + formatBrl(sim.deltas.revenue) : '+ R$ 0' }}
            </div>
            <div class="carbon-tile-sub">
              Novo Total: {{ sim ? formatBrl(sim.projected.revenue) : 'R$ 0' }}
            </div>
          </div>
        </div>

        <!-- Tile 2: Nova Nota Média -->
        <div class="col-12 col-sm-6 col-md-3">
          <div class="carbon-result-tile">
            <div class="carbon-tile-label">Nova Nota Média Projetada</div>
            <div class="carbon-tile-value q-my-xs row items-center">
              <span>{{ sim ? sim.projected.score : '4.09' }}</span>
              <q-icon name="star" size="18px" class="q-ml-xs text-primary-token" />
              <span v-if="sim && sim.deltas.score > 0" class="carbon-tag carbon-tag--success q-ml-sm">
                +{{ sim.deltas.score }}
              </span>
            </div>
            <div class="carbon-tile-sub">
              Base atual: {{ sim ? sim.base.score : '4.09' }} / 5.0
            </div>
          </div>
        </div>

        <!-- Tile 3: Detratores Evitados -->
        <div class="col-12 col-sm-6 col-md-3">
          <div class="carbon-result-tile">
            <div class="carbon-tile-label">Reclamações Críticas Evitadas</div>
            <div class="carbon-tile-value q-my-xs row items-center">
              <span class="text-success-token">{{ sim ? '-' + sim.deltas.detractors_avoided.toLocaleString('pt-BR') : '0' }}</span>
              <q-icon name="mood" size="18px" class="q-ml-xs text-success-token" />
            </div>
            <div class="carbon-tile-sub">
              Clientes que deixam de dar nota 1 ou 2
            </div>
          </div>
        </div>

        <!-- Tile 4: Novos Pedidos -->
        <div class="col-12 col-sm-6 col-md-3">
          <div class="carbon-result-tile">
            <div class="carbon-tile-label">Novos Pedidos em N/NE</div>
            <div class="carbon-tile-value text-primary-token q-my-xs">
              {{ sim ? '+ ' + sim.deltas.new_orders.toLocaleString('pt-BR') : '+ 0' }}
            </div>
            <div class="carbon-tile-sub">
              Novo Ticket: {{ sim ? formatBrl(sim.projected.ticket) : 'R$ 0' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Barra de Ação Executiva com IA -->
      <div class="row items-center justify-between q-mt-md q-pa-sm carbon-sim-action-bar">
        <div class="row items-center q-gutter-x-sm text-caption">
          <q-icon name="psychology" size="18px" class="text-primary-token" />
          <span>Deseja um parecer executivo sobre o Retorno sobre Investimento (ROI) desta simulação?</span>
        </div>

        <q-btn
          dense
          no-caps
          unelevated
          square
          color="primary"
          icon="auto_awesome"
          label="Pedir Parecer da IA sobre este Cenário"
          class="carbon-primary-btn q-px-md"
          @click="askAiAboutScenario"
        />
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '../api'
import type { SimulationResult } from '../types'

const emit = defineEmits<{
  (e: 'ask-ai-scenario', question: string): void
}>()

const deliveryReduction = ref(3)
const installmentsBoost = ref(15)
const freightDiscount = ref(20)

const sim = ref<SimulationResult | null>(null)

const formatBrl = (v: number) =>
  v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 })

async function triggerSimulation(): Promise<void> {
  try {
    const res = await api.post<SimulationResult>('/simulate', {
      delivery_reduction: deliveryReduction.value,
      installments_boost: installmentsBoost.value,
      freight_discount_ne: freightDiscount.value
    })
    sim.value = res.data
  } catch (err) {
    console.error('Falha ao rodar simulação:', err)
  }
}

function resetSliders(): void {
  deliveryReduction.value = 0
  installmentsBoost.value = 0
  freightDiscount.value = 0
  void triggerSimulation()
}

function askAiAboutScenario(): void {
  const q = `Avalie a viabilidade executiva deste cenário simulado no e-commerce:
1. Reduzir o prazo médio de entrega em ${deliveryReduction.value} dias.
2. Incentivar compras parceladas (7x a 10x) em +${installmentsBoost.value}%.
3. Conceder ${freightDiscount.value}% de desconto/subsídio de frete no Norte e Nordeste.
Resultados simulados: Faturamento adicional de ${sim.value ? formatBrl(sim.value.deltas.revenue) : 'R$ 0'}, aumento de nota para ${sim.value ? sim.value.projected.score : '4.2'} e ${sim.value ? sim.value.deltas.detractors_avoided : '1600'} detratores a menos.
Quais os riscos operacionais, o ROI provável e os primeiros passos recomendados?`

  emit('ask-ai-scenario', q)
}

onMounted(() => {
  void triggerSimulation()
})
</script>

<style scoped>
.carbon-simulator-card {
  border-radius: var(--radius-none);
  border: 1px solid var(--color-border-subtle);
  background: var(--color-layer-01);
  box-shadow: none;
  transition: border-color 0.15s ease, background-color 0.2s ease;
}

.carbon-simulator-card:hover {
  border-color: var(--color-border-strong);
}

.carbon-sim-title {
  font-size: 0.875rem;
  font-weight: 600;
  letter-spacing: 0.16px;
  color: var(--color-text-primary);
}

.carbon-sim-sub {
  font-size: 0.75rem;
  color: var(--color-text-helper);
}

.text-primary-token {
  color: var(--color-primary);
}

.text-success-token {
  color: var(--color-success);
}

.carbon-reset-btn {
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

.carbon-tag--primary {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

.carbon-tag--success {
  background-color: var(--color-success-bg);
  color: var(--color-success);
}

.carbon-slider-tile {
  background-color: var(--color-layer-02);
  padding: var(--spacing-04) var(--spacing-05);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-none);
}

.carbon-slider-hint {
  font-size: 0.6875rem;
  color: var(--color-text-helper);
}

.carbon-result-tile {
  background-color: var(--color-layer-02);
  padding: var(--spacing-04) var(--spacing-05);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-none);
}

.carbon-tile-label {
  font-size: 0.6875rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.32px;
  color: var(--color-text-secondary);
}

.carbon-tile-value {
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--color-text-primary);
}

.carbon-tile-sub {
  font-size: 0.6875rem;
  color: var(--color-text-helper);
}

.carbon-sim-action-bar {
  background-color: var(--color-layer-02);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-none);
  color: var(--color-text-primary);
}

.carbon-primary-btn {
  border-radius: var(--radius-none);
  font-size: 0.75rem;
  font-weight: 500;
}
</style>

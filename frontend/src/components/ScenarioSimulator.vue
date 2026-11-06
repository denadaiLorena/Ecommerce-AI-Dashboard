<template>
  <q-card flat class="simulator-card" :class="{ 'simulator-card--dark': $q.dark.isActive }">
    <q-card-section class="q-pb-sm">
      <div class="row items-center justify-between no-wrap q-mb-xs">
        <div class="row items-center no-wrap">
          <div class="sim-icon-bubble q-mr-sm">
            <q-icon name="tune" color="white" size="20px" />
          </div>
          <div>
            <div class="text-subtitle1 text-weight-bold">Simulador de Decisões Estratégicas (What-If)</div>
            <div class="text-caption text-sub">Simule o impacto de alavancas operacionais na receita e satisfação</div>
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
            :color="$q.dark.isActive ? 'grey-4' : 'grey-7'"
            @click="resetSliders"
          />
          <q-badge color="deep-purple-7" rounded label="Olist Elasticity Model" />
        </div>
      </div>
    </q-card-section>

    <q-separator :dark="$q.dark.isActive" />

    <q-card-section class="q-py-md">
      <!-- Sliders de Decisão -->
      <div class="row q-col-gutter-lg q-mb-md">
        <!-- 1. Redução de Prazo -->
        <div class="col-12 col-md-4">
          <div class="slider-box" :class="{ 'slider-box--dark': $q.dark.isActive }">
            <div class="row items-center justify-between q-mb-xs">
              <div class="row items-center">
                <q-icon name="speed" color="primary" size="18px" class="q-mr-xs" />
                <span class="text-caption text-weight-bold">Redução no Prazo de Entrega</span>
              </div>
              <q-badge color="primary" rounded :label="`-${deliveryReduction} dias`" />
            </div>
            <div class="text-caption text-hint q-mb-sm">A cada 1 dia reduzido: +0.045 estrelas no review</div>
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
          <div class="slider-box" :class="{ 'slider-box--dark': $q.dark.isActive }">
            <div class="row items-center justify-between q-mb-xs">
              <div class="row items-center">
                <q-icon name="credit_score" color="teal" size="18px" class="q-mr-xs" />
                <span class="text-caption text-weight-bold">Incentivo a Parcelamento (7x-10x)</span>
              </div>
              <q-badge color="teal" rounded :label="`+${installmentsBoost}%`" />
            </div>
            <div class="text-caption text-hint q-mb-sm">Migração de compras 1x (R$ 96) para 7x+ (R$ 334)</div>
            <q-slider
              v-model="installmentsBoost"
              :min="0"
              :max="30"
              :step="5"
              color="teal"
              label
              :label-value="`+${installmentsBoost}%`"
              @change="triggerSimulation"
            />
          </div>
        </div>

        <!-- 3. Subsídio Frete Norte/Nordeste -->
        <div class="col-12 col-md-4">
          <div class="slider-box" :class="{ 'slider-box--dark': $q.dark.isActive }">
            <div class="row items-center justify-between q-mb-xs">
              <div class="row items-center">
                <q-icon name="local_shipping" color="deep-orange" size="18px" class="q-mr-xs" />
                <span class="text-caption text-weight-bold">Desconto de Frete (Norte/Nordeste)</span>
              </div>
              <q-badge color="deep-orange" rounded :label="`-${freightDiscount}% frete`" />
            </div>
            <div class="text-caption text-hint q-mb-sm">Regiões onde o frete corrói >30% do pedido</div>
            <q-slider
              v-model="freightDiscount"
              :min="0"
              :max="40"
              :step="5"
              color="deep-orange"
              label
              :label-value="`-${freightDiscount}%`"
              @change="triggerSimulation"
            />
          </div>
        </div>
      </div>

      <!-- Resultados Projetados em Cards -->
      <div class="row q-col-gutter-md q-mt-xs">
        <!-- Card 1: Faturamento Adicional -->
        <div class="col-12 col-sm-6 col-md-3">
          <div class="result-tile" :class="{ 'result-tile--dark': $q.dark.isActive }">
            <div class="text-caption text-label">Faturamento Adicional Estimado</div>
            <div class="text-h6 text-weight-bolder text-positive q-my-xs">
              {{ sim ? '+ ' + formatBrl(sim.deltas.revenue) : '+ R$ 0' }}
            </div>
            <div class="text-caption text-hint">
              Novo Total: {{ sim ? formatBrl(sim.projected.revenue) : 'R$ 0' }}
            </div>
          </div>
        </div>

        <!-- Card 2: Nova Nota Média -->
        <div class="col-12 col-sm-6 col-md-3">
          <div class="result-tile" :class="{ 'result-tile--dark': $q.dark.isActive }">
            <div class="text-caption text-label">Nova Nota Média Projetada</div>
            <div class="text-h6 text-weight-bolder text-amber-8 q-my-xs row items-center">
              <span>{{ sim ? sim.projected.score : '4.09' }}</span>
              <q-icon name="star" size="20px" color="amber-8" class="q-ml-xs" />
              <q-badge v-if="sim && sim.deltas.score > 0" color="positive" rounded class="q-ml-sm">
                +{{ sim.deltas.score }}
              </q-badge>
            </div>
            <div class="text-caption text-hint">
              Base atual: {{ sim ? sim.base.score : '4.09' }} / 5.0
            </div>
          </div>
        </div>

        <!-- Card 3: Detratores Evitados -->
        <div class="col-12 col-sm-6 col-md-3">
          <div class="result-tile" :class="{ 'result-tile--dark': $q.dark.isActive }">
            <div class="text-caption text-label">Reclamações Críticas Evitadas</div>
            <div class="text-h6 text-weight-bolder text-negative q-my-xs row items-center">
              <span>{{ sim ? '-' + sim.deltas.detractors_avoided.toLocaleString('pt-BR') : '0' }}</span>
              <q-icon name="mood" size="20px" color="positive" class="q-ml-xs" />
            </div>
            <div class="text-caption text-hint">
              Clientes que deixam de dar nota 1 ou 2
            </div>
          </div>
        </div>

        <!-- Card 4: Novos Pedidos -->
        <div class="col-12 col-sm-6 col-md-3">
          <div class="result-tile" :class="{ 'result-tile--dark': $q.dark.isActive }">
            <div class="text-caption text-label">Novos Pedidos em N/NE</div>
            <div class="text-h6 text-weight-bolder text-indigo q-my-xs">
              {{ sim ? '+ ' + sim.deltas.new_orders.toLocaleString('pt-BR') : '+ 0' }}
            </div>
            <div class="text-caption text-hint">
              Novo Ticket: {{ sim ? formatBrl(sim.projected.ticket) : 'R$ 0' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Barra de Ação Executiva com IA -->
      <div
        class="row items-center justify-between q-mt-md q-pa-sm sim-action-bar"
        :class="{ 'sim-action-bar--dark': $q.dark.isActive }"
      >
        <div class="row items-center q-gutter-x-sm text-caption text-weight-medium">
          <q-icon name="psychology" size="20px" color="primary" />
          <span>Deseja um parecer executivo sobre o Retorno sobre Investimento (ROI) desta simulação?</span>
        </div>

        <q-btn
          dense
          no-caps
          unelevated
          rounded
          color="primary"
          icon="auto_awesome"
          label="Pedir Parecer da IA sobre este Cenário"
          class="q-px-md"
          @click="askAiAboutScenario"
        />
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { api } from '../api'
import type { SimulationResult } from '../types'

const $q = useQuasar()

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
.simulator-card {
  border-radius: 14px;
  border: 1px solid #E2E8F0;
  background: #FFFFFF;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.3s ease;
}

.simulator-card--dark {
  background: #1E1E2F;
  border-color: #2D2D44;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.35);
}

.sim-icon-bubble {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #3B82F6, #1D4ED8);
  display: flex;
  align-items: center;
  justify-content: center;
}

.text-sub {
  color: #64748B;
}

.text-hint {
  font-size: 0.75rem;
  color: #94A3B8;
}

.slider-box {
  background: #F8FAFC;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid #E2E8F0;
}

.slider-box--dark {
  background: #252538;
  border-color: #2D2D44;
}

.result-tile {
  background: #F1F5F9;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid #E2E8F0;
}

.result-tile--dark {
  background: #232336;
  border-color: #2D2D44;
}

.text-label {
  font-size: 0.76rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: #64748B;
}

.sim-action-bar {
  background: #F8FAFC;
  border-radius: 10px;
  border: 1px dashed #CBD5E1;
}

.sim-action-bar--dark {
  background: #252538;
  border-color: #3E3E5B;
}
</style>

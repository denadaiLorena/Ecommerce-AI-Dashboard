<template>
  <q-card flat class="carbon-kpi-tile">
    <!-- Indicador semântico superior discreto estilo Carbon -->
    <div class="carbon-kpi-indicator" :class="indicatorClass"></div>

    <q-card-section class="q-pa-md">
      <div class="row items-center justify-between no-wrap q-mb-xs">
        <span class="carbon-kpi-label ellipsis">{{ title }}</span>
        <q-icon :name="icon" size="18px" :class="iconClass" />
      </div>

      <div class="carbon-kpi-value q-my-xs">{{ value }}</div>

      <div v-if="subtitle" class="carbon-kpi-sub ellipsis">
        {{ subtitle }}
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    title: string
    value: string | number
    subtitle?: string
    icon?: string
    color?: string
  }>(),
  {
    subtitle: '',
    icon: 'insights',
    color: 'primary'
  }
)

const indicatorClass = computed(() => {
  switch (props.color) {
    case 'positive':
      return 'indicator--success'
    case 'negative':
      return 'indicator--danger'
    case 'warning':
    case 'amber-8':
      return 'indicator--warning'
    default:
      return 'indicator--primary'
  }
})

const iconClass = computed(() => {
  switch (props.color) {
    case 'positive':
      return 'icon--success'
    case 'negative':
      return 'icon--danger'
    case 'warning':
    case 'amber-8':
      return 'icon--warning'
    default:
      return 'icon--neutral'
  }
})
</script>

<style scoped>
.carbon-kpi-tile {
  position: relative;
  background-color: var(--color-layer-01);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-none);
  transition: border-color 0.15s ease, background-color 0.15s ease;
  min-height: 112px;
}

.carbon-kpi-tile:hover {
  border-color: var(--color-border-strong);
}

.carbon-kpi-indicator {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
}

.indicator--primary {
  background-color: var(--color-primary);
}

.indicator--success {
  background-color: var(--color-success);
}

.indicator--danger {
  background-color: var(--color-danger);
}

.indicator--warning {
  background-color: var(--color-warning);
}

.carbon-kpi-label {
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.32px;
  color: var(--color-text-secondary);
}

.carbon-kpi-value {
  font-size: 1.75rem;
  font-weight: 400;
  line-height: 1.25;
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
}

.carbon-kpi-sub {
  font-size: 0.75rem;
  color: var(--color-text-helper);
  line-height: 1.3;
}

.icon--neutral {
  color: var(--color-text-secondary);
}

.icon--success {
  color: var(--color-success);
}

.icon--danger {
  color: var(--color-danger);
}

.icon--warning {
  color: var(--color-warning-text);
}
</style>

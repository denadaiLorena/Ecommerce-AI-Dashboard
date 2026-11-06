<template>
  <q-card flat class="kpi-card" :class="{ 'kpi-card--dark': $q.dark.isActive }">
    <div class="kpi-accent" :style="{ background: gradientMap[color] || gradientMap.primary }"></div>
    <q-card-section class="row items-center no-wrap q-py-md">
      <div class="kpi-icon-wrap" :style="{ background: bgMap[color] || bgMap.primary }">
        <q-icon :name="icon" size="24px" color="white" />
      </div>
      <div class="q-ml-md col">
        <div class="kpi-label">{{ title }}</div>
        <div class="kpi-value">{{ value }}</div>
        <div v-if="subtitle" class="kpi-sub">{{ subtitle }}</div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
withDefaults(
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

const gradientMap: Record<string, string> = {
  positive: 'linear-gradient(180deg, #43A047, #66BB6A)',
  primary: 'linear-gradient(180deg, #1976D2, #42A5F5)',
  negative: 'linear-gradient(180deg, #E53935, #EF5350)',
  'amber-8': 'linear-gradient(180deg, #FF8F00, #FFB300)',
}

const bgMap: Record<string, string> = {
  positive: 'linear-gradient(135deg, #43A047, #66BB6A)',
  primary: 'linear-gradient(135deg, #1976D2, #42A5F5)',
  negative: 'linear-gradient(135deg, #E53935, #EF5350)',
  'amber-8': 'linear-gradient(135deg, #FF8F00, #FFB300)',
}
</script>

<style scoped>
.kpi-card {
  position: relative;
  overflow: hidden;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  background: white;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}
.kpi-card--dark {
  background: #1e1e2f;
  border-color: #2d2d44;
}
.kpi-card--dark:hover {
  box-shadow: 0 8px 25px rgba(0,0,0,0.4);
}
.kpi-accent {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
}
.kpi-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.kpi-label {
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  opacity: 0.6;
  margin-bottom: 2px;
}
.kpi-value {
  font-size: 1.4rem;
  font-weight: 800;
  line-height: 1.2;
}
.kpi-sub {
  font-size: 0.78rem;
  opacity: 0.5;
  margin-top: 2px;
}
</style>

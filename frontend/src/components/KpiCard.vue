<template>
  <q-card flat bordered class="kpi-card">
    <q-card-section class="row items-center no-wrap">
      <q-avatar :color="color" text-color="white" :icon="icon" size="52px" />
      <div class="q-ml-md">
        <div class="text-caption text-grey-7">{{ title }}</div>
        <div class="text-h5 text-weight-bold">{{ value }}</div>
        <div v-if="subtitle" class="text-caption text-grey-6">{{ subtitle }}</div>
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
</script>
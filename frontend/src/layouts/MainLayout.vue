<template>
  <q-layout view="hHh lpr lFf">
    <q-header class="carbon-header">
      <q-toolbar class="carbon-toolbar">
        <!-- Logo / Marca Estilo Carbon Shell -->
        <div class="row items-center no-wrap carbon-brand">
          <q-icon name="analytics" size="20px" class="q-mr-sm text-primary-token" />
          <span class="carbon-title-prefix">Ecommerce</span>
          <span class="carbon-title-suffix">AI Metric Pulse</span>
        </div>

        <q-space />

        <!-- Toggle Modo Claro / Escuro -->
        <q-btn
          flat
          dense
          square
          :icon="$q.dark.isActive ? 'light_mode' : 'dark_mode'"
          class="carbon-header-action"
          @click="$q.dark.toggle()"
        >
          <q-tooltip>{{ $q.dark.isActive ? 'Alternar para Modo Claro' : 'Alternar para Modo Escuro' }}</q-tooltip>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
</script>

<style scoped>
.carbon-header {
  background-color: var(--color-header-bg);
  border-bottom: 1px solid var(--color-header-border);
  color: var(--color-header-text);
  box-shadow: none;
}

.carbon-toolbar {
  min-height: 48px;
  height: 48px;
  max-width: 1584px;
  margin: 0 auto;
  width: 100%;
  padding: 0 var(--spacing-06);
}

@media (min-width: 1200px) {
  .carbon-toolbar {
    padding: 0 var(--spacing-07);
  }
}

.carbon-brand {
  letter-spacing: 0.2px;
  font-size: 0.875rem;
}

.carbon-title-prefix {
  font-weight: 400;
  color: var(--color-header-text);
  margin-right: 4px;
}

.carbon-title-suffix {
  font-weight: 600;
  color: var(--color-header-text);
}

.text-primary-token {
  color: var(--color-primary);
}

.carbon-header-action {
  width: 48px;
  height: 48px;
  color: var(--color-header-text);
  border-radius: var(--radius-none);
  transition: background-color 0.15s ease;
}

.carbon-header-action:hover {
  background-color: var(--color-layer-02);
}
</style>

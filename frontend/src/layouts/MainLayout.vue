<template>
  <q-layout view="hHh lpr lFf">
    <q-header class="main-header" :class="{ 'dark-header': $q.dark.isActive }">
      <q-toolbar class="q-px-md" style="min-height: 56px">
        <q-toolbar-title class="text-weight-bold" style="font-size: 1.2rem; letter-spacing: 0.5px">
          AI Metric Pulse
        </q-toolbar-title>

        <q-space />

        <q-btn
          flat
          round
          dense
          :icon="$q.dark.isActive ? 'light_mode' : 'dark_mode'"
          color="white"
          @click="$q.dark.toggle()"
        >
          <q-tooltip>{{ $q.dark.isActive ? 'Modo claro' : 'Modo escuro' }}</q-tooltip>
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
.main-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.dark-header {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}
</style>

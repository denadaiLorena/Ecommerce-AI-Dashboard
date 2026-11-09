<template>
  <q-page class="flex flex-center carbon-second-page">
    <q-btn
      color="primary"
      square
      unelevated
      to="/"
      label="Ir para Visão Geral"
      no-caps
      class="carbon-btn"
    />
  </q-page>
</template>

<script setup lang="ts">
</script>

<style scoped>
.carbon-second-page {
  background-color: var(--color-bg);
  font-family: var(--font-sans);
}

.carbon-btn {
  border-radius: var(--radius-none);
  font-weight: 500;
}
</style>

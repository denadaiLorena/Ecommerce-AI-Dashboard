<template>
  <div class="fullscreen carbon-not-found text-center q-pa-md flex flex-center">
    <div>
      <div class="carbon-404-number">404</div>

      <div class="carbon-404-msg">Página não encontrada</div>

      <q-btn
        class="q-mt-xl carbon-btn-home"
        color="primary"
        square
        unelevated
        to="/"
        label="Voltar para a Visão Geral"
        no-caps
      />
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.carbon-not-found {
  background-color: var(--color-bg);
  color: var(--color-text-primary);
  font-family: var(--font-sans);
}

.carbon-404-number {
  font-size: 20vh;
  font-weight: 300;
  line-height: 1;
  color: var(--color-text-secondary);
  opacity: 0.5;
  letter-spacing: -0.04em;
}

.carbon-404-msg {
  font-size: 1.5rem;
  font-weight: 400;
  color: var(--color-text-secondary);
  margin-top: var(--spacing-04);
}

.carbon-btn-home {
  border-radius: var(--radius-none);
  font-weight: 500;
}
</style>

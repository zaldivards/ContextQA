<template>
  <div id="container" class="text-white-alpha-80">
    <aside id="sidebar">
      <slot name="menu"></slot>
    </aside>
    <section id="main">
      <slot name="main"></slot>
    </section>
  </div>
</template>

<script>
export default {
  name: "MainLayout",
};
</script>

<style scoped>
#container {
  display: grid;
  grid-template-columns: 250px 1fr;
  grid-template-rows: 100vh;
}
#sidebar {
  background-color: #1d2d39;
}
#sidebar > * {
  background-color: #1d2d39 !important;
}
</style>
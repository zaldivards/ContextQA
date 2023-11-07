<template>
  <div id="container">
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
  grid-template-columns: 350px 1fr;
  grid-template-rows: 100vh;
}
</style>
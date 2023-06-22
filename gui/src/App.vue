<template>
  <div>
    <Menubar :model="items" class="m-auto sticky z-4" />
    <router-view />
  </div>
</template>

<script>
import Menubar from "primevue/menubar";
export default {
  name: "App",
  components: {
    Menubar,
  },
  data() {
    return {
      items: [
        {
          label: "Home",
          icon: "pi pi-fw pi-home",
          command: () => this.$router.push({ path: "/chat" }),
        },
        {
          label: "Settings",
          icon: "pi pi-fw pi-cog",
          command: () => this.$router.push({ path: "/context" }),
        },
      ],
    };
  },
};
</script>

<style>
@import url("https://fonts.googleapis.com/css2?family=Poppins:wght@300;400&display=swap");

body {
  font-family: "Poppins", sans-serif;
}
.disabled {
  pointer-events: none;
  outline: none;
}
</style>

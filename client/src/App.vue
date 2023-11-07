<template>
  <div>
    <MainLayout>
      <template #menu>
        <Menu
          :model="items"
          class="m-4 sticky z-4 border-none"
          :pt="{ label: { class: 'text-gl' }, icon: { class: 'text-gl' } }"
        >
          <template #start>
            <img
              alt="logo"
              src="/images/title.png"
              height="30"
              class="px-3"
              title="ContextQA"
            />
          </template>
        </Menu>
      </template>
      <template #main>
        <router-view />
      </template>
    </MainLayout>
  </div>
</template>

<script>
import MainLayout from "@/components/MainLayout.vue";
import Menu from "primevue/menu";
export default {
  name: "App",
  components: {
    Menu,
    MainLayout,
  },
  data() {
    return {
      items: [
        {
          label: "Home",
          icon: "pi pi-fw pi-home",
          command: () => this.$router.push({ path: "/" }),
        },
        {
          label: "Chat",
          icon: "pi pi-comments",
          command: () => this.$router.push({ path: "/chat/talk" }),
        },
        {
          label: "QA",
          icon: "pi pi-file-o",
          command: () => this.$router.push({ path: "/chat/document" }),
        },
        {
          label: "Settings",
          icon: "pi pi-fw pi-cog",
          command: () => this.$router.push({ path: "/context" }),
        },
      ],
    };
  },
  computed: {
    context() {
      return this.$store.state.identifier ?? "None";
    },
    store() {
      const store = this.$store.state.vectorStore;
      return store.charAt(0).toUpperCase() + store.slice(1);
    },
  },
};
</script>

<style>
@import url("https://fonts.googleapis.com/css2?family=Poppins:wght@300;400&display=swap");

body {
  font-family: "Poppins", sans-serif;
  margin: 0;
}
.disabled {
  pointer-events: none;
  outline: none;
}
.top-img {
  top: 4px;
}
</style>

<template>
  <div>
    <Menubar :model="items" class="m-auto sticky z-4">
      <template #start>
        <img
          alt="logo"
          src="/images/title.png"
          height="30"
          class="mr-2"
          title="ContextQA"
        />
      </template>
      <template #end>
        <div>
          <span class="text-xl">Context: </span
          ><span class="font-semibold text-xl">{{ context }}</span>
          <span class="text-xl ml-2" v-if="store"
            ><span class="text-400">|</span> Vector store: </span
          ><span class="font-semibold text-xl">{{ store }}</span>
        </div>
      </template>
    </Menubar>
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
          command: () => this.$router.push({ path: "/" }),
        },
        {
          label: "Chat",
          icon: "pi pi-comment",
          items: [
            {
              label: "Talk",
              icon: "pi pi-comments",
              command: () => this.$router.push({ path: "/chat/talk" }),
            },
            {
              label: "Query document",
              icon: "pi pi-file-o",
              command: () => this.$router.push({ path: "/chat/document" }),
            },
          ],
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
}
.disabled {
  pointer-events: none;
  outline: none;
}
.top-img {
  top: 3px;
}
</style>

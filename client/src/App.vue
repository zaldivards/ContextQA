<template>
  <div>
    <MainLayout>
      <template #menu>
        <Menu
          :model="items"
          class="my-4 sticky z-4 border-none w-full bg-inherit"
          :pt="{
            label: { class: 'text-gl text-white-alpha-80 shadow-6' },
            submenuHeader: { class: 'text-gl text-white-alpha-80 bg-inherit' },
            icon: { class: 'text-gl text-white-alpha-80 shadow-6' },
            separator: { class: 'border-black-alpha-10' },
            action: ({ props, state, context }) => ({
              class: context.focused ? 'bg-menu-focus' : undefined,
            }),
          }"
        >
          <template #start>
            <div class="w-full">
              <img
                alt="logo"
                src="/images/title.png"
                height="30"
                class="m-auto mb-3 block"
                title="ContextQA"
              />
            </div>
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
        { separator: true },
        {
          label: "Home",
          icon: "pi pi-fw pi-home",
          command: () => this.$router.push({ path: "/" }),
        },
        {
          label: "Assistants",
          items: [
            {
              label: "Chat",
              icon: "pi pi-fw pi-comments",
              command: () => this.$router.push({ path: "/chat/talk" }),
            },
            {
              label: "QA",
              icon: "pi pi-fw pi-file-o",
              command: () => this.$router.push({ path: "/chat/document" }),
            },
          ],
        },
        {
          label: "Sources",
          items: [
            {
              label: "Ingestion",
              icon: "pi pi-fw pi-upload",
              command: () => this.$router.push({ path: "/context" }),
            },
            {
              label: "Manage",
              icon: "pi pi-fw pi-th-large",
            },
          ],
        },
        {
          label: "Settings",
          items: [
            {
              label: "Models",
              icon: "pi pi-fw pi-box",
            },
            {
              label: "Status",
              icon: "pi pi-fw pi-info-circle",
            },
            {
              label: "Other configurations",
              icon: "pi pi-fw pi-cog",
            },
          ],
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
  background-color: #0e1b30;
}
.disabled {
  pointer-events: none;
  outline: none;
}
.top-img {
  top: 4px;
}

.bg-menu-focus {
  background-color: #183462 !important;
}

.bg-inherit {
  background-color: inherit !important;
}

.p-menuitem:hover * {
  background-color: #183462 !important;
}

.input-bg input,
.input-bg span,
.input-bg p-inputtext,
.input-bg .p-fileupload-content,
.input-bg .p-dropdown-trigger {
  background-color: #394d6d !important;
  color: rgba(255, 255, 255, 0.8) !important;
}

.bg-contextqa-primary {
  background-color: #0e1624 !important;
}
.bg-contextqa-primary-main {
  background-color: #0e1b30 !important;
}
</style>

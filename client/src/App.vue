<template>
  <div>
    <MainLayout>
      <template #menu>
        <Menu :model="items" class="my-4 sticky z-4 border-none w-full bg-inherit" :pt="{
          label: { class: 'text-gl text-white-alpha-80 shadow-6' },
          submenuHeader: { class: 'text-gl bg-inherit text-teal-300' },
          icon: { class: 'text-gl text-white-alpha-80 shadow-6' },
          separator: { class: 'border-black-alpha-10' },
          action: ({ props, state, context }) => ({
            class: context.focused ? 'bg-menu-focus' : undefined,
          }),
        }">
          <template #start>
            <div class="w-full">
              <img alt="logo" src="/images/title.png" height="30" class="m-auto mb-3 block" title="ContextQA" />
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
          label: "Status",
          icon: "pi pi-fw pi-info-circle",
        },
        {
          label: "Assistants",
          items: [
            {
              label: "Chat",
              icon: "pi pi-fw pi-comments",
              command: () => this.$router.push({ path: "/chat/conversational" }),
            },
            {
              label: "QA",
              icon: "pi pi-fw pi-file-o",
              command: () => this.$router.push({ path: "/chat/qa" }),
            },
          ],
        },
        {
          label: "Sources",
          items: [
            {
              label: "Ingestion",
              icon: "pi pi-fw pi-upload",
              command: () => this.$router.push({ path: "/sources/ingestion" }),
            },
            {
              label: "Manage",
              icon: "pi pi-fw pi-th-large",
              command: () => this.$router.push({ path: "/sources/" }),
            },
          ],
        },
        {
          label: "Settings",
          items: [
            {
              label: "Models",
              icon: "pi pi-fw pi-box",
              command: () => this.$router.push({ path: "/settings/models" }),
            },
            {
              label: "Vector stores",
              icon: "pi pi-fw pi-database",
              command: () => this.$router.push({ path: "/settings/vector-stores" }),
            },
            {
              label: "Extra settings",
              icon: "pi pi-fw pi-cog",
              command: () => this.$router.push({ path: "/settings/extra" }),

            },
          ],
        }
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

@media (max-width: 767px) {

  .p-datatable-wrapper {
    width: 100%;
    overflow: scroll !important;
  }

  .dt-responsive-table {
    width: 100% !important;
  }

  /* Styles for the table header */
  .dt-responsive-table table thead {
    display: none !important;
    /* Hide the table header on mobile */
  }

  /* Styles for the table rows */
  .dt-responsive-table table tbody {
    display: flex !important;
    flex-direction: column !important;
    align-items: stretch !important;
    margin: 0 !important;
    padding: 0 !important;
    min-height: auto !important;
    /* Adjust the min-height as needed */
  }

  /* Styles for individual table rows (cards) */
  .dt-responsive-table table tbody tr {
    border: 1px solid #ccc !important;
    margin-bottom: 1rem !important;
    background-color: #fff !important;
    padding: 1rem !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
  }

  /* Styles for table cells within rows */
  .dt-responsive-table table tbody td {
    margin: 0.5rem 0 !important;
    /* overflow: hidden; */
  }

  /* Hide individual table rows (cards) on mobile */
  .dt-responsive-table table tbody tr {
    display: table-row !important;
  }

  /* Set the display of table cells to be block-level elements */
  .dt-responsive-table table tbody td {
    display: block !important;
    margin: 0.5rem 0 !important;
  }
}
</style>

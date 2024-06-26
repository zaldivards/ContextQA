<template>
  <div :class="!initialized && 'relative h-screen'" class="text-white">
    <div class="fixed bg-black-alpha-40" :style="{ zIndex: -10, inset: 0 }" v-show="!initialized" />
    <div v-if="!initialized">
      <div class="flex flex-column justify-content-between align-items-center h-screen overflow-hidden text-white"
        :class="expanded ? 'fadeoutup animation-duration-1000 animation-ease-out' : ''" v-if="!expandedEnd">
        <div />
        <Card class="text-xl text-white-alpha-80 bg-inherit flex flex-column justify-content-center shadow-none" :pt="{
          header: {
            class: 'text-center',
          }
        }">
          <template #header>
            <img alt="contextqa logo" src="/images/logo.png" class="w-5rem" />
          </template>
          <template #content>
            <p class="w-full lg:w-8 m-auto p-3 lg:p-2">
              Hi there, welcome to
              <span class="relative"><img alt="contextqa text" src="/images/title.png"
                  class="w-6rem relative top-img" /></span>,
            </p>
            <p class="w-full lg:w-8 m-auto p-3 lg:p-2">
              Before we get started, we'd like to ensure that ContextQA functions seamlessly for you. To do so, we
              kindly ask you to set up a few essential details:
            </p>
            <div class="w-full lg:w-8 m-auto p-3 lg:p-2">
              <p>
                <span class="font-bold text-teal-400">LLMs Configuration: </span> Adjust settings related to Large
                Language Models
                (LLMs) to tailor
                their usage
                according to your preferences.
              </p>
              <p>
                <span class="font-bold text-teal-400">Vector Stores Settings: </span>Configure preferences for Vector
                Stores to
                optimize performance and
                enhance your
                experience with ContextQA.
              </p>
              <p>
                <span class="font-bold text-teal-400">Other Settings: </span>Review and adjust any additional settings
                necessary for
                ContextQA to align
                perfectly
                with your needs.
              </p>
            </div>
            <p class="w-full lg:w-8 m-auto p-3 lg:p-2">
              Your cooperation in this matter is greatly appreciated. Let's make your experience with ContextQA
              exceptional from the very start!
            </p>
            <p class="w-full lg:w-8 m-auto p-3 lg:p-2">Let's get started!</p>
          </template>
        </Card>
        <Button icon="pi pi-angle-double-down" text aria-label="expand" @click="onExpanded" size="large"
          class="bg-inherit"
          :icon-class="!expanded && 'fadeinup animation-ease-out animation-duration-1000 animation-iteration-infinite'" />
      </div>
      <StepperView v-else class="fadeindown animation-duration-1000 animation-ease-out" @finish="onFinish" />
    </div>
    <MainLayout v-else>
      <template #menu>
        <Menu :model="items"
          class="mt-2 sticky z-4 border-none w-full bg-inherit h-full flex flex-column justify-content-between" :pt="{
            label: { class: 'text-gl text-white-alpha-80 shadow-6' },
            submenuHeader: { class: 'text-gl bg-inherit text-teal-300' },
            icon: { class: 'text-gl text-white-alpha-80 shadow-6' },
            separator: { class: 'border-black-alpha-10' },
            menu: { class: 'flex-grow-1' },
            end: { class: 'text-red-200' },
            action: ({ context }) => {
              if (context.focused) {
                prevSelectedItem = context.item.label
              }
              return {
                class: context.focused || context.item.label == prevSelectedItem ? 'bg-menu-focus' : undefined,
              }
            },
          }">
          <template #start>
            <div class="w-full">
              <img alt="logo" src="/images/title.png" height="30" class="m-auto mb-3 block" title="ContextQA" />
            </div>
          </template>
          <template #end>
            <div class="flex gap-2 p-2">
              <img src="/images/bug.svg" alt="bug logo" width="25" height="25">
              <a href="https://github.com/zaldivards/ContextQA/issues/new" class="no-underline bug-link"
                target="_blank">Report a bug | Request a new feature</a>
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
import StepperView from "@/views/Stepper"
import Button from 'primevue/button';
import Card from "primevue/card";
import {
  fetchResource
} from "@/utils/client";

export default {
  name: "App",
  components: {
    Menu,
    MainLayout,
    StepperView,
    Button,
    Card
  },
  mounted() {
    this.initialized = localStorage.getItem('isInitialized')
    if (this.initialized === null) {
      this.$router.push('/')
      fetchResource("/settings/init-status").then(status => {
        if (status == 'ok') {
          this.initialized = true
          localStorage.setItem('isInitialized', true);
        } else this.initialized = false
      })
        .catch((error) => { });
    }
  },
  data() {
    return {
      expanded: false,
      expandedEnd: false,
      initialized: false,
      prevSelectedItem: '',
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
          command: () => this.$router.push({ path: "/status" }),
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
  methods: {
    onExpanded() {
      this.expanded = true;
      setTimeout(() => this.expandedEnd = true, 800)
    },
    onFinish() {
      localStorage.setItem('isInitialized', true);
      setTimeout(() => this.initialized = true, 3000)
    }
  },
  computed: {
    context() {
      return this.$store.state.identifier ?? "None";
    },
    store() {
      const store = this.$store.state.vectorStore;
      return store.charAt(0).toUpperCase() + store.slice(1);
    },
  }
};
</script>

<style>
.bug-link:visited {
  color: inherit;
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

  .dt-responsive-table table thead {
    display: none !important;
  }

  .dt-responsive-table table tbody {
    display: flex;
    flex-direction: column;
    margin: 0 !important;
    min-height: auto !important;
  }

  .dt-responsive-table table tbody tr {
    border-bottom: 1px solid #1f1b42 !important;
    margin-bottom: 0.5rem !important;
    padding: 1rem !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
  }

  .dt-responsive-table table tbody tr {
    display: table-row !important;
  }

  .dt-responsive-table table tbody td {
    display: block !important;
    padding: 5px 5px 5px 5px;
    white-space: nowrap !important;
    width: 400px !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
  }
}
</style>

<template>
  <div id="container" class="text-white-alpha-80" :class="customClass">
    <aside id="sidebar" ref="sidebar" v-if="show">
      <slot name="menu"></slot>
    </aside>
    <Button
      type="button"
      icon="pi pi-ellipsis-v"
      @click="toggle"
      aria-haspopup="true"
      aria-controls="overlay_menu"
      id="menu-button"
      class="hidden"
    />

    <section id="main">
      <slot name="main"></slot>
    </section>
  </div>
</template>

<script>
import Button from "primevue/button";
export default {
  name: "MainLayout",
  components: { Button },
  data() {
    return {
      customClass: "marker",
      originalWindowWidth: 1000,
    };
  },
  mounted() {
    // Define the media query condition
    const mediaQuery = window.matchMedia("(min-width: 700px)");

    // Attach an event listener to the window's resize event
    window.addEventListener("resize", (evt) => {
      this.handleResize(mediaQuery);
    });
  },
  methods: {
    toggle() {
      if (!this.customClass || this.customClass == "hidden-grid") {
        this.customClass = "normal-grid";
      } else {
        this.customClass = "hidden-grid";
      }
    },
    handleResize(mediaQuery) {
      if (mediaQuery.matches) {
        const currentWindowWidth = window.innerWidth;
        if (this.originalWindowWidth < currentWindowWidth) {
          this.customClass = "marker";
        } else this.customClass = "";
      }
    },
  },
  computed: {
    show() {
      return (
        this.customClass === "normal-grid" || this.customClass === "marker"
      );
    },
  },
};
</script>

<style scoped>
#container {
  display: grid;
  height: 100vh;
  grid-template-columns: 20% 5% 1fr;
  grid-template-areas: "sidebar main main";
}
#sidebar {
  background-color: #1d2d39;
  grid-area: sidebar;
}
#menu-button {
  grid-row: button;
}
#main {
  grid-area: main;
}
#sidebar > * {
  background-color: #1d2d39 !important;
}

.negative-padding {
  left: -200px !important;
}

.normal {
  left: 0px !important;
}

.normal-grid {
  height: auto !important;
  grid-template-columns: 1fr !important;
  grid-template-areas: "sidebar" "button" "main" !important;
}

.hidden-grid {
  height: auto !important;
  grid-template-columns: 1fr !important;
  grid-template-areas: "button" "main" !important;
}

@media screen and (max-width: 1000px) {
  #container {
    height: auto;
    grid-template-columns: 1fr;
    grid-template-areas: "button" "main";
  }

  #menu-button {
    display: block !important;
    height: 40px;
    width: 100%;
  }
}
@media screen and (min-width: 1000px) {
  #container {
    height: 100vh !important;

    grid-template-columns: 20% 5% 1fr !important;
    grid-template-areas: "sidebar main main" !important;
  }
}
</style>

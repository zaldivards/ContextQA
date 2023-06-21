<template>
  <div class="formgrid grid mx-7">
    <div class="field col" v-if="!isUser"></div>
    <div class="field col">
      <ProgressBar
        mode="indeterminate"
        style="height: 1px"
        v-if="activate"
      ></ProgressBar>
      <div class="formgrid grid" :class="isUser ? 'w-max' : ''" v-else>
        <Avatar
          icon="pi pi-user"
          class="user-card"
          style="background-color: #2196f3; color: #ffffff"
          :class="isUser ? 'mr-3' : 'ml-3'"
          size="large"
          shape="circle"
          v-if="isUser"
        />

        <Card
          class="field col shadow-none animation-duration-300"
          :class="
            isUser
              ? ['bg-teal-500', 'fadeinleft', 'text-white']
              : ['bg-bluegray-100', 'fadeinright']
          "
        >
          <template #content>
            {{ contentStored }}
          </template>
          <template #footer>
            <div
              class="date w-max justify-content-end text-xs"
              :class="isUser ? 'text-white-alpha-70' : 'text-gray-700'"
            >
              {{ dateStr }}
            </div>
          </template>
        </Card>

        <Avatar
          icon="pi pi-prime"
          :class="!isUser ? 'ml-3' : 'mr-3'"
          size="large"
          shape="circle"
          v-if="!isUser"
        />
      </div>
    </div>
    <div class="field col" v-if="isUser"></div>
  </div>
</template>

<script>
import Card from "primevue/card";
import Avatar from "primevue/avatar";
import ProgressBar from "primevue/progressbar";

export default {
  name: "ChatCard",
  props: { role: String, content: String, idx: Number },
  components: { Card, Avatar, ProgressBar },
  data() {
    return {
      lastMessageLocal: "",
    };
  },
  methods: {
    setAlternativeContent() {
      if (!this.lastMessageLocal) {
        this.lastMessageLocal = this.$store.state.lastMessageText;
      }
    },
  },
  computed: {
    isUser() {
      return this.role == "user";
    },
    dateStr() {
      const now = new Date();
      const [date, time] = now.toISOString().split("T");
      return `${date} ${time.slice(0, -5)}`;
    },
    activate() {
      return (
        this.$store.state.showSpinner &&
        !this.isUser &&
        this.$store.state.messages.length - this.idx <= 2
      );
    },
    contentStored() {
      this.setAlternativeContent();
      return this.isUser ? this.content : this.lastMessageLocal;
    },
  },
};
</script>

<style>
</style>
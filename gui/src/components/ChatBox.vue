<template>
  <div
    class="justify-content-center m-auto"
    :class="identifier || !requiresContext ? '' : ['opacity-50', 'disabled']"
  >
    <Toast class="z-5" />

    <Panel
      ref="panel"
      class="w-9 m-auto my-5 scroll-panel chat-height overflow-y-scroll"
      :header="header"
      :pt="{
        header: {
          class: 'bg-primary',
          style: 'position: sticky !important; top: 0 !important;z-index: 3',
        },
        footer: {
          style:
            'position: sticky !important; bottom: 0 !important;border-top: 1px solid #eee;',
        },
      }"
    >
      <ChatCard
        :key="i"
        v-for="(message, i) in messages"
        :role="message.role"
        :idx="i"
        :content="message.content"
      ></ChatCard>

      <template #footer>
        <MessageAdder @send="pushMessages" ref="adder" />
      </template>
    </Panel>
  </div>
</template>

<script>
import Panel from "primevue/panel";
import Toast from "primevue/toast";
import ChatCard from "@/components/ChatCard.vue";
import MessageAdder from "@/components/MessageAdder.vue";

import { askLLM, showError, showWarning } from "@/utils/client";

export default {
  name: "ChatContainer",
  components: { Panel, ChatCard, MessageAdder, Toast },
  props: { requiresContext: Boolean },
  mounted() {
    if (!this.identifier) {
      showWarning(
        "You need to set the document context in the settings section to initialize a chat"
      );
    }
  },
  created() {
    this.messages = this.$store.state.messages;
    this.$store.dispatch("setLastMessage", { isInit: true, content: null });
    this.autoScroll();
  },
  data() {
    return { messages: [] };
  },
  methods: {
    ask(question) {
      this.$store.dispatch("activateSpinner", true);
      this.addMessage({ content: "", role: "bot" });

      askLLM("/context/query", {
        question: question,
        processor: this.$store.state.vectorStore,
        identifier: this.$store.state.identifier,
      })
        .then((result) => {
          this.$store.dispatch("setLastMessage", {
            isInit: false,
            content: result,
          });
          this.autoScroll();
        })
        .catch((error) => {
          this.$store.dispatch("setLastMessage", {
            content: "I am having issues, my apologies. Try again later.",
            role: "bot",
          });

          showError(error.message);
          this.$store.dispatch("activateSpinner", false);
          this.autoScroll();
        });
    },
    pushMessages(message) {
      this.addMessage({ content: message, role: "user" });
      this.ask(message);
    },
    autoScroll() {
      this.$nextTick(() => {
        setTimeout(() => {
          let container = this.$refs.panel.$el;
          container.scrollTop = container.scrollHeight;
        }, 100);
      });
    },
    addMessage(message) {
      this.messages = [...this.messages, message];
      this.$store.dispatch("setMessage", message);
      this.autoScroll();
    },
  },
  computed: {
    identifier() {
      return this.$store.state.identifier;
    },
    header() {
      return this.requiresContext
        ? `Context: ${this.identifier ?? "None"}`
        : "Chat";
    },
  },
};
</script>

<style scoped>
.chat-height {
  height: auto !important;
  max-height: 45rem !important;
}
</style>
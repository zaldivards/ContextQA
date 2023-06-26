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
        :documentQA="requiresContext"
        :sentDate="message.date"
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

import { askLLM, showError, showWarning, getDateTimeStr } from "@/utils/client";

export default {
  name: "ChatContainer",
  components: { Panel, ChatCard, MessageAdder, Toast },
  props: { requiresContext: Boolean },
  mounted() {
    if (!this.identifier && this.requiresContext) {
      showWarning(
        "You need to set the document context in the settings section to initialize a chat"
      );
    }
  },
  created() {
    const action = this.requiresContext
      ? "setLastDocumentMessage"
      : "setLastChatMessage";
    this.messages = this.requiresContext
      ? this.$store.state.documentMessages
      : this.$store.state.chatMessages;
    this.$store.dispatch(action, { isInit: true, content: null });
    this.autoScroll();
  },
  data() {
    return { messages: [] };
  },
  methods: {
    promise(question) {
      if (this.requiresContext) {
        return askLLM("/context/query", {
          question: question,
          processor: this.$store.state.vectorStore,
          identifier: this.$store.state.identifier,
        });
      }
      return askLLM("/qa", {
        message: question,
      });
    },
    ask(question) {
      let sentDate = "";
      this.$store.dispatch("activateSpinner", true);
      this.addMessage({ content: "", role: "bot", date: sentDate });
      const action = this.requiresContext
        ? "setLastDocumentMessage"
        : "setLastChatMessage";

      this.promise(question)
        .then((result) => {
          sentDate = getDateTimeStr();
          this.$store.dispatch(action, {
            isInit: false,
            content: result,
            date: sentDate,
          });
        })
        .catch((error) => {
          sentDate = getDateTimeStr();
          this.$store.dispatch(action, {
            content: "I am having issues, my apologies. Try again later.",
            role: "bot",
            date: sentDate,
          });

          showError(error.message);
          this.$store.dispatch("activateSpinner", false);
        })
        .finally(() => {
          this.messages.at(-1).date = sentDate;
          this.autoScroll();
          this.$refs.adder.$refs.textarea.$el.focus();
        });
    },
    pushMessages(message) {
      this.addMessage({
        content: message,
        role: "user",
        date: getDateTimeStr(),
      });
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
      const action = this.requiresContext
        ? "setDocumentMessage"
        : "setChatMessage";
      this.messages = [...this.messages, message];
      this.$store.dispatch(action, message);
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
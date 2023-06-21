<template>
  <div class="justify-content-center m-auto">
    <Toast />

    <Panel
      :header="`Chat-${identifier}`"
      class="w-9 max-h-screen m-auto overflow-y-scroll"
    >
      <MessageAdder @send="pushMessages" />
      <ChatCard
        :key="i"
        v-for="(message, i) in messages"
        :role="message.role"
        :idx="i"
        :content="message.content"
      ></ChatCard>
    </Panel>
  </div>
</template>

<script>
import Panel from "primevue/panel";
import ChatCard from "@/components/ChatCard.vue";
import MessageAdder from "@/components/MessageAdder.vue";
import Toast from "primevue/toast";

import { askLLM, showError } from "@/utils/client";

export default {
  name: "ChatContainer",
  components: { Panel, ChatCard, MessageAdder, Toast },
  created() {
    this.messages = this.$store.state.messages;
  },
  data() {
    return { messages: [] };
  },
  methods: {
    ask(question) {
      this.$store.dispatch("activateSpinner", true);
      let botMessage = { content: "", role: "bot" };
      this.$store.dispatch("setMessage", botMessage);
      this.messages = [...this.messages, botMessage];

      askLLM("/api/context/query", {
        question: question,
        processor: "local",
        identifier: this.$store.state.identifier,
      })
        .then((result) => {
          this.$store.dispatch("setLastMessage", result);
        })
        .catch((error) => {
          this.$store.dispatch(
            "setLastMessage",
            "I am having connection issues, my apologies. Try again later."
          );

          showError("The LLM server did not process the message properly");
          this.$store.dispatch("activateSpinner", false);
        });
    },
    pushMessages(message) {
      let userMessage = { content: message, role: "user" };
      this.messages = [...this.messages, userMessage];
      this.$store.dispatch("setMessage", userMessage);
      this.ask(message);
    },
  },
  computed: {
    identifier() {
      return this.$store.state.identifier;
    },
  },
};
</script>

<style>
</style>
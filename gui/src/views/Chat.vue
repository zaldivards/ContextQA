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
  data() {
    return { messages: [] };
  },
  methods: {
    ask(question) {
      askLLM("/api/context/query", {
        question: question,
        processor: "local",
        identifier: this.$store.state.identifier,
      })
        .then((result) => {
          this.messages.push({ content: result, role: "bot" });
        })
        .catch((error) => {
          showError("The LLM server did not process the message properly");
        });
    },
    pushMessages(message) {
      this.messages = [...this.messages, { content: message, role: "user" }];
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
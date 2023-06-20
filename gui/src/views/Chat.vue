<template>
  <div class="justify-content-center m-auto">
    <Panel
      header="Chat-someID"
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
import ChatCard from "../components/ChatCard.vue";
import MessageAdder from "../components/MessageAdder.vue";

export default {
  name: "ChatContainer",
  components: { Panel, ChatCard, MessageAdder },
  data() {
    return { messages: [] };
  },
  methods: {
    async askLLM(question) {
      const response = await fetch(
        "api/query-llm" +
          new URLSearchParams({
            question: question,
            processor: "local",
            identifier: "",
          })
      );
      const data = await response.json();
      return data.response;
    },
    pushMessages(message) {
      this.messages = [...this.messages, { content: message, role: "user" }];
    },
  },
};
</script>

<style>
</style>
<template>
  <div class="justify-content-center m-auto">
    <Panel
      header="Chat-someID"
      class="w-9 max-h-screen m-auto overflow-y-scroll"
    >
      <span class="p-float-label mt-2">
        <InputText class="mt-2 mb-4" id="question" v-model="value" />
        <label for="question">Ask me a question</label>
      </span>
      <ChatCard :role="'user'"></ChatCard>
      <ChatCard :role="'bot'"></ChatCard>
      <ChatCard :role="'user'"></ChatCard>
      <ChatCard :role="'bot'"></ChatCard>
      <ChatCard :role="'user'"></ChatCard>
      <ChatCard :role="'bot'"></ChatCard>
      <ChatCard :role="'user'"></ChatCard>
      <ChatCard :role="'bot'"></ChatCard>
      <ChatCard :role="'user'"></ChatCard>
      <ChatCard :role="'bot'"></ChatCard>
      <ChatCard :role="'user'"></ChatCard>
    </Panel>
  </div>
</template>

<script>
import Panel from "primevue/panel";
import InputText from "primevue/inputtext";
import ChatCard from "../components/ChatCard.vue";

export default {
  name: "ChatContainer",
  components: { Panel, ChatCard, InputText },
};
</script>

<style>
</style>
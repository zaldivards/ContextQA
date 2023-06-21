<template>
  <div class="mt-2">
    <Textarea
      class="mt-1 mb-2 w-5"
      id="question"
      @keyup.enter="sendQuestion"
      v-model="question"
      placeholder="Ask me a question"
    />
  </div>
</template>

<script>
import Textarea from "primevue/textarea";

export default {
  name: "MessageAdder",
  components: { Textarea },
  data() {
    return { question: "" };
  },
  methods: {
    sendQuestion(evt) {
      if (!evt.shiftKey) {
        this.$emit("send", this.question);
        this.question = "";
      }
    },
  },
};
</script>

<style>
</style>
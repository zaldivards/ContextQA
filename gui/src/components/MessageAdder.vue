<template>
  <div class="mt-2">
    <InputText
      class="mt-1 mb-2 w-5"
      id="question"
      @keyup.enter="sendQuestion"
      v-model="question"
      placeholder="Ask me a question"
    />
  </div>
</template>

<script>
import InputText from "primevue/inputtext";

export default {
  name: "MessageAdder",
  components: { InputText },
  data() {
    return { question: "" };
  },
  methods: {
    sendQuestion() {
      this.$emit("send", this.question);
      this.question = "";
    },
  },
};
</script>

<style>
</style>
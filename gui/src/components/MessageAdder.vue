<template>
  <span class="p-float-label mt-2">
    <InputText
      class="mt-2 mb-4"
      id="question"
      @keyup.enter="sendQuestion"
      v-model="question"
    />
    <label for="question">Ask me a question</label>
  </span>
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
<template>
  <div>
    <Textarea
      style="background-color: #394d6d"
      ref="textarea"
      class="mt-1 mb-2 w-full text-white-alpha-80 border-round-2xl"
      :class="disable ? 'disabled' : ''"
      id="question"
      @keydown.enter="sendQuestion"
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
        this.$refs.textarea.$el.blur();
        this.question = "";
      }
    },
  },
  computed: {
    disable() {
      return this.$store.state.showSpinner;
    },
  },
};
</script>

<style>
</style>
<template>
  <div>
    <Textarea
      style="background-color: #394d6d"
      ref="textarea"
      class="lg:mb-0 md:mb-0 mb-3 w-full text-white-alpha-80 border-round-2xl max-h-30rem overflow-scroll"
      :class="disable ? 'disabled' : ''"
      id="question"
      @keydown.enter="sendQuestion"
      v-model="question"
      placeholder="Ask me a question"
      autoResize
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
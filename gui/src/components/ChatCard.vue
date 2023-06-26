<template>
  <div class="formgrid grid mx-7">
    <div class="field col" v-if="!isUser"></div>
    <div class="field col">
      <ProgressBar
        mode="indeterminate"
        style="height: 1px"
        v-if="activate"
      ></ProgressBar>
      <div class="formgrid grid" :class="isUser ? 'max-w-max' : ''" v-else>
        <Avatar
          image="/images/user.png"
          :class="isUser ? 'mr-3' : 'ml-3'"
          size="large"
          shape="circle"
          v-if="isUser"
        />

        <Card
          class="field col shadow-none animation-duration-300 breakline-ok"
          :class="
            isUser
              ? ['bg-teal-600', 'fadeinleft', 'text-white']
              : ['bg-bluegray-500', 'fadeinright', 'text-white']
          "
        >
          <template #content>
            <div v-html="contentStored"></div>
          </template>
          <template #footer>
            <div
              class="date w-max justify-content-end text-xs text-white-alpha-70"
            >
              {{ dateStr }}
            </div>
          </template>
        </Card>

        <Avatar
          image="/images/logo.png"
          :class="!isUser ? 'ml-3' : 'mr-3'"
          size="large"
          v-if="!isUser"
        />
      </div>
    </div>
    <div class="field col" v-if="isUser"></div>
  </div>
</template>

<script>
import Card from "primevue/card";
import Avatar from "primevue/avatar";
import ProgressBar from "primevue/progressbar";

export default {
  name: "ChatCard",
  props: { role: String, content: String, idx: Number, documentQA: Boolean },
  components: { Card, Avatar, ProgressBar },
  data() {
    return {
      lastMessageLocal: "",
    };
  },
  methods: {
    setAlternativeContent() {
      if (!this.lastMessageLocal) {
        const lastMessageState = this.documentQA
          ? this.$store.state.lastDocumentMessageText
          : this.$store.state.lastChatMessageText;
        this.lastMessageLocal = lastMessageState ?? this.content;
      }
    },
    formatCode(message) {
      const formattedText = message
        .replaceAll(/(?<=```)(?!\n{2})[^`]+(?=```)/g, (match, offset, text) => {
          match = match.trim();
          const lines = match.split("\n");
          if (lines.length > 1) {
            match = lines.slice(1).join("\n");
          }
          return `<code class='text-yellow-600 bg-black-alpha-70 p-3 w-auto block'>${match}</code>`;
        })
        .replaceAll("```", "")
        .replaceAll(/(?<=`)(?![\s.])[^`]+(?=`)/g, (match, offset, text) => {
          return `<code class='text-yellow-600 bg-black-alpha-70 p-1 w-min'>${match}</code>`;
        });
      return formattedText.replaceAll("`", "").replaceAll(
        "ContextQA",
        `<span class="relative"
              ><img
                alt="contextqa text"
                src="/images/title.png"
                class="w-2 top-img relative"
            /></span>`
      );
    },
  },
  computed: {
    isUser() {
      return this.role == "user";
    },
    dateStr() {
      const now = new Date();
      now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
      const [date, time] = now.toISOString().split("T");
      return `${date} ${time.slice(0, -5)}`;
    },
    activate() {
      const length = this.documentQA
        ? this.$store.state.documentMessages.length
        : this.$store.state.chatMessages.length;
      return (
        this.$store.state.showSpinner && !this.isUser && length - this.idx <= 2
      );
    },
    contentStored() {
      this.setAlternativeContent();
      if (this.isUser) {
        return this.content;
      }
      return this.formatCode(this.lastMessageLocal);
    },
  },
};
</script>

<style scoped>
.breakline-ok {
  white-space: pre-wrap;
}
</style>
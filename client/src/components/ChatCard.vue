<template>
  <ProgressBar
    mode="indeterminate"
    style="height: 1px"
    v-if="activate"
  ></ProgressBar>
  <div class="formgrid grid" :class="isUser ? 'max-w-max' : ''" v-else>
    <Avatar
      image="/images/user.png"
      size="small"
      shape="circle"
      v-if="isUser"
    />
    <Avatar image="/images/logo.png" size="small" v-if="!isUser" />

    <Card
      class="field col ml-2 shadow-none animation-duration-300 breakline-ok"
      :class="
        isUser
          ? ['bg-inherit', 'fadeinleft', 'text-white-alpha-80']
          : ['bg-contextqa-primary', 'fadeinright', 'text-white-alpha-80']
      "
      :pt="{
        content: { class: 'py-1' },
      }"
    >
      <template #content>
        <div v-html="contentStored"></div>
      </template>
      <template #footer>
        <div class="date w-max justify-content-end text-xs text-white-alpha-70">
          {{ sentDate }}
        </div>
      </template>
    </Card>
  </div>
</template>

<script>
import Card from "primevue/card";
import Avatar from "primevue/avatar";
import ProgressBar from "primevue/progressbar";

export default {
  name: "ChatCard",
  props: {
    role: String,
    content: String,
    sentDate: String,
    idx: Number,
    documentQA: Boolean,
  },
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
        .replaceAll(
          /(?<=```)(?!\n{2}|\s+\-)[^`]+(?:`[^`]+)?(?=```)/g,
          (match, offset, text) => {
            const lines = match.split("\n");
            if (lines.length > 1 && /[\w\s]/.test(lines[0].at(-1))) {
              match = lines.slice(1).join("\n");
            }
            return `<code class='text-yellow-600 bg-black-alpha-70 p-3 w-auto block'>${match.trim()}</code>`;
          }
        )
        .replaceAll("```", "")
        .replaceAll(/(?<=`)(?![\s.,)])[^`]+(?=`)/g, (match, offset, text) => {
          return `<code class='text-yellow-600 bg-black-alpha-70 p-1 w-min'>${match}</code>`;
        })
        .replaceAll(/\[.+\]\([\w:\/.\-]+\)/g, (match, offset, text) => {
          const parts = match.match(/\[(.*?)\]\((.*?)\)/, "$1");
          return `<a href="${parts[2]}">${parts[1]}</a>`;
        });
      return formattedText.replaceAll("`", "").replaceAll(
        "ContextQA",
        `<span class="relative"
              ><img
                alt="contextqa text"
                src="/images/title.png"
                class="w-1 top-img relative"
            /></span>`
      );
    },
  },
  computed: {
    isUser() {
      return this.role == "user";
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
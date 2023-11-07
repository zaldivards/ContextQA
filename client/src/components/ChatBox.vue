<template>
  <div
    class="justify-content-center m-auto"
    :class="identifier || !requiresContext ? '' : ['opacity-50', 'disabled']"
  >
    <div>
      <Dialog
        :dismissableMask="true"
        :closeOnEscape="true"
        :closable="true"
        :visible="showDialog"
        :draggable="false"
        modal
        header="Internet access enabled"
        class="w-6"
      >
        <template #closeicon>
          <button @click="closeDialog" class="no-background">
            <i class="pi pi-times" style="color: red"></i>
          </button>
        </template>
        <p>
          There are two main points you need to take into account when enabling
          internet access:
        </p>
        <ul>
          <li>
            <b>Increased API usage</b>: With internet access, the assistant may
            need to make additional API calls to fetch information from the web.
            This can result in slightly higher API usage compared to when
            internet access is disabled.
          </li>
          <li>
            <b>Accuracy limitations</b>: While internet access can provide the
            assistant with access to a vast amount of information, it's
            important to note that the assistant's responses are still based on
            a mixture of licensed data, data created by human trainers, and
            publicly available data. Therefore, there may be instances where the
            assistant's accuracy is not the best, especially when it comes to
            real-time or highly specific information.
          </li>
        </ul>
      </Dialog>
    </div>
    <Toast class="z-5" />

    <Panel
      ref="panel"
      class="w-9 m-auto my-5 scroll-panel chat-height overflow-y-scroll"
      :header="header"
      :pt="{
        header: {
          class: 'bg-primary',
          style: 'position: sticky !important;   top: 0 !important;z-index: 3',
        },
        footer: {
          style: 'border-top: 1px solid #eee;',
          class: 'grid fixed bottom-0 w-screen',
        },
        content: {
          class: 'border-none',
        },
      }"
    >
      <ChatCard
        :key="i"
        v-for="(message, i) in messages"
        :role="message.role"
        :idx="i"
        :content="message.content"
        :documentQA="requiresContext"
        :sentDate="message.date"
      ></ChatCard>
      <div class="fixed bottom-0 w-full mb-5">
        <div class="col-2 flex align-items-center" v-if="!requiresContext">
          <span class="mr-2">Enable internet access</span>
          <InputSwitch v-model="internetEnabled" @input="switchHandler" />
        </div>
        <MessageAdder @send="pushMessages" ref="adder" />
      </div>
    </Panel>
  </div>
</template>

<script>
import Panel from "primevue/panel";
import InputSwitch from "primevue/inputswitch";
import Dialog from "primevue/dialog";
import Toast from "primevue/toast";
import ChatCard from "@/components/ChatCard.vue";
import MessageAdder from "@/components/MessageAdder.vue";

import { askLLM, showError, showWarning, getDateTimeStr } from "@/utils/client";

export default {
  name: "ChatContainer",
  components: { Panel, ChatCard, MessageAdder, Toast, InputSwitch, Dialog },
  props: { requiresContext: Boolean },
  mounted() {
    if (!this.identifier && this.requiresContext) {
      showWarning(
        "You need to set the document context in the settings section to initialize a chat"
      );
    }
  },
  created() {
    let action = "";
    if (this.requiresContext) {
      action = "setLastDocumentMessage";
      this.messages = this.$store.state.documentMessages;
    } else {
      action = "setLastChatMessage";
      this.messages = this.$store.state.chatMessages;
      this.internetEnabled = this.$store.state.internetEnabled;
    }
    this.$store.dispatch(action, { isInit: true, content: null });
    this.autoScroll();
  },
  data() {
    return { messages: [], internetEnabled: false, showDialog: false };
  },
  methods: {
    promise(question) {
      if (this.requiresContext) {
        return askLLM("/context/query", {
          question: question,
          processor: this.$store.state.vectorStore,
          identifier: this.$store.state.identifier,
        });
      }
      return askLLM("/qa", {
        message: question,
        internet_access: this.internetEnabled,
      });
    },
    ask(question) {
      let sentDate = "";
      this.$store.dispatch("activateSpinner", true);
      this.addMessage({ content: "", role: "bot", date: sentDate });
      const action = this.requiresContext
        ? "setLastDocumentMessage"
        : "setLastChatMessage";

      this.promise(question)
        .then((result) => {
          sentDate = getDateTimeStr();
          this.$store.dispatch(action, {
            isInit: false,
            content: result,
            date: sentDate,
          });
        })
        .catch((error) => {
          sentDate = getDateTimeStr();
          this.$store.dispatch(action, {
            content: "I am having issues, my apologies. Try again later.",
            role: "bot",
            date: sentDate,
          });

          showError(error.message);
          this.$store.dispatch("activateSpinner", false);
        })
        .finally(() => {
          this.messages.at(-1).date = sentDate;
          this.autoScroll();
          this.$refs.adder.$refs.textarea.$el.focus();
        });
    },
    pushMessages(message) {
      this.addMessage({
        content: message,
        role: "user",
        date: getDateTimeStr(),
      });
      this.ask(message);
    },
    autoScroll() {
      this.$nextTick(() => {
        setTimeout(() => {
          let container = this.$refs.panel.$el;
          container.scrollTop = container.scrollHeight;
        }, 100);
      });
    },
    addMessage(message) {
      const action = this.requiresContext
        ? "setDocumentMessage"
        : "setChatMessage";
      this.messages = [...this.messages, message];
      this.$store.dispatch(action, message);
      this.autoScroll();
    },
    switchHandler(value) {
      this.showDialog = value;
      if (!this.requiresContext)
        this.$store.dispatch("setInternetAccess", value);
    },
    closeDialog() {
      this.showDialog = false;
    },
  },
  computed: {
    identifier() {
      return this.$store.state.identifier;
    },
    header() {
      return this.requiresContext
        ? `Context: ${this.identifier ?? "None"}`
        : "ContextQA Chat";
    },
  },
};
</script>

<style scoped>
.chat-height {
  height: auto !important;
  max-height: 45rem !important;
}
.no-background {
  background: none;
  border: none;
}
.no-background:hover {
  cursor: pointer;
}
</style>
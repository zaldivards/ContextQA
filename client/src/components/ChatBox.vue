<template>
  <div
    class="justify-content-center mx-auto"
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
        class="w-full lg:w-6"
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
    <Toast class="z-5 w-9 lg:w-3" />

    <Panel
      ref="panel"
      class="w-12 lg:w-8 m-auto lg:my-5 scroll-panel chat-height overflow-y-scroll scrollbar bg-inherit relative"
      :header="header"
      :pt="{
        header: {
          class: 'border-none bg-contextqa-primary-main sticky top-0',
        },
        footer: {
          style: 'border-top: 1px solid #eee;',
          class: 'grid fixed bottom-0 w-screen',
        },
        content: {
          class: 'border-none bg-inherit',
        },
      }"
    >
      <div :key="i" v-for="(message, i) in messages">
        <ProgressBar
          mode="indeterminate"
          style="height: 1px"
          v-if="activate && message.role == 'bot' && message.isLatest"
        ></ProgressBar>
        <div
          v-else
          class="formgrid grid"
          :class="message.role == 'user' ? 'max-w-max' : ''"
        >
          <Avatar
            image="/images/user.png"
            size="small"
            shape="circle"
            v-if="message.role == 'user'"
          />
          <Avatar
            image="/images/logo.png"
            size="small"
            v-if="message.role != 'user'"
          />

          <Card
            class="field col mx-2 shadow-none animation-duration-300 breakline-ok"
            :class="
              message.role == 'user'
                ? ['bg-inherit', 'fadeinleft', 'text-white-alpha-80']
                : ['bg-contextqa-primary', 'fadeinright', 'text-white-alpha-80']
            "
            :pt="{
              content: { class: 'py-1' },
              body: { class: message.role == 'user' ? 'pt-0' : '' },
            }"
          >
            <template #content>
              <div v-if="message.isLatest" v-html="answer"></div>
              <div v-else v-html="message.content"></div>
            </template>
            <template #footer>
              <div
                class="date w-max justify-content-end text-xs text-white-alpha-70"
              >
                {{ message.date }}
              </div>
            </template>
          </Card>
        </div>
      </div>

      <div class="fixed bottom-0 w-11 lg:w-7 mb-5 align-items-center">
        <div class="m-auto">
          <div class="flex align-items-center mb-2" v-if="!requiresContext">
            <span class="mr-2">Enable internet access</span>
            <InputSwitch v-model="internetEnabled" @input="switchHandler" />
          </div>
          <MessageAdder @send="pushMessages" ref="adder" />
        </div>
      </div>
    </Panel>
  </div>
</template>

<script>
import Panel from "primevue/panel";
import ProgressBar from "primevue/progressbar";
import InputSwitch from "primevue/inputswitch";
import Dialog from "primevue/dialog";
import Toast from "primevue/toast";
import Card from "primevue/card";
import Avatar from "primevue/avatar";
import MessageAdder from "@/components/MessageAdder.vue";

import { askLLM, showError, showWarning, getDateTimeStr } from "@/utils/client";
import { formatCode, clean } from "@/utils/text";

export default {
  name: "ChatContainer",
  components: {
    Panel,
    MessageAdder,
    Toast,
    InputSwitch,
    Dialog,
    Card,
    Avatar,
    ProgressBar,
  },
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
    return {
      messages: [],
      internetEnabled: false,
      showDialog: false,
      lastMessageLocal: "",
      answer: "",
    };
  },
  methods: {
    getGenerator(question) {
      if (this.requiresContext) {
        return askLLM("/qa/", {
          question: question,
        });
      }
      return askLLM("/bot/", {
        message: question,
        internet_access: this.internetEnabled,
      });
    },
    async ask(question) {
      let sentDate = "";
      let activated = false;
      let temp = "";
      let block = "init";
      let single = "init";
      this.$store.dispatch("activateSpinner", true);
      this.addMessage({
        content: "",
        role: "bot",
        date: sentDate,
        isLatest: true,
      });
      const action = this.requiresContext
        ? "setLastDocumentMessage"
        : "setLastChatMessage";
      try {
        for await (const token of this.getGenerator(question)) {
          if (!activated) {
            this.$store.dispatch("activateSpinner", false);
            activated = true;
          }
          if (token.includes("```")) {
            if (block == "init") {
              block = "waiting";
            } else if (block == "waiting") {
              block = "finished";
            }
          } else if (token.includes("`")) {
            if (single == "init") {
              single = "waiting";
            } else if (single == "waiting") {
              single = "finished";
            }
          }

          if (this.internetEnabled) {
            if (token.trim().endsWith('"') || token.trim().endsWith("}")) {
              temp += token.trim().slice(-1);
              this.answer += clean(token.trim().slice(0, -1));
            } else if (token.trim().endsWith('" }')) {
              temp += token.trim().slice(-3);
              this.answer += clean(token.trim().slice(0, -3));
            } else {
              this.answer += clean(token);
            }
            if (temp && temp.length <= 3) {
              temp += token;
            }
            if (temp.length == 3) {
              temp = "";
            }
          } else {
            if (token.includes("<sources>")) {
              const sources = JSON.parse(token.split("<sources>")[1]);
            }
            this.answer += clean(token);
          }

          if (block == "finished" || single == "finished") {
            this.answer = formatCode(this.answer);
            block = single = "init";
          }
          this.autoScroll();
        }

        sentDate = getDateTimeStr();
        this.$store.dispatch(action, {
          isInit: false,
          content: this.answer,
          date: sentDate,
        });
      } catch (error) {
        console.log("Error: " + error);
        sentDate = getDateTimeStr();
        this.$store.dispatch(action, {
          content: "I am having issues, my apologies. Try again later.",
          role: "bot",
          date: sentDate,
        });

        showError(error.message);
        this.$store.dispatch("activateSpinner", false);
      } finally {
        this.messages.at(-1).date = sentDate;
        this.messages.at(-1).isLatest = false;
        this.messages.at(-1).content = this.answer;
        this.answer = "";
        this.$refs.adder.$refs.textarea.$el.focus();
      }
    },
    pushMessages(message) {
      this.addMessage({
        content: message,
        role: "user",
        date: getDateTimeStr(),
      });
      this.ask(message).then(() => {});
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
    activate() {
      const flag = this.$store.state.showSpinner && !this.answer;
      return flag;
    },
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

.scrollbar::-webkit-scrollbar {
  width: 1px;
  background-color: #0e1b30 !important;
}

.scrollbar::-webkit-scrollbar-thumb {
  background-color: #aaa;
}
</style>
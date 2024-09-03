<template>
  <div class="my-4 justify-content-center">
    <div class="lg:px-0 lg:w-10 lg:m-auto md:m-auto grid justify-content-center"
      :class="sourcesReady || !requiresContext ? '' : ['opacity-50', 'disabled']">
      <DynamicDialog :pt="{ content: { class: 'h-full' } }" />
      <div>
        <Dialog :dismissableMask="true" :closeOnEscape="true" :closable="true" :visible="showDialog" :draggable="false"
          modal header="Internet access enabled" class="w-full lg:w-6">
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

      <Panel ref="panel"
        class="col-12 lg:col-8 lg:my-5 scroll-panel chat-height overflow-y-scroll scrollbar bg-inherit py-0"
        :header="header" :pt="{
          header: {
            class: 'border-none bg-contextqa-primary-main sticky top-0 pt-3',
          },
          footer: {
            style: 'border-top: 1px solid #eee;',
            class: 'grid fixed bottom-0 w-screen',
          },
          content: {
            class: 'border-none bg-inherit',
          },
        }">
        <div :key="i" v-for="(message, i) in messages">
          <ProgressBar mode="indeterminate" style="height: 1px"
            v-if="activate && message.role == 'bot' && message.isLatest">
          </ProgressBar>
          <div v-else class="formgrid grid" :class="message.role == 'user' ? 'max-w-max' : ''">
            <Avatar image="/images/user.png" size="small" shape="circle" v-if="message.role == 'user'" />
            <Avatar image="/images/logo.png" size="small" v-if="message.role != 'user'" />

            <Card class="card field col mx-2 shadow-none animation-duration-300 breakline-ok max-w-screen" :class="message.role == 'user'
              ? ['bg-inherit', 'fadeinleft', 'text-white-alpha-80']
              : ['bg-contextqa-primary', 'fadeinright', 'text-white-alpha-80']
              " :pt="{
                content: { class: 'py-0' },
                footer: { class: message.role == 'bot' && 'p-0 m-0' },
                body: { class: message.role == 'user' ? 'pt-0' : '' },
              }">
              <template #content>
                <div v-if="message.isLatest" v-html="answer" />
                <div v-else v-html="prettyFormat(message)" />
              </template>
              <template #footer>
                <div class="text-xs text-white-alpha-70 flex gap-2 align-items-center">
                  {{ message.date }}
                  <CopyButton v-if="message.role != 'user'" :content="message.content" />
                </div>
              </template>
            </Card>
          </div>
        </div>

        <div class="fixed centered w-11 lg:w-5 mb-5 flex justify-content-center" v-if="isEmpty">
          <p class="w-fit bg-gray-500 p-4 border-round-xl">No conversation yet</p>
        </div>

      </Panel>
      <div class="fixed bottom-0 w-full flex justify-content-center" style="background-color: #0e1b30">
        <div class="w-11 lg:w-5 lg:mb-3 md:mb-3 mb-1 pt-1">
          <div class="m-auto flex flex-column gap-0">
            <div class="flex justify-content-start gap-2" v-if="!requiresContext">
              <span class="font-bold text-white-alpha-60">Enable internet access</span>
              <InputSwitch v-model="internetEnabled" @change="switchHandler" class="bg-inherit flex-shrink-0"
                :pt="{ slider: { style: 'height: 23px;' } }" />
            </div>
            <Button v-else label="Sources" class="my-2 w-fit" icon="pi pi-search-plus" severity="secondary" rounded
              @click="showSources" />
            <div class="flex gap-2 my-1 pb-2 overflow-x-scroll" v-if="!requiresContext" title="Common queries">
              <Chip :key="i"
                class="cursor-pointer bg-black-alpha-60 flex-shrink-0 hover:border-gray-600 border-1 border-black-alpha-60"
                v-for="(item, i) in chips" @click="() => chipOverwrite(item)" :label="item.statement" />
            </div>
            <MessageAdder @send="pushMessages" ref="adder" />
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { defineAsyncComponent } from "vue";
import Button from "primevue/button";
import Chip from 'primevue/chip';
import DynamicDialog from "primevue/dynamicdialog";
import Panel from "primevue/panel";
import ProgressBar from "primevue/progressbar";
import InputSwitch from "primevue/inputswitch";
import Dialog from "primevue/dialog";
import Toast from "primevue/toast";
import Card from "primevue/card";
import Avatar from "primevue/avatar";
import MessageAdder from "@/components/MessageAdder.vue";
import CopyButton from "@/components/CopyButton.vue";
import { marked } from "marked"
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'

marked.use({
  pedantic: false,
  gfm: true,
  breaks: true,
});

const renderer = new marked.Renderer();

renderer.code = (code, lang, _) => {
  lang = lang || 'plaintext';
  let finalCode = code
  try {
    finalCode = hljs.highlight(code, { language: lang }).value;
  }
  catch (e) {
    console.log(`${lang} is not supported by highlight.js, rendering as plain text`);
  }
  return `<div class="border-round-top bg-white-alpha-10 text-sm mb-4"><div class="p-2">${lang}</div><code class="hljs ${lang} p-3 block">${finalCode}</code></div>`;
};

marked.use({ renderer });

const SourcesBox = defineAsyncComponent(() =>
  import("@/components/SourcesBox.vue")
);

import {
  askLLM,
  showError,
  showWarning,
  getDateTimeStr,
  fetchResource,
} from "@/utils/client";
import { chipsContent, SERVER_BASE_URL } from "@/utils/constants"
import { formatCode } from "@/utils/text";

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
    Button,
    DynamicDialog,
    Chip,
    CopyButton
  },
  props: { requiresContext: Boolean },
  mounted() {
    if (this.requiresContext) {
      if (!this.sourcesReady) {
        fetchResource("/sources/check-availability/")
          .then((response) => {
            this.$store.dispatch("setSourcesFlag", response.status == "ready");
            if (!this.sourcesReady && this.requiresContext) {
              showWarning(
                "You need to ingest at least one source to initialize a QA session"
              );
            }
          })
          .catch((error) => showError(error));
      }
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
      chips: chipsContent,
      internetEnabled: false,
      showDialog: false,
      lastMessageLocal: "",
      answer: "",
      latestSources: "",
    };
  },
  methods: {
    prettyFormat(message) {
      if (message.role == 'user') return message.content; // ensure to pretty format only the bot responses
      let cleanMessage = message.content.trim().replace(/<sources>/g, '')
      if (!cleanMessage.startsWith('```'))
        // remove leading whitespaces to prevent marked to format certain parts of the response as code blocks
        // code blocks must be surrounded by triple backticks
        cleanMessage = cleanMessage.replace(/ {2,}/, '')
      return formatCode(marked(cleanMessage))
    },
    chipOverwrite(item) {
      this.$refs.adder.question = `${item.statement}${item.template && '\n\n' + item.template}`
      this.$refs.adder.$refs.textarea.$el.focus()
    },
    showSources() {
      const dialogRef = this.$dialog.open(SourcesBox, {
        props: {
          header: "Relevant sources",
          style: {
            width: "50vw",
          },
          pt: {
            title: {
              class: 'lg:text-4xl md:text-4xl text-xl'
            }
          },
          class: ["w-9"],
          modal: true,
          dismissableMask: true,
          draggable: false,
        },
        data: {
          sources: this.latestSources,
        },
      });
    },
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
      let finished = false;
      this.$store.dispatch("activateSpinner", true);
      this.addMessage({
        content: "",
        role: "bot",
        date: sentDate,
        isLatest: true,
      });
      if (this.requiresContext) this.latestSources = "";
      const action = this.requiresContext
        ? "setLastDocumentMessage"
        : "setLastChatMessage";
      try {
        for await (let token of this.getGenerator(question)) {
          if (!activated) {
            this.$store.dispatch("activateSpinner", false);
            activated = true;
          }

          if (this.internetEnabled) {
            token = token.replace("\\n", "\n");
            if (token.trim().endsWith('"') || token.trim().endsWith("}")) {
              temp += token.trim().slice(-1);
              this.answer += token.trim().slice(0, -1);
            } else if (token.trim().endsWith('" }')) {
              temp += token.trim().slice(-3);
              this.answer += token.trim().slice(0, -3);
            } else {
              this.answer += token;
            }
            if (temp && temp.length <= 3) {
              temp += token;
            }
            if (temp.length == 3) {
              temp = "";
            }
          } else {
            if (token.includes("<sources>") && this.requiresContext) {
              finished = true;
              this.latestSources = token.split("<sources>")[1];
              this.$store.dispatch("setLatestSources", this.latestSources);
            }
            if (!finished) this.answer += token
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
        finished = false;
      }
    },
    playAudio() {
      const audio = new Audio(`${SERVER_BASE_URL}/static/notification.mp3`);
      audio.play();
    },
    pushMessages(message) {
      this.addMessage({
        content: message,
        role: "user",
        date: getDateTimeStr(),
      });
      this.ask(message).then(this.playAudio);
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
      this.showDialog = value.target.checked
      if (!this.requiresContext) {
        this.$store.dispatch("setInternetAccess", this.internetEnabled);
      }
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
    sourcesReady() {
      return this.$store.state.sourcesReady;
    },
    header() {
      return this.requiresContext ? "QA Session" : "ContextQA Chat";
    },
    isEmpty() {
      return this.messages.length == 0;
    }
  },
};
</script>

<style>
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

.breakline-ok {
  white-space: pre-wrap;
}

.centered {
  bottom: 45%;
}

.card p,
.card ol,
.card ul {
  margin: 0 !important;
}

.card ul,
.card ol {
  display: flex;
  flex-direction: column;
}
</style>
<template>
  <div class="my-6 justify-content-center">
    <ConfirmDialog></ConfirmDialog>

    <Toast class="z-5" />
    <form @submit.prevent="postData" class="px-3 lg:px-0 w-full lg:w-7 m-auto">
      <h2 class="mb-5">⚙️ Set the context document</h2>

      <div :class="disabled ? ['opacity-50', 'disabled'] : ''" class="grid">
        <FileUpload
          @remove="() => (this.uploadedFile = null)"
          accept=".pdf,.txt"
          fileLimit="1"
          :maxFileSize="100000000"
          @select="handleFileSelect"
          :showUploadButton="false"
          :multiple="false"
          :pt="{
            badge: { class: 'hidden' },
            details: { class: 'ml-6' },
            root: { class: 'col-12' },
          }"
        />
        <div class="col-12 lg:col-6 input-bg">
          <label for="separator">Separator</label>
          <InputText
            class="block my-2"
            v-model="separator"
            type="text"
            placeholder="Text separator, default '.'"
            id="separator"
          />
        </div>

        <div class="col-12 md:col-12 input-bg lg:col-6">
          <label for="chunkSize">Chunk size</label>
          <InputNumber
            class="block my-2 w-max"
            v-model="chunkSize"
            inputId="integeronly"
            placeholder="Chunk size, default 200"
            :min="0"
            :max="1000"
            id="chunkSize"
          />
        </div>

        <div class="col-12 md:col-12 input-bg lg:col-6">
          <label for="overlap">Overlap</label>
          <InputNumber
            class="block outline-none my-2 w-max"
            inputId="integeronly"
            v-model="overlap"
            placeholder="Chunk overlap, default 0"
            id="overlap"
            :min="0"
            :max="200"
          />
        </div>
        <div class="col-12 md:col-12 input-bg lg:col-6">
          <label for="store">Vector store</label>
          <div class="vertical-justify-center">
            <Dropdown
              v-model="selectedStore"
              :options="stores"
              placeholder="Choose a vector store"
              id="store"
            />
          </div>
        </div>
      </div>
      <Button
        type="button"
        label="Submit"
        icon="pi pi-check"
        @click="postData(doPost)"
        :disabled="nullData || disabled"
        :loading="loading"
        class="col-offset-4 lg:col-offset-0 col-4 lg:col-2 mt-5"
      />
    </form>
  </div>
</template>
<script setup>
import { useConfirm } from "primevue/useconfirm";
import { useStore } from "vuex";
const confirm = useConfirm();
const store = useStore();
function postData(postFunction) {
  if (store.state.vectorStore) {
    confirm.require({
      message: "Are you sure you want to replace the context?",
      header: "Confirmation",
      icon: "pi pi-exclamation-triangle",
      accept: () => {
        postFunction();
      },
    });
  } else {
    postFunction();
  }
}
</script>

<script>
import ConfirmDialog from "primevue/confirmdialog";
import FileUpload from "primevue/fileupload";
import InputText from "primevue/inputtext";
import InputNumber from "primevue/inputnumber";
import Button from "primevue/button";
import Toast from "primevue/toast";
import Dropdown from "primevue/dropdown";

import { setContext, showSuccess, showError } from "@/utils/client";

export default {
  name: "ContextManager",
  components: {
    FileUpload,
    InputText,
    Button,
    InputNumber,
    Toast,
    Dropdown,
    ConfirmDialog,
  },
  data() {
    return {
      uploadedFile: null,
      separator: ".",
      chunkSize: 200,
      overlap: 0,
      loading: false,
      disabled: false,
      selectedStore: "Local",
      stores: ["Local", "Pinecone"],
    };
  },
  computed: {
    nullData() {
      return (
        this.uploadedFile === null ||
        !this.separator ||
        this.chunkSize === null ||
        this.overlap === null ||
        !this.selectedStore
      );
    },
  },
  methods: {
    doPost() {
      this.loading = true;
      this.disabled = true;

      setContext("/context/set", {
        separator: this.separator,
        chunkSize: this.chunkSize,
        overlap: this.overlap,
        file: this.uploadedFile,
        processor: this.selectedStore.toLowerCase(),
      })
        .then((result) => {
          this.$store.dispatch("setApiParams", {
            identifier: this.uploadedFile.name,
            vectorStore: this.selectedStore.toLowerCase(),
          });
          showSuccess(
            "Context set successfully, redirecting to the chat session"
          );
          this.loading = false;
          setTimeout(() => this.$router.push("/chat/document"), 2000);
        })
        .catch((error) => {
          showError(error.message);
          this.loading = false;
          this.disabled = false;
        });
    },
    handleFileSelect(evt) {
      this.uploadedFile = evt.files[0];
    },
  },
};
</script>

<style scoped>
.vertical-justify-center {
  display: flex;
  align-items: flex-end;
}
</style>
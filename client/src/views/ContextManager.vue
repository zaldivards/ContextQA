<template>
  <div class="my-6 justify-content-center">
    <ConfirmDialog></ConfirmDialog>

    <Toast class="z-5" />
    <form @submit.prevent="postData" class="px-3 lg:px-0 w-full lg:w-7 m-auto">
      <h2 class="mb-5">⚙️ Set the context document</h2>

      <div :class="disabled ? ['opacity-50', 'disabled'] : ''" class="grid">
        <FileUpload
          @remove="() => (this.uploadedFile = null)"
          accept=".pdf,.txt,.csv"
          fileLimit="1"
          :maxFileSize="100000000"
          @select="handleFileSelect"
          :showUploadButton="false"
          :multiple="false"
          :pt="{
            thumbnail: { class: 'hidden' },
            badge: { class: 'hidden' },
            details: { class: 'ml-6' },
            root: { class: 'col-12' },
          }"
        >
          <template #empty>
            <p>Drag and drop files here to upload</p>
          </template>
        </FileUpload>
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
import Button from "primevue/button";
import Toast from "primevue/toast";

import { setContext, showSuccess, showError } from "@/utils/client";

export default {
  name: "ContextManager",
  components: {
    FileUpload,
    Button,
    Toast,
    ConfirmDialog,
  },
  data() {
    return {
      uploadedFile: null,
      loading: false,
      disabled: false,
    };
  },
  computed: {
    nullData() {
      return this.uploadedFile === null;
    },
  },
  methods: {
    doPost() {
      this.loading = true;
      this.disabled = true;

      setContext("/qa/ingest/", {
        file: this.uploadedFile,
      })
        .then(() => {
          this.$store.dispatch("setApiParams", this.uploadedFile.name);
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
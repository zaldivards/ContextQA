<template>
  <div class="my-6 justify-content-center">
    <ConfirmDialog></ConfirmDialog>

    <Toast class="z-5" />
    <form @submit.prevent="postData" class="px-3 lg:px-0 w-full lg:w-7 m-auto">
      <h2 class="mb-5">⚙️ Choose and ingest sources</h2>

      <div :class="disabled ? ['opacity-50', 'disabled'] : ''" class="grid">
        <FileUpload
          @remove="handleFileSelectRemove"
          accept=".pdf,.txt,.csv"
          :fileLimit="10"
          :maxFileSize="100000000"
          @select="handleFileSelectRemove"
          :showUploadButton="false"
          :multiple="true"
          :pt="{
            thumbnail: { class: 'hidden' },
            badge: { class: 'hidden' },
            details: { class: 'ml-6' },
            root: { class: 'col-12' },
          }"
        >
          <template #empty>
            <p>
              Drag and drop files here to upload.
              <b>You can upload up to 10 sources</b>
            </p>
          </template>
        </FileUpload>
      </div>
      <Button
        type="button"
        label="Submit"
        icon="pi pi-check"
        @click="sendFiles"
        :disabled="nullData || disabled"
        :loading="loading"
        class="col-offset-4 lg:col-offset-0 col-4 lg:col-2 mt-5"
      />
    </form>
  </div>
</template>
<script>
import ConfirmDialog from "primevue/confirmdialog";
import FileUpload from "primevue/fileupload";
import Button from "primevue/button";
import Toast from "primevue/toast";

import {
  ingestSources,
  showSuccess,
  showError,
  showWarning,
} from "@/utils/client";

const MAX_NUMBER_OF_FILES = 10;

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
      selectedFiles: [],
      loading: false,
      disabled: false,
    };
  },
  computed: {
    nullData() {
      return (
        this.selectedFiles.length == 0 ||
        this.selectedFiles.length > MAX_NUMBER_OF_FILES
      );
    },
  },
  methods: {
    sendFiles() {
      this.loading = true;
      this.disabled = true;

      ingestSources("/sources/ingest/", {
        files: this.selectedFiles,
      })
        .then((ingestionResult) => {
          if (!ingestionResult.completed) {
            showWarning(
              "All sources were skipped because their content has not changed since the last ingestion",
              10000
            );
            this.disabled = false;
          } else {
            if (ingestionResult.skipped_files.length > 0) {
              showWarning(
                "The folowing sources were skipped because their content has not changed since the last ingestion:",
                10000
              );
              ingestionResult.skipped_files.forEach((filename) =>
                showWarning(filename, 10000)
              );
            }
            showSuccess(
              `${ingestionResult.completed} sources were successfully ingested, redirecting to the QA session`
            );

            setTimeout(
              () => this.$router.push("/chat/qa"),
              ingestionResult.skipped_files.length > 0 ? 10000 : 2000
            );
          }
          this.loading = false;
        })
        .catch((error) => {
          showError(error.message);
          this.loading = false;
          this.disabled = false;
        });
    },
    handleFileSelectRemove(evt) {
      this.selectedFiles = evt.files;
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
<template>
  <div>
    <Toast />
    <form @submit.prevent="postData" class="w-7 m-5">
      <div :class="disabled ? ['opacity-50', 'disabled'] : ''">
        <FileUpload
          @remove="() => (this.uploadedFile = null)"
          accept=".pdf,.txt"
          fileLimit="1"
          :maxFileSize="100000000"
          @select="handleFileSelect"
          :showUploadButton="false"
          :multiple="false"
          :pt="{ badge: { style: 'display: none !important' } }"
        />
        <div class="my-4">
          <div class="flex flex-column gap-2">
            <label for="username">Separator</label>
            <InputText
              class="block mb-2 p-inputtext-lg w-auto max-w-max"
              v-model="separator"
              type="text"
              placeholder="Text separator, default '.'"
              id="separator"
            />
          </div>

          <div class="flex flex-column gap-2">
            <label for="chunkSize">Chunk size</label>
            <InputNumber
              class="block mb-2 p-inputtext-lg w-max"
              v-model="chunkSize"
              inputId="integeronly"
              placeholder="Chunk size, default 200"
              :min="0"
              :max="1000"
              id="chunkSize"
            />
          </div>

          <div class="flex flex-column gap-2">
            <label for="overlap">Overlap</label>
            <InputNumber
              class="block outline-none mb-2 p-inputtext-lg w-max"
              inputId="integeronly"
              v-model="overlap"
              placeholder="Chunk overlap, default 0"
              id="overlap"
              :min="0"
              :max="200"
            />
          </div>
        </div>
      </div>
      <Button
        type="button"
        label="Submit"
        icon="pi pi-check"
        @click="postData"
        :disabled="nullData || disabled"
        :loading="loading"
      />
    </form>
  </div>
</template>

<script>
import FileUpload from "primevue/fileupload";
import InputText from "primevue/inputtext";
import InputNumber from "primevue/inputnumber";
import Button from "primevue/button";
import Toast from "primevue/toast";
import { setContext, showSuccess, showError } from "@/utils/client";

export default {
  name: "ContextManager",
  components: { FileUpload, InputText, Button, InputNumber, Toast },
  data() {
    return {
      uploadedFile: null,
      separator: ".",
      chunkSize: 200,
      overlap: 0,
      loading: false,
      disabled: false,
    };
  },
  computed: {
    nullData() {
      return (
        this.uploadedFile === null ||
        !this.separator ||
        this.chunkSize === null ||
        this.overlap === null
      );
    },
  },
  methods: {
    postData() {
      this.loading = true;
      this.disabled = true;
      setContext("api/context/set", {
        separator: this.separator,
        chunkSize: this.chunkSize,
        overlap: this.overlap,
        file: this.uploadedFile,
      })
        .then((result) => {
          this.$store.dispatch("setIdentifier", this.uploadedFile.name);
          showSuccess(
            "Context set successfully, redirecting to the chat session"
          );
          this.loading = false;
          setTimeout(() => this.$router.push("/chat"), 2000);
        })
        .catch((error) => {
          console.log(error);
          showError("Something went wrong: " + error.message);
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

<style>
</style>
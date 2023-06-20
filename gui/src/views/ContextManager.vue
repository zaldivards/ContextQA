<template>
  <form @submit.prevent="setContext" class="w-7 m-5">
    <FileUpload
      @remove="() => (this.uploadedFile = null)"
      accept=".pdf,.txt"
      :maxFileSize="100000000"
      @select="handleFileSelect"
      :showUploadButton="false"
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

    <Button
      type="button"
      label="Submit"
      :loading="loading"
      icon="pi pi-check"
      @click="setContext"
      :disabled="nullData"
    />
  </form>
</template>

<script>
import FileUpload from "primevue/fileupload";
import InputText from "primevue/inputtext";
import InputNumber from "primevue/inputnumber";
import Button from "primevue/button";

export default {
  name: "ContextManager",
  components: { FileUpload, InputText, Button, InputNumber },
  data() {
    return {
      uploadedFile: null,
      separator: ".",
      chunkSize: 200,
      overlap: 0,
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
    setContext() {
      console.log(
        this.uploadedFile,
        this.separator,
        this.chunkSize,
        this.overlap
      );
      //   console.log(evt.target.files);
    },
    handleFileSelect(evt) {
      this.uploadedFile = evt.files[0];
      //   this.uploadedFile = evt.target.files[0];
    },
  },
};
</script>

<style>
</style>
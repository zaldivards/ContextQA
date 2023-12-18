<template>
  <div class="w-full">
    <Card
      :key="i"
      v-for="(source, i) in data"
      class="mx-0 my-5"
      :pt="{
        content: { class: 'mx-0' },
      }"
    >
      <template #title>
        {{ source.title }}
      </template>
      <template #content>
        <p v-if="source.format_ == 'txt'">
          {{ source.content }}
        </p>
        <DataTable v-else-if="source.format_ == 'csv'" :value="source.content">
          <Column
            v-for="(name, i) in Object.keys(source.content[0])"
            :key="i"
            :field="name"
            :header="name"
          ></Column>
        </DataTable>
        <Image
          class="m-0"
          :src="`data:image/jpg;base64,${source.content}`"
          v-else
          preview
        />
      </template>
    </Card>
  </div>
</template>

<script>
import Card from "primevue/card";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Image from "primevue/image";

export default {
  inject: ["dialogRef"],
  name: "SourcesBox",
  components: { Card, DataTable, Column, Image },
  data() {
    return {
      data: [],
    };
  },
  mounted() {
    try {
      this.data = JSON.parse(this.dialogRef.data.sources);
    } catch (e) {
      console.log(e);
    }
  },
};
</script>

<style>
</style>
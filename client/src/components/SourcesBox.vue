<template>
  <div class="w-full grid">
    <p v-if="data.length == 0">No related sources</p>
    <div v-else :key="i" v-for="(source, i) in data" class="mx-0 my-5 col-12 lg:col-6">


      <Card :pt="{
      content: { class: 'mx-0' }, title: { class: 'lg:text-xl text-xs' },
    }" class="h-full">
        <template #title>
          {{ source.title }}
        </template>
        <template #content>
          <p v-if="source.format_ == 'txt'">
            {{ source.content }}
          </p>

          <VerticalRow v-else-if="source.format_ == 'csv'" :cell="source.content[0]" />

          <div v-else class="text-center">
            <Image class="m-0" :src="`data:image/jpg;base64,${source.content}`" preview
              :pt="{ image: { class: 'w-full' }, mask: { class: 'w-full' } }" />
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script>
import Card from "primevue/card";
import Image from "primevue/image";
import VerticalRow from "@/components/VerticalRow.vue"

export default {
  inject: ["dialogRef"],
  name: "SourcesBox",
  components: { Card, Image, VerticalRow },
  data() {
    return {
      data: [],
    };
  },
  mounted() {
    const sources =
      this.dialogRef.data.sources || this.$store.state.latestSources;
    try {
      this.data = JSON.parse(sources);
    } catch (e) {
      console.log(e);
    }
  },
};
</script>

<style></style>
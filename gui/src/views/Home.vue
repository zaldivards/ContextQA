<template>
  <div class="justify-content-center h-screen">
    <div class="m-8">
      <Card
        class="m-auto w-7 text-xl"
        :pt="{
          content: {
            class: 'justify-content-center',
          },
        }"
      >
        <template #content>
          <p class="w-8 m-auto p-2">
            Hi! <span class="text-teal-300">ContextQA</span> is a tool that
            leverages the power of LLMs and it allows you to query any document
            you set. This version supports
            <span class="font-semibold">pdf</span> and
            <span class="font-semibold">txt</span> files.
          </p>
          <p class="w-8 m-auto p-2">
            Before starting querying any document you need to first set the
            vector processor/store in the settings tab. Currently we support the
            <span class="font-semibold">local</span> and
            <span class="font-semibold">pinecone</span>
            processor. Note that some extra settings are required to use the
            pinecone processor. You should choose the local processor if you
            want a quick start.
          </p>
          <p class="w-8 m-auto p-2">
            Additionally, this UI might be used as a sustitute of the ChatGPT
            one, which most of the times idles too much.
          </p>
          <p class="w-8 m-auto p-2">
            Please give us a start on
            <a
              href="https://github.com/zaldivards/llm-retriever/tree/dev"
              class="text-teal-300 no-underline"
              title="Go to repo"
              target="_blank"
              >Github</a
            >.
          </p>
          <p class="w-8 m-auto p-2">Happy Querying!</p>
        </template>
      </Card>
    </div>
  </div>
</template>

<script>
import Card from "primevue/card";
export default {
  name: "HomeSite",
  components: { Card },
};
</script>

<style>
</style>
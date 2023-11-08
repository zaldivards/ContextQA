<template>
  <div class="justify-content-center h-max">
    <div class="m-8">
      <Card
        class="text-lg text-white-alpha-80 max-h-full bg-contextqa-primary"
        :pt="{
          content: {
            class: 'justify-content-center',
          },
          header: {
            class: 'text-center',
          },
        }"
      >
        <template #header>
          <img alt="contextqa logo" src="/images/logo.png" class="w-1 mt-7" />
        </template>
        <template #content>
          <p class="w-8 m-auto p-2">
            Hi!
            <span class="relative"
              ><img
                alt="contextqa text"
                src="/images/title.png"
                class="w-1 relative top-img"
            /></span>
            is a tool that leverages the power of LLMs to help you query any
            document you want. This version of
            <span class="relative"
              ><img
                alt="contextqa text"
                src="/images/title.png"
                class="w-1 relative top-img"
            /></span>
            supports <span class="font-semibold">pdf</span> and
            <span class="font-semibold">txt</span> files.
          </p>
          <p class="w-8 m-auto p-2">
            Before starting querying any document you need to first set the
            vector processor/store, which is used to encode and store the
            document representations and to find the most relevant context, you
            can set this in the settings tab. Currently, we support two types of
            vector processors/stores: the
            <span class="font-semibold">local</span> processor, which runs on
            your local machine, and the
            <span class="font-semibold">pinecone</span> processor, which is a
            cloud-based service. Note that the pinecone processor requires some
            extra settings to be configured. If you want a quick start, we
            recommend choosing the local processor
          </p>
          <p class="w-8 m-auto p-2">
            Additionally, this UI can be used as an alternative to the ChatGPT
            UI, which is another conversational AI tool that may experience long
            idle times. Furthermore, in this latest version you can enable
            internet access for the assistant, which helps to expand its
            knowledge.
          </p>
          <p class="w-8 m-auto p-2">
            Please give us a star on
            <a
              href="https://github.com/zaldivards/ContextQA"
              class="text-teal-300 no-underline"
              title="Go to repo"
              target="_blank"
              >Github</a
            >
            if you find
            <span class="relative"
              ><img
                alt="contextqa text"
                src="/images/title.png"
                class="w-1 relative top-img"
            /></span>
            helpful.
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

<style scoped>
.top-img {
  top: 2px;
}
</style>
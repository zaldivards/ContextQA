<template>
  <div class="formgrid grid mx-7">
    <div class="field col" v-if="!isUser"></div>
    <div class="field col">
      <div class="formgrid grid" :class="isUser ? 'w-max' : ''">
        <Avatar
          icon="pi pi-user"
          class="user-card"
          style="background-color: #2196f3; color: #ffffff"
          :class="isUser ? 'mr-3' : 'ml-3'"
          size="large"
          shape="circle"
          v-if="isUser"
        />
        <Card
          class="field col shadow-none"
          :class="isUser ? ['bg-teal-500', 'text-white'] : 'bg-bluegray-100'"
        >
          <template #content> Otro test </template>
          <template #footer>
            <div
              class="date w-max justify-content-end text-xs"
              :class="isUser ? 'text-white-alpha-70' : 'text-gray-700'"
            >
              2023-06-19 00:00:00
            </div>
          </template>
        </Card>

        <Avatar
          icon="pi pi-prime"
          :class="!isUser ? 'ml-3' : 'mr-3'"
          size="large"
          shape="circle"
          v-if="!isUser"
        />
      </div>
    </div>
    <div class="field col" v-if="isUser"></div>
  </div>

  <!-- <div class="flex flex-wrap" :class="isUser"> -->

  <!-- </div> -->
</template>

<script>
import Card from "primevue/card";
import Avatar from "primevue/avatar";

export default {
  name: "ChatCard",
  props: ["role"],
  components: { Card, Avatar },
  computed: {
    isUser() {
      console.log(this.role);
      return this.role == "user";
    },
  },
};
</script>

<style>
.date {
  /* border-bottom: 0.5px solid rgb(17, 176, 182); */
}
</style>
<template>
    <div class="my-2 py-5 justify-content-center">
        <div class="px-3 lg:px-0 w-screen lg:w-10 m-auto flex flex-column lg:gap-7 md:gap-7">
            <h1>Status of ContextQA components</h1>
            <div class="grid w-full" ref="test">
                <div class="lg:col-4 lg:p-4 md:p-2 md:col-6 col-6" v-for="(item, i) in statuses" :key="i">
                    <div class="relative shadow-5 h-10rem border-round-xl align-content-center text-center bg-black-alpha-40 border-1"
                        :class="statusBadge(item.status)">
                        {{ item.name }}
                        <span class="absolute border-circle lg:w-2rem w-1rem lg:h-2rem h-1rem positioned border-none"
                            v-show="item.status !== 'ok'">
                            <Button icon="pi pi-info-circle" rounded @click="(e) => toggle(e, i)" />
                            <OverlayPanel ref="op">
                                <div v-if="item.status === 'irrelevant'">ContextQA is not using this component</div>
                                <div v-else>
                                    <span class="font-bold">
                                        {{ item.name }}
                                    </span> is not working properly. Please check your settings, logs and/or <a
                                        href="https://github.com/zaldivards/ContextQA/issues/new">report a bug</a>
                                </div>
                            </OverlayPanel>
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import Button from "primevue/button";
import OverlayPanel from 'primevue/overlaypanel';
import {
    fetchResource,
    showError
} from "@/utils/client";
export default {
    name: 'StatusView',
    components: { Button, OverlayPanel },
    data() {
        return {
            statuses: [],
        }
    },
    mounted() {
        fetchResource("/status/?")
            .then(statuses => this.statuses = statuses)
            .catch((error) => showError(error));
    },
    methods: {
        statusBadge(statusStr) {
            if (statusStr === 'ok') return 'border-green-500'
            if (statusStr === 'fail') return 'border-red-500'
            return 'border-yellow-500'
        },
        toggle(event, index) {
            this.$refs.op[index].toggle(event);
        }
    }
}
</script>

<style scoped>
.positioned {
    top: -10px;
    right: -5px;
}

@media screen and (max-width: 1000px) {
    .positioned {
        top: -5px;
        right: 15px;
    }
}
</style>
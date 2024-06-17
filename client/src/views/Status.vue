<template>
    <div class="my-2 py-5 justify-content-center">
        <div class="px-3 lg:px-0 w-screen lg:w-10 m-auto flex flex-column lg:gap-7 md:gap-7">
            <div class="flex gap-3 align-items-center">
                <h1 class="lg:text-2xl md:text-2xl text-xl">Status of ContextQA components</h1>
                <Button icon="pi pi-refresh" rounded text size="large" @click="fetchStatus" title="Refresh"/>
            </div>
            <div v-if="loading" class="flex justify-content-center align-items-center h-30rem">
                <LoadingSpinner size="5rem" />
            </div>
            <div class="grid w-full" v-else>
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
                                    </span> is not working properly. Please check your settings, server logs and/or <a
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
import LoadingSpinner from "@/components/LoadingSpinner";
import {
    fetchResource,
    showError
} from "@/utils/client";
export default {
    name: 'StatusView',
    components: { Button, OverlayPanel, LoadingSpinner },
    data() {
        return {
            statuses: [],
            loading: true
        }
    },
    mounted() {
        this.fetchStatus()
    },
    methods: {
        fetchStatus() {
            this.loading = true
            fetchResource("/status/?")
                .then(statuses => {
                    this.statuses = statuses
                    this.loading = false
                })
                .catch((error) => showError(error));
        },
        statusBadge(statusStr) {
            if (statusStr === 'ok') return 'border-green-500'
            if (statusStr === 'fail') return 'border-red-500'
            return 'border-gray-500'
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
<template>
    <div class="my-2 justify-content-center">
        <div class="px-3 lg:px-0 w-full lg:w-9 m-auto grid">
            <h1>Manage sources</h1>
            <DataTable v-model:selection="selectedSources" :value="sources" dataKey="id" tableStyle="min-width: 50rem"
                paginator size="large" :rows="size" :totalRecords="totalRecords" :rowsPerPageOptions="[5, 10]"
                @page="pageUpdated" :lazy="true" :loading="loading">
                <Column field="id" header="ID"></Column>
                <Column field="title" header="Name"></Column>
                <Column field="digest" header="Digest"></Column>
                <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
            </DataTable>

            <Button type="button" label="Remove selected sources" icon="pi pi-times" severity="danger"
                @click="deleteSources" class="col-offset-4 lg:col-offset-0 col-4 lg:col-3 mt-5" />
        </div>

    </div>
</template>

<script>
import Button from "primevue/button";

import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import {
    fetchResource,
    showError
} from "@/utils/client";
export default {
    name: "SourcesManager",
    components: { Column, DataTable, Button },
    data() {
        return {
            loading: false,
            sources: [],
            selectedSources: [],
            size: 10,
            totalRecords: 0,
        }
    },
    mounted() {
        this.updateSources(this.size, 0)
    },
    methods: {
        updateSources(limit, skip) {
            this.loading = true;
            fetchResource("/sources/?" + new URLSearchParams({ limit: limit, skip: skip }))
                .then(json => {
                    this.sources = json.sources
                    this.totalRecords = json.total
                }).catch((error) => showError(error));
            this.loading = false
        },
        deleteSources() {
            console.log(this.selectedSources, this.size, this.totalRecords);
        },
        pageUpdated(evt) {
            this.updateSources(evt.rows, evt.first)
        },
    }
}
</script>

<style></style>
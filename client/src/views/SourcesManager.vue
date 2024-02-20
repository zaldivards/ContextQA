<template>
    <div class="my-2 justify-content-center">
        <Toast class="z-5" />
        <div class="px-3 lg:px-0 w-full lg:w-10 m-auto">
            <h1>Manage sources</h1>
            <DataTable v-model:selection="selectedSources" :value="sources" dataKey="id" tableStyle="min-width: 50rem"
                paginator size="large" :rows="size" :totalRecords="totalRecords" :rowsPerPageOptions="[5, 10]"
                @page="pageUpdated" :lazy="true" :loading="loading">
                <Column field="id" header="ID"></Column>
                <Column field="title" header="Name"></Column>
                <Column field="digest" header="Digest"></Column>
                <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
                <template #empty>No sources available</template>
            </DataTable>

            <Button type="button" label="Remove selected sources" icon="pi pi-times" severity="danger"
                @click="deleteSources" class="col-offset-4 lg:col-offset-0 col-4 lg:col-3 mt-5" :disabled="disableButton" />
        </div>

    </div>
</template>

<script>
import Button from "primevue/button";
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Toast from "primevue/toast";
import {
    fetchResource,
    showError,
    showSuccess
} from "@/utils/client";
export default {
    name: "SourcesManager",
    components: { Column, DataTable, Button, Toast },
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
            const sourcesNames = this.selectedSources.map(entry => entry.title)
            fetchResource("/sources/remove/", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(sourcesNames)
            })
                .then(json => {
                    showSuccess(`${json.removed} source(s) removed successfully`)
                    this.sources = this.sources.filter(entry => !sourcesNames.includes(entry.title))
                }).catch((error) => showError(error));
        },
        pageUpdated(evt) {
            this.updateSources(evt.rows, evt.first)
        },
    },
    computed: {
        disableButton() {
            return this.selectedSources.length == 0;
        }
    }
}
</script>

<style></style>
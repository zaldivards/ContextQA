<template>
    <div class="my-2 justify-content-center">
        <Toast class="z-5" />
        <div class="px-3 lg:px-0 w-full lg:w-10 m-auto">
            <h1>Manage sources</h1>
            <DataTable v-model:selection="selectedSources" :value="sources" dataKey="id" tableStyle="min-width: 50rem"
                paginator size="large" :rows="size" :totalRecords="totalRecords" :rowsPerPageOptions="[5, 10]"
                @page="pageUpdated" :lazy="true" :loading="loading">

                <template #header>
                    <div class="flex justify-content-between">
                        <Button type="button" icon="pi pi-filter-slash" label="Clear" outlined @click="clear()" />
                        <IconField iconPosition="left">
                            <InputIcon>
                                <i class="pi pi-search" />
                            </InputIcon>
                            <InputText v-model="searchSubstr" placeholder="Search sources" ref="searcher" @input="filter" />
                        </IconField>
                    </div>
                </template>

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
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';
import InputText from 'primevue/inputtext';
import Toast from "primevue/toast";
import {
    fetchResource,
    showError,
    showSuccess
} from "@/utils/client";
export default {
    name: "SourcesManager",
    components: { Column, DataTable, Button, Toast, InputText, IconField, InputIcon },
    data() {
        return {
            loading: false,
            sources: [],
            selectedSources: [],
            size: 10,
            totalRecords: 0,
            searchSubstr: null
        }
    },
    mounted() {
        this.updateSources(this.size, 0)
        window.onkeydown = ((evt) => {
            this.$refs.searcher.$el.focus()
            if (evt.keyCode == 27) {
                this.clear()
            }
        })
        window.focus()
    },
    beforeUnmount(){
        window.onkeydown = null
    },
    methods: {
        updateSources(limit, skip, query = "") {
            this.loading = true;
            fetchResource("/sources/?" + new URLSearchParams({ limit: limit, skip: skip, query: query }))
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
                    this.selectedSources = []
                }).catch((error) => showError(error));
        },
        pageUpdated(evt) {
            this.updateSources(evt.rows, evt.first)
        },
        clear() {
            this.searchSubstr = null
            this.$refs.searcher.$el.blur()
            this.updateSources(this.size, 0)
        },
        filter() {
            setTimeout(() => {
                this.updateSources(this.size, 0, this.searchSubstr)
            }, 500);
        }
    },
    computed: {
        disableButton() {
            return this.selectedSources.length == 0;
        }
    }
}
</script>

<style></style>
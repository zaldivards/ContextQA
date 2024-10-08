<template>
    <div class="my-6">
        <ConfirmDialog :draggable="false" />
        <Toast class="z-5" />
        <div class="px-3 lg:px-0 lg:w-10 m-auto">
            <h1>Manage sources</h1>
            <DataTable v-model:selection="selectedSources" :value="sources" dataKey="id" paginator size="normal"
                selectionMode="multiple" :rows="size" :totalRecords="totalRecords" :rowsPerPageOptions="[5, 10]"
                @page="pageUpdated" :lazy="true" :loading="loading" class="dt-responsive-table" :pt="{
                    bodyRow: { class: 'bg-black-alpha-40 text-white' }, header: { class: 'bg-black-alpha-40 border-none' }
                }">

                <template #header>
                    <div class="flex justify-content-between">
                        <Button type="button" icon="pi pi-filter-slash" text size="large" @click="clear()"
                            title="Clear filter" />
                        <div class="flex gap-3 align-items-center">
                            <Button type="button" icon="pi pi-refresh" text size="large"
                                @click="updateSources(size, 0, searchSubstr)" title="Refresh" />
                            <IconField iconPosition="left">
                                <InputIcon class="pi pi-search" />
                                <InputText v-model="searchSubstr" placeholder="Search..." ref="searcher"
                                    @input="filter" />
                            </IconField>
                        </div>
                    </div>
                </template>

                <Column selectionMode="multiple" :pt="{
                    headerCell: { class: 'bg-blue-800 text-white' }
                }" class="border-t-1 border-black-alpha-60" />
                <Column field="id" header="ID" :pt="{
                    headerCell: { class: 'bg-blue-800 text-white' }
                }" class="border-t-1 border-black-alpha-60" />
                <Column field="title" header="Name" :pt="{
                    headerCell: { class: 'bg-blue-800 text-white' }
                }" class="border-t-1 border-black-alpha-60" />
                <Column field="digest" header="Digest" :pt="{
                    headerCell: { class: 'bg-blue-800 text-white' }
                }" class="border-t-1 border-black-alpha-60 hash-style" />
                <template #empty>No sources available</template>
            </DataTable>
            <button @click="deleteSources"
                class="mt-5 flex align-items-center bg-red-700 text-white border-none gap-2 p-3 text-sm border-round-sm"
                :class="disableButton ? 'opacity-50 cursor-auto' : 'cursor-pointer'" :disabled="disableButton">
                <i class="pi pi-trash" />
                <span>Remove</span>
            </button>
        </div>

    </div>
</template>

<script>
import Button from "primevue/button";
import Column from 'primevue/column';
import ConfirmDialog from "primevue/confirmdialog";
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
    components: { Column, DataTable, Button, Toast, InputText, IconField, InputIcon, ConfirmDialog },
    data() {
        return {
            loading: false,
            sources: [],
            selectedSources: [],
            size: 10,
            totalRecords: 0,
            searchSubstr: null,
            recoverContext: false
        }
    },
    mounted() {

        if (this.$store.state.sourcesDetails.sources.length == 0) {
            this.updateSources(this.size, 0)
        }
        else {
            this.sources = this.$store.state.sourcesDetails.sources
            this.totalRecords = this.$store.state.sourcesDetails.total
            this.searchSubstr = this.$store.state.sourcesDetails.query
            this.size = this.$store.state.sourcesDetails.size
            this.highlightPage(this.$store.state.sourcesDetails.page)
        }


        window.onkeydown = ((evt) => {
            this.$refs.searcher.$el.focus()
            if (evt.keyCode == 27) {
                this.clear()
            }
        })
        window.focus()
    },
    beforeUnmount() {
        window.onkeydown = null
    },
    methods: {
        highlightPage(page) {
            this.$nextTick(() => {
                const nodes = this.getPageButtonsNodes()
                for (let i = 0; i < nodes.length; i++) {
                    const node = nodes[i];
                    if (parseInt(node.innerText) == page) {
                        this.recoverContext = true
                        node.click()
                    }
                }
            });
        },
        getPageButtonsNodes() {
            return document.getElementsByClassName("p-paginator-page");
        },
        updateSources(limit, skip, query = "") {
            this.loading = true;
            fetchResource("/sources/?" + new URLSearchParams({ limit: limit, skip: skip, query: query ?? "" }))
                .then(json => {
                    this.sources = json.sources
                    this.totalRecords = json.total
                    this.size = limit
                    this.$store.dispatch("setSourcesDetails", { sources: this.sources, total: this.totalRecords, query: query, size: this.size, page: (skip / limit) + 1 })
                }).catch((error) => showError(error));
            this.loading = false
        },
        deleteSources() {
            this.$confirm.require({
                message: "Are you sure you want to delete the selected sources?",
                header: `Danger Zone - Removing ${this.selectedSources.length} source(s)`,
                icon: "pi pi-info-circle",
                rejectClass: 'p-button-secondary p-button-outlined',
                acceptClass: 'p-button-danger',
                accept: () => {
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
                reject: () => this.selectedSources = []
            })
        },
        pageUpdated(evt) {
            if (!this.recoverContext)
                this.updateSources(evt.rows, evt.first, this.searchSubstr)
            this.recoverContext = false
        },
        clear() {
            this.searchSubstr = null
            this.$refs.searcher.$el.blur()
            this.updateSources(this.size, 0)
            this.recoverContext = true
            this.getPageButtonsNodes() ?? [0].click()
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
<style>
.hash-style {
    word-break: break-all;
    overflow-wrap: break-word
}
</style>
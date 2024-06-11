<template>
    <div class="my-6 justify-content-center">
        <ConfirmDialog :draggable="false" />
        <Toast class="z-5" />

        <div class="px-3 lg:px-0 w-full lg:w-7 m-auto grid">
            <h1 class="mb-5 col-12">Vector store configurations</h1>

            <h3 class="mb-5 col-12">Processors</h3>


            <RadioBox provider="chroma" class="col-6 max-h-15rem" v-model="store" :checked="store == 'chroma'"
                @change="onBoxCHange">
            </RadioBox>
            <RadioBox provider="pinecone" class="col-6 max-h-15rem" v-model="store" :checked="store == 'pinecone'"
                @change="onBoxCHange">
            </RadioBox>

            <div class="grid col-12 mt-5" v-if="isLocal">
                <div class="flex flex-column gap-2 col-6">
                    <label for="home">Vector store home</label>
                    <InputText id="home" v-model="storeParams['home']" class="border-round-xl" />
                </div>
                <div class="flex flex-column gap-2 col-6">
                    <label for="collection">Collection name</label>
                    <InputText id="collection" v-model="storeParams['collection']" class="border-round-xl" />
                </div>
            </div>

            <div class="grid col-12 mt-5" v-else>
                <div class="flex flex-column gap-2 col-6">
                    <label for="environment">Environment region</label>
                    <InputText id="environment" v-model="storeParams['environment']"
                        class="border-round-xl" />
                </div>
                <div class="flex flex-column gap-2 col-6">
                    <label for="index">Index</label>
                    <InputText id="index" v-model="storeParams['index']" class="border-round-xl" />
                </div>

                <div class="flex flex-column gap-2 lg:col-6 md:col-6 col-8">
                    <label for="token">Access token</label>
                    <div class="flex justify-content-between">
                        <Password id="token" :feedback="false" v-model="storeParams['token']"
                            inputClass="border-round-xl" class="flex-grow-1"/>
                        <HelpButton>
                            <template #content>
                                <ol>
                                    <li>Create an <a href="https://www.pinecone.io/" target="_blank"
                                            class="no-underline">account</a></li>
                                    <li>Generate and get the API key in the <span class="font-bold">API keys</span>
                                        section</li>
                                </ol>
                            </template>
                        </HelpButton>
                    </div>
                </div>
            </div>


            <h3 class="mb-2 col-12">Advanced settings</h3>

            <div class="grid col-12">
                <div class="flex flex-column gap-2 col-6">
                    <label for="chunkSize">Chunk size</label>

                    <Dropdown v-model="chunkSize" :options="[2000, 1000, 500, 400, 300, 100]"
                        class="col-12 bg-inherit border-black-alpha-20" :focusOnHover="false" :pt="{
                            panel: { class: 'bg-inherit' }
                        }" placeholder="Select the chunk size" id="chunkSize"></Dropdown>
                </div>
                <div class="flex flex-column gap-2 col-6">
                    <label for="overlap">Chunk overlap</label>

                    <Dropdown v-model="overlap" :options="[1000, 500, 200, 100, 50]"
                        class="col-12 bg-inherit border-black-alpha-20" :focusOnHover="false" :pt="{
                            panel: { class: 'bg-inherit' }
                        }" placeholder="Select the chunk overlap" id="overlap"></Dropdown>
                </div>

            </div>
            <div class="mx-auto lg:mx-0">
                <Button type="button" label="Save" icon="pi pi-check" @click="setConfig" class="mt-5"
                    :disabled="disableButton" rounded />
            </div>

        </div>
    </div>

</template>

<script>
import Button from "primevue/button";
import ConfirmDialog from "primevue/confirmdialog";
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import RadioBox from "@/components/RadioBox";
import Toast from "primevue/toast";
import HelpButton from '@/components/HelpButton'


import {
    fetchResource,
    showError,
    showSuccess
} from "@/utils/client";

export default {
    name: "VectorStoreSettings",
    components: { RadioBox, InputText, Password, Dropdown, Button, Toast, ConfirmDialog, HelpButton },
    props: { byPassDialog: Boolean },
    created() {
        fetchResource("/settings/store").then(settings => {
            this.store = settings.store
            this.initialStore = this.store
            this.chunkSize = settings.chunk_size
            this.overlap = settings.overlap
            this.storeParams = settings.store_params
            this.initialStoreParams = this.storeParams
        })
            .catch((error) => showError(error));
    },
    data() {
        return {
            initialStore: '',
            store: '',
            chunkSize: 0,
            overlap: 0,
            initialStoreParams: {},
            storeParams: {}
        }
    },
    methods: {
        fetchFunction() {
            fetchResource("/settings/store", {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ store: this.store, chunk_size: this.chunkSize, overlap: this.overlap, store_params: this.storeParams })
            }).then(response => {
                this.store = response.store
                this.chunkSize = response.chunk_size
                this.overlap = response.overlap
                this.storeParams = response.store_params
                showSuccess("Settings successfully updated")
            }).catch((error) => showError(error));
        },
        setConfig() {
            if (this.byPassDialog) {
                this.fetchFunction()
            }
            else {
                this.$confirm.require({
                    message: "Are you sure you want to update the store settings?",
                    header: "Danger Zone",
                    icon: "pi pi-info-circle",
                    rejectClass: 'p-button-secondary p-button-outlined',
                    acceptClass: 'p-button-danger',
                    accept: this.fetchFunction
                })
            }
        },

        onBoxCHange() {
            if (this.initialStore != this.store)

                this.storeParams = this.store == "chroma" ? { home: '', collection: '' } : { index: '', environment: '' };

            else
                this.storeParams = this.initialStoreParams
        }
    },
    computed: {
        isLocal() {
            return this.store == "chroma"
        },
        disableButton() {
            for (var key in this.storeParams) {
                return (this.storeParams[key] == null || this.storeParams[key] == "") && key != "token"
            }
            return false
        }
    }
}
</script>

<style></style>
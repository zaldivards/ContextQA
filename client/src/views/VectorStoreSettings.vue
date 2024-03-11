<template>
    <div class="my-6 justify-content-center">
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
                    <InputText id="home" v-model="storeParams['home']" />
                </div>
                <div class="flex flex-column gap-2 col-6">
                    <label for="collection">Colletion name</label>
                    <InputText id="collection" v-model="storeParams['collection']" />
                </div>
            </div>

            <div class="grid col-12 mt-5" v-else>
                <div class="flex flex-column gap-2 col-6">
                    <label for="token">Access token</label>
                    <Password id="token" :feedback="false" v-model="storeParams['token']" />
                </div>
                <div class="flex flex-column gap-2 col-6">
                    <label for="index">Index</label>
                    <InputText id="index" v-model="storeParams['index']" />
                </div>

                <div class="flex flex-column gap-2 col-6">
                    <label for="environment">Environment region</label>
                    <InputText id="environment" v-model="storeParams['environment']" />
                </div>
            </div>


            <h3 class="mb-2 col-12">Advanced settings</h3>

            <div class="grid col-12">
                <Dropdown v-model="chunkSize" :options="[2000, 1000, 500, 400, 300, 100]"
                    class="col-6 bg-inherit border-black-alpha-20" :focusOnHover="false" :pt="{
                panel: { class: 'bg-inherit' }
            }" placeholder="Select the chunk size"></Dropdown>

                <Dropdown v-model="overlap" :options="[1000, 500, 200, 100, 50]"
                    class="col-6 bg-inherit border-black-alpha-20" :focusOnHover="false" :pt="{
                panel: { class: 'bg-inherit' }
            }" placeholder="Select the chunk overlap"></Dropdown>
            </div>

            <Button type="button" label="Save" icon="pi pi-check" @click="setConfig"
                class="col-offset-4 lg:col-offset-0 col-4 lg:col-2 mt-5" :disabled="disableButton"/>
        </div>
    </div>

</template>

<script>
import Button from "primevue/button";
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import RadioBox from "@/components/RadioBox";
import Toast from "primevue/toast";

import {
    fetchResource,
    showError,
    showSuccess
} from "@/utils/client";

export default {
    name: "VectorStoreSettings",
    components: { RadioBox, InputText, Password, Dropdown, Button, Toast },
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
        setConfig() {
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
            console.log(this.storeParams);
            for (var key in this.storeParams) {
                return (this.storeParams[key] == null || this.storeParams[key] == "") && key != "token"
            }
            return false
        }
    }
}
</script>

<style></style>
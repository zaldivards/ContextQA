<template>
    <div class="my-6 justify-content-center">
        <ConfirmDialog></ConfirmDialog>
        <Toast class="z-5" />

        <div class="px-3 lg:px-0 w-full lg:w-7 m-auto grid">

            <h1 class="mb-5 col-12">LLM configurations</h1>


            <h3 class="mb-5 col-12">Providers</h3>


            <RadioBox provider="openai" class="col-6 max-h-15rem" :checked="provider == 'openai'" v-model="provider"
                @change="onBoxCHange">
            </RadioBox>
            <RadioBox provider="google" class="col-6 max-h-15rem" :checked="provider == 'google'" v-model="provider"
                @change="onBoxCHange">
            </RadioBox>

            <h3 class="mb-5 col-12">Models</h3>

            <div class="grid col-12">

                <div class="col-6">
                    <Dropdown v-model="selectedModel" :options="modelOptions"
                        class="w-full bg-inherit border-black-alpha-20 border-round" :focusOnHover="false" :pt="{
                            panel: { class: 'bg-inherit' }
                        }" placeholder="Select a model"></Dropdown>
                </div>
                <div class="col-6">
                    <label for="temperature">Temperature</label>
                    <Slider v-model="temperature" class="mt-2" :min="0.1" :max="2.0" :step="0.1" id="temperature" />
                    <div class="mt-2">{{ temperature }}</div>
                </div>
                <div class="col-6">
                    <label for="token">Access token</label>
                    <Password v-model="token" :feedback="false" id="token" :pt="{
                        root: { 'class': 'p-0' }
                    }" class="w-full" inputClass="border-round-xl" />
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
import Password from 'primevue/password';
import RadioBox from "@/components/RadioBox";
import Slider from 'primevue/slider';
import Toast from "primevue/toast";

import {
    fetchResource,
    showError,
    showSuccess
} from "@/utils/client";

export default {
    name: "ModelSetttings",
    components: { RadioBox, Slider, Button, Password, Toast, Dropdown, ConfirmDialog },
    created() {
        fetchResource("/settings/model").then(settings => {
            this.selectedModel = settings.model
            this.initialModel = this.selectedModel
            this.provider = settings.provider
            this.initialProvider = this.provider
            this.temperature = settings.temperature
            settings.provider_options.forEach(entry => {
                this.globalModelOptions[entry.provider] = entry.models
            })
        })
            .catch((error) => showError(error));
    },
    data() {
        return {
            initialProvider: "",
            provider: "",
            selectedModel: "",
            initialModel: "",
            temperature: 0.1,
            globalModelOptions: {},
            token: ""
        }
    },
    methods: {
        setConfig() {
            this.$confirm.require({
                message: "Are you sure you want to update the model settings?",
                header: "Danger Zone",
                icon: "pi pi-info-circle",
                rejectClass: 'p-button-secondary p-button-outlined',
                acceptClass: 'p-button-danger',
                accept: () => {
                    fetchResource("/settings/model", {
                        method: 'PATCH',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ provider: this.provider, model: this.selectedModel, temperature: this.temperature, token: this.token || null })
                    }).then(response => {
                        this.selectedModel = response.model
                        this.provider = response.provider
                        this.temperature = response.temperature
                        showSuccess("Settings were updated successfully")
                    }).catch((error) => showError(error));
                }
            })
        },
        onBoxCHange() {
            if (this.initialProvider != this.provider)
                this.selectedModel = null;
            else
                this.selectedModel = this.initialModel
        }
    },
    computed: {
        modelOptions() {
            return this.globalModelOptions[this.provider]
        },
        disableButton() {
            return this.selectedModel == null
        }
    }
}
</script>

<style>
.p-dropdown {
    border-color: inherit !important;
    box-shadow: none !important;
    outline: none !important;
}

.p-highlight {
    background-color: #183462 !important;
    color: #c9dcfa;
}

.p-password-input:focus {
    outline: none !important;
}

.p-password-input {
    width: 100%;
}
</style>
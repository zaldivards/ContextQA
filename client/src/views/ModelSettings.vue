<template>
    <div class="my-6 justify-content-center">
        <Toast class="z-5" />

        <div class="px-3 lg:px-0 w-full lg:w-7 m-auto grid">

            <h1 class="mb-5 col-12">LLM configurations</h1>


            <h3 class="mb-5 col-12">Providers</h3>


            <RadioBox provider="openai" class="col-6 max-h-15rem" :checked="provider == 'openai'" v-model="provider">
            </RadioBox>
            <RadioBox provider="google" class="col-6 max-h-15rem" :checked="provider == 'google'" v-model="provider">
            </RadioBox>

            <h3 class="mb-5 col-12">Models</h3>

            <Listbox v-model="selectedModel" :options="modelOptions" class="col-5 bg-inherit border-black-alpha-20"
                :focusOnHover="false" :pt="{
                    item: { class: 'bg-inherit' }
                }"></Listbox>
            <div class="col-7">
                <label for="temperature">Temperature</label>
                <Slider v-model="temperature" class="mt-2" :min="0.1" :max="2.0" :step="0.1" id="temperature" />
                <div class="mt-2">{{ temperature }}</div>
            </div>
            <div class="col-12">
                <div for="token">Access token</div>
                <Password v-model="token" :feedback="false" id="token" class="col-5" :pt="{
                    root: { 'class': 'p-0' }
                }" />
            </div>
            <Button type="button" label="Set model config" icon="pi pi-check" @click="setConfig"
                class="col-offset-4 lg:col-offset-0 col-4 lg:col-3 mt-5" :disabled="disableButton" />
        </div>
    </div>
</template>

<script>
import Button from "primevue/button";
import Listbox from 'primevue/listbox';
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
    components: { RadioBox, Listbox, Slider, Button, Password, Toast },
    created() {
        fetchResource("/settings/").then(settings => {
            this.selectedModel = settings.model
            this.provider = settings.provider
            this.temperature = settings.temperature
            settings.provider_options.forEach(entry => {
                this.globalModelOptions[entry.provider] = entry.models
            })
        })
            .catch((error) => showError(error));
    },
    data() {
        return {
            provider: "",
            selectedModel: "",
            temperature: 0.1,
            globalModelOptions: {},
            token: ""
        }
    },
    methods: {
        setConfig() {
            console.log(this.selectedModel, this.temperature, this.provider);
            fetchResource("/settings/", {
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
.p-listbox-item:hover,
.p-listbox-item:focus {
    background-color: #183462 !important;
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
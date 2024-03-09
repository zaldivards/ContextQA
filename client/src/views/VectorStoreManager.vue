<template>
    <div class="my-6 justify-content-center">

        <div class="px-3 lg:px-0 w-full lg:w-7 m-auto grid">
            <h1 class="mb-5 col-12">Vector store configurations</h1>

            <h3 class="mb-5 col-12">Processors</h3>


            <RadioBox provider="chroma" class="col-6 max-h-15rem" v-model="store" :checked="store == 'chroma'">
            </RadioBox>
            <RadioBox provider="pinecone" class="col-6 max-h-15rem" v-model="store" :checked="store == 'pinecone'">
            </RadioBox>

            <div class="grid col-12 mt-5" v-if="isLocal">
                <div class="flex flex-column gap-2 col-6">
                    <label for="home">Vector store home</label>
                    <InputText id="home" />
                </div>
                <div class="flex flex-column gap-2 col-6">
                    <label for="collection">Colletion name</label>
                    <InputText id="collection" />
                </div>
            </div>

            <div class="grid col-12 mt-5" v-else>
                <div class="flex flex-column gap-2 col-6">
                    <label for="token">Access token</label>
                    <Password id="token" :feedback="false" />
                </div>
                <div class="flex flex-column gap-2 col-6">
                    <label for="index">Index</label>
                    <InputText id="index" />
                </div>

                <div class="flex flex-column gap-2 col-6">
                    <label for="environment">Environment region</label>
                    <InputText id="environment" />
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

            <Button type="button" label="Save" icon="pi pi-check"
                class="col-offset-4 lg:col-offset-0 col-4 lg:col-2 mt-5" />
        </div>
    </div>

</template>

<script>
import Button from "primevue/button";
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import RadioBox from "@/components/RadioBox";


export default {
    name: "VectorStoreManager",
    components: { RadioBox, InputText, Password, Dropdown, Button },
    data() {
        return {
            store: '',
            chunkSize: 0,
            overlap: 0
        }
    },
    computed: {
        isLocal() {
            return this.store == "chroma"
        }
    }
}
</script>

<style></style>
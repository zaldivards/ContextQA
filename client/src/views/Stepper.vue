<template>
    <div>
        <Stepper :pt="{
            panelContainer: { class: 'bg-inherit text-white' },
            stepperpanel: {
                content: { class: 'h-2rem' },
                header: { class: 'bg-inherit' },
                action: { class: 'bg-inherit' },
                title: { class: 'text-white' }
            },
        }" v-if="!hasFinished" :linear="true">
            <StepperPanel header="LLM">
                <template #content="{ nextCallback }">
                    <div class="relative">
                        <ModelSettings byPassDialog />
                        <Button icon="pi pi-chevron-right" rounded size="large" class="absolute top-50 right-0"
                            @click="nextCallback" title="Next" severity="secondary" />
                    </div>
                </template>
            </StepperPanel>
            <StepperPanel header="Vector store">
                <template #content="{ prevCallback, nextCallback }">
                    <div class="relative">
                        <VectorStoreSettings byPassDialog />
                        <Button icon="pi pi-chevron-left" rounded size="large" class="absolute top-50 left-0"
                            @click="prevCallback" title="Prev" severity="secondary" />
                        <Button icon="pi pi-chevron-right" rounded size="large" class="absolute top-50 right-0"
                            @click="nextCallback" title="Next" severity="secondary" />
                    </div>
                </template>
            </StepperPanel>
            <StepperPanel header="Extras">
                <template #content="{ prevCallback }">
                    <div class="relative">
                        <ExtraSettings byPassDialog />
                        <Button icon="pi pi-chevron-left" rounded size="large" class="absolute top-50 left-0"
                            @click="prevCallback" title="Prev" severity="secondary" />
                        <Button icon="pi pi-check" rounded size="large" class="absolute top-50 right-0"
                            severity="success" @click="onDone" />
                    </div>
                </template>
            </StepperPanel>
        </Stepper>
        <div class="flex h-screen justify-content-center align-items-center fadeinright animation-duration-1000 animation-ease-out"
            v-else>
            <h1 class="lg:text-8xl md:text-8xl text-lg">That's it!!! Happy querying 🎊</h1>
        </div>
    </div>
</template>

<script>

import Button from 'primevue/button'
import Stepper from 'primevue/stepper';
import StepperPanel from 'primevue/stepperpanel';
import ModelSettings from '@/views/ModelSettings'
import VectorStoreSettings from "@/views/VectorStoreSettings"
import ExtraSettings from "@/views/ExtraSettings"

export default {
    name: 'StepperView',
    components: { Stepper, StepperPanel, ModelSettings, VectorStoreSettings, ExtraSettings, Button },
    data() {
        return {
            hasFinished: false,
        }
    },
    methods: {
        onDone() {
            this.hasFinished = true
            this.$emit('finish')
        }
    }
}
</script>

<template>
    <Button :icon="`pi ${copied ? 'pi-check' : 'pi-copy'}`" text class="bg-inherit text-gray-300" title="Copy"
        size="large" @click="onClick" />
</template>

<script>
import Button from "primevue/button";
export default {
    name: 'CopyButton',
    components: { Button },
    props: { content: String },
    data() {
        return {
            copied: false,
        }
    },
    methods: {
        onClick() {
            navigator.clipboard.writeText(this.content.replace('<sources>', ''))
            this.copied = true
            setTimeout(() => this.copied = false, 2000)
        }
    }
}
</script>

<style></style>
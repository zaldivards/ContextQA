<template>
    <span>
        <Button icon="pi pi-question-circle" rounded text @click="(e) => toggle(e)" size="large" title="Help" />
        <OverlayPanel ref="op">
            <slot name="content" />
        </OverlayPanel>
    </span>
</template>

<script>
import Button from "primevue/button";
import OverlayPanel from 'primevue/overlaypanel';

export default {
    name: 'HelpButton',
    components: { Button, OverlayPanel },
    methods: {
        toggle(event) {
            this.$refs.op.toggle(event);
        }
    }
}
</script>
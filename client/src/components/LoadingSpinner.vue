<template>
    <div :style="{ height: size, width: size, borderTopColor: 'blue' }"
        class="animate-spin border-1 border-circle" />
</template>

<script>
export default {
    name: 'LoadingSpinner',
    props: { size: String }
}
</script>

<style scoped>
@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}
.animate-spin {
    animation: spin 1s linear infinite;
}
</style>
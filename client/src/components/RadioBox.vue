<template>
    <label :title="capitalizedProvider"
        class="text-center border-round-2xl flex flex-column justify-content-center align-items-center"
        :class="checked ? 'checked shadow-4' : ''" @mouseover="hover = true" @mouseleave="hover = false"
        :style="{ filter: imgFilter }">
        <input type="radio" name="provider" :value="provider" v-model="inputValue" :checked="checked" />
        <img alt="provider logo" :src="src" class="max-w-full max-h-full" />
    </label>
</template>

<script>
export default {
    name: "RadioBox",
    data() {
        return {
            hover: false
        };
    },
    props: { provider: String, checked: Boolean, modelValue: String },
    computed: {
        src() {
            return `/images/${this.provider}.png`
        },
        capitalizedProvider() {
            return this.provider.charAt(0).toUpperCase() + this.provider.slice(1);
        },
        inputValue: {
            get() {
                return this.modelValue
            },
            set(value) {
                this.$emit('update:modelValue', value)
            }
        },
        imgFilter() {
            return this.checked || this.hover ? 'grayscale(0%)' : 'grayscale(100%)';
        }
    }
}
</script>

<style scoped>
input[type="radio"] {
    position: absolute;
    opacity: 0;
}

input[type="radio"]:hover,
label:hover {
    cursor: pointer;
}

label {
    background-color: rgba(252, 254, 255, 0);
}

.checked {
    background-color: #10223f
}
</style>
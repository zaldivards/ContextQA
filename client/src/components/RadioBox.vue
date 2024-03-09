<template>
    <label :title="capitalizedProvider" class="text-center border-round-2xl" :class="checked ? 'checked' : ''">
        <input type="radio" name="provider" :value="provider" v-model="inputValue" :checked="checked" />
        <img alt="provider logo" :src="src" class="max-w-full max-h-full" />
    </label>
</template>

<script>
export default {
    name: "RadioBox",
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


input[type="radio"]:checked+img,
input[type="radio"]:hover+img {
    filter: grayscale(0%);
}

label:hover,
.checked {
    background-color: white;
}

img {
    filter: grayscale(100%);
}
</style>
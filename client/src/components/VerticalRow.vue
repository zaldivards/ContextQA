<template>
    <div>
        <table>
            <tbody>
                <tr :key="i" v-for="([name, value], i) in Object.entries(cell)" class="cursor-pointer">
                    <th class="text-left border-bottom-1 border-black-alpha-40 lg:text-base md:text-base text-xs">{{
                        capitalize(name) }}</th>
                    <td class="py-1 border-bottom-1 border-black-alpha-40 lg:text-base md:text-base text-xs">{{ value }}
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script>
export default {
    name: "VerticalRow",
    props: { cell: Object },
    methods: {
        capitalize(value) {
            return value.charAt(0).toUpperCase() + value.substring(1)
        }
    }
}
</script>

<style scoped>
table,
tbody,
th,
td {
    border-collapse: collapse;
}

tr:hover td,
tr:hover th {
    border-bottom-color: #6dd3c8 !important;
}
</style>
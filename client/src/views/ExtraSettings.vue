<template>
    <div class="my-6 justify-content-center">
        <Toast class="z-5" />
        <div class="px-3 lg:px-0 w-full lg:w-7 m-auto grid">
            <h1 class="col-12">Extra settings</h1>
            <div class="flex flex-column gap-2 col-12">
                <h3>Media</h3>
                <label for="media-dir">Media directory</label>
                <InputText id="media-dir" v-model="media" class="col-6" />
            </div>
            <div class="col-12 grid">
                <h3 class="col-12 mb-0 pb-0">LLM Memory</h3>
                <p class="col-12 pt-0">Manage memory history in-memory (Local) or using an external Redis server</p>
                <SelectButton class="choice col-4 w-max" v-model="memoryValue" :options="memoryOptions"
                    :allowEmpty="false"
                    :pt="{ button: { class: 'choice w-min col-6 h-full border-none text-black-alpha-90' } }">
                    <template #option="slotProps">
                        <span v-if="slotProps.index == 1" class="">
                            <img src="/images/redis.svg" alt="redis logo" width="50" height="50">
                        </span>
                        <p v-else class="">{{ slotProps.option }}</p>
                    </template>
                </SelectButton>
                <div class="flex flex-column gap-2 col-6" v-if="isRedis">
                    <label for="redis-url">Redis connection URL</label>
                    <InputText id="redis-url" v-model="memoryUrl" class="col-12" />
                </div>
            </div>
            <div class="col-12 grid">
                <h3 class="col-12 mb-0 pb-0">Database</h3>
                <p class="col-12 pt-0">Manage sources registries either in sqlite or using an external MySQL server</p>
                <SelectButton class="choice col-4 w-max" v-model="dbValue" :options="dbOptions" :allowEmpty="false"
                    :pt="{ button: { class: 'choice w-min col-6 h-full border-none text-black-alpha-90' } }">
                    <template #option="slotProps">
                        <span v-if="slotProps.index == 1">
                            <img src="/images/mysql.png" alt="mysql logo" width="50" height="50">
                        </span>
                        <span v-else>
                            <img src="/images/sqlite.png" alt="sqlite logo" width="50" height="50">
                        </span>
                    </template>
                </SelectButton>
                <div class="grid col-12" v-if="isMysql">
                    <div class="flex flex-column gap-2 grid col-3">
                        <label for="db-user">User</label>
                        <InputText id="db-user" v-model="mysqlData.user" class="col-11" />
                    </div>
                    <div class="flex flex-column gap-2 grid col-3">
                        <label for="db-name">Database name</label>
                        <InputText id="db-name" v-model="mysqlData.db" class="col-11" />
                    </div>
                    <div class="col-6"></div>
                    <div class="flex flex-column gap-2 grid col-3">
                        <label for="db-host">Host</label>
                        <InputText id="db-host" v-model="mysqlData.host" class="col-11" />
                    </div>
                    <div class="flex flex-column gap-2 grid col-3">
                        <label for="db-passw">Password</label>
                        <Password id="db-passw" v-model="mysqlData.password" :feedback="false" class="col-11 p-0" />

                    </div>
                </div>
                <div class="flex flex-column gap-2 col-6" v-else>
                    <label for="sqlite-url">SQLite connection URL</label>
                    <InputText id="sqlite-url" v-model="sqliteUrl" class="col-12" />
                </div>
            </div>
            <Button type="button" label="Save" icon="pi pi-check"
                class="col-offset-4 lg:col-offset-0 col-4 lg:col-2 mt-5" />
        </div>
    </div>
</template>

<script>
import Button from "primevue/button";
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import SelectButton from 'primevue/selectbutton';
import Toast from "primevue/toast";

import {
    fetchResource,
    showError,
    showSuccess
} from "@/utils/client";

export default {
    name: "ExtraSettings",
    components: { Toast, InputText, SelectButton, Button, Password },
    created() {
        fetchResource("/settings/extra").then(settings => {
            this.media = settings.media_dir
            this.memoryUrl = settings.memory.url
            this.memoryValue = settings.memory.kind
            this.dbValue = settings.database.kind
            this.sqliteUrl = settings.database.url
            this.mysqlData = settings.database.data ?? {}
        })
            .catch((error) => showError(error));
    },
    data() {
        return {
            media: '',
            memoryUrl: null,
            memoryValue: "",
            memoryOptions: ["Local", "Redis"],
            dbValue: "",
            dbOptions: ["sqlite", "mysql"],
            sqliteUrl: null,
            mysqlData: {}
        }
    },
    computed: {
        isRedis() {
            return this.memoryValue == "Redis"
        },
        isMysql() {
            return this.dbValue == "mysql"
        }
    }
}
</script>

<style>
.choice.p-button {
    filter: grayscale(100%);
    background-color: grey;
}

.choice.p-highlight {
    filter: grayscale(0%);
    background-color: white !important;
}
</style>
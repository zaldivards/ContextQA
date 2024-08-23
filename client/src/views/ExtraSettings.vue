<template>
    <div class="my-6 justify-content-center">
        <ConfirmDialog :draggable="false" />
        <Toast class="z-5" />
        <div class="px-3 lg:px-0 w-full lg:w-4 m-auto">
            <Message severity="warn" :closable="false">Please make sure your relational DB and Redis instance (if
                needed) are up and
                running</Message>
            <h1 class="mb-0">Extra settings</h1>
            <div class="flex flex-column gap-2">
                <h3 class="mt-0">Media</h3>
                <label for="media-dir">Media directory</label>
                <InputText id="media-dir" v-model="media" class="border-round-lg" />
            </div>
            <div>
                <h3 class="mb-0 pb-0">LLM Memory</h3>
                <p class="pt-0">Manage memory history in-memory (Local) or using an external Redis server</p>
                <div class="flex flex-column gap-2">
                    <SelectButton class="choice w-max flex" v-model="memoryValue" :options="memoryOptions"
                        :allowEmpty="false" :pt="{ button: { class: 'choice border-none text-black-alpha-90' } }">
                        <template #option="slotProps">
                            <span v-if="slotProps.index == 1">
                                <img src="/images/redis.svg" alt="redis logo" width="50" height="50">
                            </span>
                            <p v-else>{{ slotProps.option }}</p>
                        </template>
                    </SelectButton>
                    <div class="flex flex-column gap-2" v-if="isRedis">
                        <label for="redis-url">Redis connection URL</label>
                        <InputText id="redis-url" v-model="memoryUrl" class="border-round-lg" />
                    </div>
                </div>
            </div>
            <div>
                <h3 class="mb-0 pb-0">Database</h3>
                <p class="pt-0">Manage sources registries either in sqlite or using an external MySQL server</p>
                <div class="flex flex-column gap-2">
                    <SelectButton class="choice w-max flex" v-model="dbValue" :options="dbOptions" :allowEmpty="false"
                        :pt="{ button: { class: 'choice border-none text-black-alpha-90' } }">
                        <template #option="slotProps">
                            <span v-if="slotProps.index == 1">
                                <img src="/images/mysql.png" alt="mysql logo" width="50" height="50">
                            </span>
                            <span v-else>
                                <img src="/images/sqlite.png" alt="sqlite logo" width="50" height="50">
                            </span>
                        </template>
                    </SelectButton>
                    <div v-if="isMysql" class="flex flex-column gap-2">
                        <label for="mysql-creds" class="font-medium">MySQL credentials</label>
                        <div class="grid col-12" id="mysql-creds">
                            <div class="flex flex-column gap-2 lg:col-6 md:col-6 col-6">
                                <label for="db-user">User</label>
                                <InputText id="db-user" v-model="mysqlData.user" class="border-round-lg" />
                            </div>
                            <div class="flex flex-column gap-2 lg:col-6 md:col-6 col-6">
                                <label for="db-name">Database</label>
                                <InputText id="db-name" v-model="mysqlData.db" class="border-round-lg" />
                            </div>
                            <div class="flex flex-column gap-2 lg:col-6 md:col-6 col-6">
                                <label for="db-host">Host</label>
                                <InputText id="db-host" v-model="mysqlData.host" class="border-round-lg" />
                            </div>
                            <div class="flex flex-column gap-2 lg:col-6 md:col-6 col-6">
                                <label for="db-passw">Password</label>
                                <Password id="db-passw" v-model="mysqlData.password" :feedback="false"
                                    inputClass="border-round-lg" />

                            </div>
                        </div>
                    </div>
                    <div class="flex flex-column gap-2" v-else>
                        <label for="sqlite-url" class="font-medium">SQLite connection URL</label>
                        <InputText id="sqlite-url" v-model="sqliteUrl" class="col-12 border-round-lg" />
                    </div>
                </div>


            </div>
            <div class="mx-auto lg:mx-0">

                <Button type="button" label="Save" icon="pi pi-check" class="mt-5" rounded @click="setConfig" />
            </div>
        </div>
    </div>
</template>

<script>
import Button from "primevue/button";
import ConfirmDialog from "primevue/confirmdialog";
import Message from 'primevue/message';
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
    components: { Toast, InputText, SelectButton, Button, Password, ConfirmDialog, Message },
    props: { byPassDialog: Boolean },
    created() {
        fetchResource("/settings/extra").then(settings => {
            this.media = settings.media_dir
            this.memoryUrl = settings.memory.url
            this.memoryValue = settings.memory.kind
            this.dbValue = settings.database.kind
            this.sqliteUrl = settings.database.url
            this.mysqlData = settings.database.credentials ?? {}
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
    methods: {
        fetchFunction() {
            fetchResource("/settings/extra", {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    media_dir: this.media,
                    memory: {
                        kind: this.memoryValue,
                        url: this.memoryUrl || undefined
                    },
                    database: {
                        kind: this.dbValue,
                        url: this.dbValue == 'mysql' ? undefined : this.sqliteUrl || undefined,
                        credentials: this.dbValue == 'mysql' ? this.mysqlData || undefined : undefined
                    }
                })
            }).then(response => {
                showSuccess("Successfully updated")
            }).catch((error) => showError(error));
        },
        setConfig() {
            if (this.byPassDialog) {
                this.fetchFunction()
            }
            else {
                this.$confirm.require({
                    message: "Are you sure you want to update the extra settings?",
                    header: "Danger Zone",
                    icon: "pi pi-info-circle",
                    rejectClass: 'p-button-secondary p-button-outlined',
                    acceptClass: 'p-button-danger',
                    accept: this.fetchFunction,
                })
            }
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
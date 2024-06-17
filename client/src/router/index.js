import { createRouter, createWebHistory } from 'vue-router'
import Chat from "@/views/Chat.vue"
import ContextManager from "@/views/ContextManager"
import DocumentQA from "@/views/DocumentQA.vue"
import Home from "@/views/Home"
import ModelSettings from "@/views/ModelSettings"
import SourcesManager from "@/views/SourcesManager"
import VectorStoreSettings from "@/views/VectorStoreSettings"
import ExtraSettings from "@/views/ExtraSettings"
import Status from "@/views/Status"




const routes = [
    {
        path: '/',
        name: 'home',
        component: Home
    },
    {
        path: '/status',
        name: 'status',
        component: Status
    },
    {
        path: '/chat/qa',
        name: 'chat-qa',
        component: DocumentQA
    },
    {
        path: '/chat/conversational',
        name: 'chat-conversational',
        component: Chat
    },
    {
        path: '/sources/ingestion',
        name: 'ingestion',
        component: ContextManager
    },
    {
        path: '/sources/',
        name: 'sources-manager',
        component: SourcesManager
    },
    {
        path: '/settings/models',
        name: 'modelsSettings',
        component: ModelSettings
    },
    {
        path: '/settings/vector-stores',
        name: 'vectorStoreSettings',
        component: VectorStoreSettings,
    },
    {
        path: '/settings/extra',
        name: 'extraSettings',
        component: ExtraSettings,
    },
]

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
})

export default router
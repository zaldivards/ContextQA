import { createRouter, createWebHistory } from 'vue-router'
import Chat from "@/views/Chat.vue"
import DocumentQA from "@/views/DocumentQA.vue"
import ContextManager from "@/views/ContextManager"
import Home from "@/views/Home"



const routes = [
    {
        path: '/',
        name: 'home',
        component: Home
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
    }
]

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
})

export default router
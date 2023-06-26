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
        path: '/chat/document',
        name: 'chat-document',
        component: DocumentQA
    },
    {
        path: '/chat/talk',
        name: 'chat-talk',
        component: Chat
    },
    {
        path: '/context',
        name: 'context',
        component: ContextManager
    }
]

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
})

export default router
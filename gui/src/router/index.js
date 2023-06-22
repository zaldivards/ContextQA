import { createRouter, createWebHistory } from 'vue-router'
import ChatContainer from "@/views/Chat.vue"
import ContextManager from "@/views/ContextManager"
import Home from "@/views/Home"



const routes = [
    {
        path: '/',
        name: 'home',
        component: Home
    },
    {
        path: '/chat',
        name: 'chat',
        component: ChatContainer
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
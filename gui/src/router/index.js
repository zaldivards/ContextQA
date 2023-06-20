import { createRouter, createWebHistory } from 'vue-router'
import ChatContainer from "../views/Chat.vue"
import ContextManager from "../views/ContextManager"


const routes = [
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
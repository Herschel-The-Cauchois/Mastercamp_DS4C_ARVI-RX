import { createRouter, createWebHistory } from 'vue-router'
import MainView from '../views/main.vue'

const routes = [
    {
        path: "/",
        name: "index",
        component: MainView,
        meta: {
            placeholder_data: false
        }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

//Here router guards if needed

export default router
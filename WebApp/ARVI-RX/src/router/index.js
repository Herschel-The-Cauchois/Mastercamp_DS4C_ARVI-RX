import { createRouter, createWebHistory } from 'vue-router'
import MainView from '../views/main.vue'
import DashView from '../views/dashboard.vue'
import ReView from '../views/reviews.vue'
import AnnotationView from '../views/caseannotation.vue'
import LogView from '../views/log_in.vue'

const routes = [
    {
        path: "/",
        name: "index",
        component: MainView,
        meta: {
            requires_auth: false
        }
    },
    {
        path: "/dashboard",
        name: "dashboard",
        component: DashView,
        meta: {
            requires_auth: true
        }
    },
    {
        path: "/cases",
        name: "case annotation",
        component: AnnotationView,
        meta: {
            requires_auth: true
        }
    },
    {
        path: "/evaluate",
        name: "evaluations",
        component: ReView,
        meta: {
            requires_auth: true
        }
    },
    {
        path: "/connect",
        name: "log in",
        component: LogView,
        meta: {
            requires_auth: false
        }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

//Here router guards if needed

export default router
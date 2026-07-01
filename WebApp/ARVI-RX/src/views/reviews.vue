<template>

    <section id="review-table">
        <table>
            <thead>
                <tr>Run n°</tr>
                <tr>True Label</tr>
                <tr>Case Image</tr>
                <tr>Model Used</tr>
                <tr>Confidence</tr>
                <tr>Latency (ms)</tr>
                <tr>Correct ?</tr>
                <tr>Error Type</tr>
                <tr>Comments</tr>
                <tr>Action</tr>
            </thead>
            <tbody>
                <ReviewRow v-for="element in eval_req" :key="element.id" :review="element" @refreshTable="refresh()"/>
            </tbody>
        </table>
    </section>

</template>

<script setup>
    import {ref} from 'vue'
    import {user_login} from '../login_info'
    import ReviewRow from '../components/review.vue'
    import axios from 'axios'

    let eval_req = ref([])

    axios({
        method: "get",
        url: "http://127.0.0.1:8000/eval/"
    }).then(res => {
        console.log(res.data)
        eval_req.value = res.data
    }).catch(err => {
        console.log(err)
    })

    function refresh() {
        axios({
            method: "get",
            url: "http://127.0.0.1:8000/eval/"
        }).then(res => {
            console.log(res.data)
            eval_req.value = res.data
        }).catch(err => {
            console.log(err)
        })
    }

</script>
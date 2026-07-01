<template>

    <table>
        <thead>
            <th>Run n°</th>
            <th>True Label</th>
            <th>Case Image</th>
            <th>Model Used</th>
            <th>Confidence</th>
            <th>Latency (ms)</th>
            <th>Correct ?</th>
            <th>Error Type</th>
            <th>Comments</th>
            <th>Action</th>
        </thead>
        <tbody>
            <ReviewRow v-for="element in eval_req" :key="element.id" :review="element" @refreshTable="refresh()"/>
        </tbody>
    </table>

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
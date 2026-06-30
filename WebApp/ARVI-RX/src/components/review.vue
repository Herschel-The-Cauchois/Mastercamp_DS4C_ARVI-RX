<template>
    <tr>
        <td>{{ review.run_id }}</td>
        <td>{{ review.ground_truth_label }}</td>
        <td>{{ review.img_path }}</td>
        <td>{{ review.model_used }}</td>
        <td>{{ review.confidence }}</td>
        <td>{{ review.latency }}</td>
        <td>
            <select name="iscorrect" id="iscorrect" class="review-input" v-model="is_correct">
                <option value="1">Yes</option>
                <option value="0">No</option>
            </select>
        </td>
        <td><input type="text" class="review-input" v-model="type_error"/></td>
        <td><input type="textarea" class="review-input" v-model="comments"/></td>
        <td>
            <button @click="updateRecord()">Update</button>
            <button @click="deleteRecord()">Delete</button>
        </td>
    </tr>
</template>

<script setup>
    import { ref, watch } from 'vue'
	import axios from 'axios'
	import { useRouter } from 'vue-router'

    const router = useRouter()

    const props = defineProps({
        review: {
            type: Object,
            required: true
        }
    })

    const type_error = ref('')
    const is_correct = ref('')
    const comments = ref('')

    const emit = defineEmits({
        refreshTable: null //i.e. no validation condition
    })

    watch( () => props.review,
    (newReview) => {
        type_error.value = newReview.error_type
        is_correct.value = newReview.is_correct
        comments.value = newReview.comments
    },
    { immediate: true }
    )

    function updateRecord() {
        console.log(type_error.value)
        console.log(is_correct.value)
        console.log(comments.value)
        axios({
            method: "patch",
            url: "http://127.0.0.1:8000/eval/",
            data: {
                id: props.review.id,
                new_correct: is_correct.value,
                new_type: type_error.value,
                new_comment: comments.value
            }
        }).then(res => {
            console.log(res.data)
        }).catch(err => {
            console.log(err)
        })
    }

    function deleteRecord() {
        axios({
            method: "delete",
            url: "http://127.0.0.1:8000/eval/",
            data: {
                id: props.review.id,
                new_correct: is_correct.value,
                new_type: type_error.value,
                new_comment: comments.value
            }
        }).then(res => {
            console.log(res.data)
            emit('refreshTable') //Signals view to refresh redoing get
            console.log("emitted")
        }).catch(err => {
            console.log(err.response)
        })
    }
</script>
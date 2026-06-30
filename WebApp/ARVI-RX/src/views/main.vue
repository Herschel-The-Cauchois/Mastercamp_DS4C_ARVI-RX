<template>

    <main> <!-- Only part of the webapp deserving that tag, since it is the main functionality -->
        <RadioForm v-if="upload_mode" @displayFeedback="feedMode($event)"/> <!-- $event represents event data -->
        <Feedback v-if="!upload_mode" :routed_image="img_disp" :analysis="details"/>
        <button id="reset" v-if="!upload_mode" @click="uploadMode()">Return to upload</button>
    </main>

</template>

<script setup>
import Feedback from '../components/feedback.vue';
import RadioForm from '../components/radioform.vue'
import { ref } from 'vue'

const upload_mode = ref(true) //How to change value based on listening ?

const dummy = {
    "predicted_class": "normal | suspected_opacity | uncertain",
    "justification": "Brief explanation based on visible radiological findings.",
    "visual_evidence": [
    "List of observable visual findings supporting the decision."
    ],
    "confidence": 0.0,
    "warnings": [
    "Important diagnostic limitations, uncertainty factors, or safety alerts."
    ]
}

const img_disp = ref("TruthOrDare.png")
const details = ref(dummy)

function feedMode(e) {
    details.value = e[0] //Transplants event data sent from component to view managing variables
    let tmp_array = e[1].split("/")
    img_disp.value = "http://127.0.0.1:8000/uploads/" + tmp_array[tmp_array.length - 1]
    upload_mode.value = false
}

function uploadMode() {
    upload_mode.value = true
    img_disp.value = "TruthOrDare.png"
    details.value = dummy
}

</script>
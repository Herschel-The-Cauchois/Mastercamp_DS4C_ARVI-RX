<template>
    <Feedback v-if="upload_mode.value" routed_image="TriggerOpTypes.png" :analysis="dummy"/>
</template>

<script setup>
import Feedback from '../components/feedback.vue';
import { ref } from 'vue'

const upload_mode = ref(false)

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

</script>
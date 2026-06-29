<template>
    <div class="feedback">
        <h2>Analysis result</h2>
        <div class="baseinfo">
            <h3>Classification : {{ analysis.predicted_class }}</h3>
            <small>Confidence : {{ analysis.confidence }}</small><br/>
            <img :src="routed_image">
        </div>
        <br/>
        <div class="textual-info">
            <p class="justification">{{ analysis.justification }}</p>
            <p><span class="info-begin">Visual evidences :</span> </p>
            <ul>
                <li v-for="evidence in analysis.visual_evidence"><span class="info">{{ evidence }}. </span></li>
            </ul>
            <p><span class="warning-header">Beware ! </span> <span class="warnings" v-for="warning in analysis.warnings">{{ warning }}</span></p>
        </div>
    </div>
</template>

<script setup>
    //For practical reasons, this component will be a part of the main view once the file has been uploaded, putting directly the response as a prop
    import { ref } from 'vue'
	import axios from 'axios'
	import { useRouter } from 'vue-router'

    const router = useRouter()

    const props = defineProps({
        analysis: {
            type: Object,
            required: true
        },
        routed_image: {
            type: String,
            required: true
        }
    })
</script>
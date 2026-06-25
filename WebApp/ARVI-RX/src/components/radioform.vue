<template>
    <div class="fileform">
        <h2>Send your radiography !</h2>
        <p class="rassurance">Your data is kept private and will stay between you and us.</p>
        <!-- Add small tutorial for the user -->
        <form action="javascript:;" @submit.prevent="tryAnalyze" enctype="multipart/form-data">
            <label for="radio">You may upload your own file.</label>
            <input type="file" id="radio" name="radio" v-on:change="addFile"></input>
            <button type="submit">Analyze</button>
        </form>
        <small id="preemptivewarn">Arvi-RX is a project who does not substitute itself from the diagnosis of a pratician. Always consult your physician for medical advice.</small>
    </div>
</template>

<script setup>
    import { ref } from 'vue'
	import axios from 'axios'
	import { useRouter } from 'vue-router'

    const ImproperFileImport = ref(false) //Shows up error message if addFile fails
    const NoFile = ref(false)
    const ErrorVariables = [ImproperFileImport, NoFile]

    const fileHandler = ref(undefined)

    function addFile(e) {
        const file = e.target.files[0];
        if (file) {
            fileHandler.value = file;
            console.log(fileHandler)
            ImproperFileImport.value = false
        } else {
            ImproperFileImport.value = true
        }
    }

    function tryAnalyze(e) {
        ErrorVariables[1].value = false

        if (fileHandler.value === "" | fileHandler.value === undefined) {
            fileHandler.value = true
            return
        }

        //Need frontend validation of .png extension

        const formSubmission = new FormData()
        formSubmission.append("file", fileHandler.value)

        axios({
            method: "put",
            url: "http://127.0.0.1:8000/analyze/",
            data: formSubmission
        }).then(res => {
            console.log(res.data)
        }).catch(err => {
            console.log(err)
            console.log(err.response)
        })
    }

</script>
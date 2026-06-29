<template>
    <div class="fileform">
        <h2>Send your radiography !</h2>
        <p class="rassurance">Your data is kept private and will stay between you and us.</p>
        <!-- Add small tutorial for the user -->
        <form action="javascript:;" @submit.prevent="tryAnalyze" enctype="multipart/form-data">
            <label for="radio">You may upload your own file : </label>
            <input type="file" id="radio" name="radio" v-on:change="addFile"></input>
            <button type="submit">Analyze</button><br/>
            <small v-if="NoFile" class="error">You do not have uploaded a file. Please do !</small>
            <small v-else-if="NotPermittedFile" class="error">The radiography must be in .png format for our model to analyze it in its smallest details.</small>
            <small v-else-if="Unreadable" class="error">The file sent is either corrupted or unreadable.</small>
            <small v-else-if="UploadError" class="error">The server has encountered an exception managing your file. Please verify your file and retry.</small>
            <small v-else-if="NotUploaded" class="error">Your file somehow wasn't found in the server when contacting the model after uploading. If you see this error, contact us.</small>
            <small v-else-if="ModelNotAvailable" class="error">The currently used model is not available at the moment. Please try later.</small>
            <small v-else-if="Unknown" class="error">An unknown error has occured. Please contact the developers.</small>
        </form>
        <small id="preemptivewarn">Arvi-RX is a project who does not substitute itself from the diagnosis of a pratician. Always consult your physician for medical advice.</small>
    </div>
</template>

<script setup>
    import { ref } from 'vue'
	import axios from 'axios'
	import { useRouter } from 'vue-router'

    const emit = defineEmits({
        displayFeedback: null //i.e. no validation condition
    })

    const ImproperFileImport = ref(false) //Shows up error message if addFile fails, managed out of final validation errors

    const NoFile = ref(false)
    const NotPermittedFile = ref(false) //Trigger frontend validation and with 422 detail backend wise
    const Unreadable = ref(false) //422 Unreadable return
    const UploadError = ref(false) //500 upload error
    const NotUploaded = ref(false) //412 second request error, haven't seen this one yet
    const ModelNotAvailable = ref(false) //All 503 errors, generic message to display while details are logged in console
    const Unknown = ref(false) //Generic message if not registered
    const ErrorVariables = [NoFile, NotPermittedFile, Unreadable, NotUploaded, UploadError, ModelNotAvailable, Unknown]

    const fileHandler = ref(undefined)
    const path_radio = ref(undefined)

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
        ErrorVariables.forEach(elem => elem.value = false)

        if (fileHandler.value === "" || fileHandler.value === undefined) {
            NoFile.value = true
            return
        }

        console.log(fileHandler.value)

        if (!fileHandler.value.name.includes(".png")) {
            NotPermittedFile.value = true
            return
        }

        const formSubmission = new FormData()
        formSubmission.append("file", fileHandler.value)

        console.log("Upload result :")
        axios({
            method: "put",
            url: "http://127.0.0.1:8000/analyze/",
            data: formSubmission //Crude because axios serialization messes up file object uploads, so no pydantic model use to translate back a sent JSON object
        }).then(res => {
            console.log(res.data)
            console.log("Model response :") 
            path_radio.value = "../data/uploads/" + res.data.filename
            axios({
                method: "post",
                url: "http://127.0.0.1:8000/analyze/",
                data: { //HEre JSON used since we made a pydantic model that works to read this !
                    img_path: path_radio.value
                }
            }).then(res => {
                console.log(res.data)
                try {
                    emit('displayFeedback', [res.data, path_radio.value]) //returns info upwards to main view
                    logging_routine(res.data, path_radio.value)
                } catch (e) {
                    console.log("Emit error : " + e)
                }
            }).catch(err => {
                console.log(err.response)
                if (err.status === 412) {
                    NotUploaded.value = true
                } else if (err.status === 503) {
                    ModelNotAvailable.value = true
                } else {
                    Unknown.value = true
                }
            })
        }).catch(err => {
            console.log(err.response)
            if (err.status === 422) {
                if (err.data.detail === "Only png images are accepted for this app.") {
                    NotPermittedFile.value = true
                } else if (err.data.detail === "Unable to read file.") {
                    Unreadable.value = true
                } else {
                    Unknown.value = true
                }
            } else if (err.status === 500) {
                UploadError.value = true
            } else {
                Unknown.value = true
            }
        })
    }

    //routine f° to be called when above is done to log on the server the file upload, result and everything
    function logging_routine(feedback, path) {
        axios({}).then(res => {}).catch(err => {})
    }

</script>
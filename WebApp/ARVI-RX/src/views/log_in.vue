<template>
    <p>Here shall be the logging screen. Credentials will be made internally to restrict the thing to a handful of researchers.</p>

    <section id="log-form">
        <form action="javascript:;" @submit.prevent="tryLog" enctype="multipart/form-data">
            <label for="email">Email</label>
            <input type="text" id="email" name="email" v-model="email"></input><br/>
            <small v-if="EmptyEmail" class="error-msg">Email field is empty.</small><br v-if="EmptyEmail"/>
            <label for="password">Password</label>
            <input type="password" id="password" name="password" v-model="password"></input><br/>
            <small v-if="EmptyPassword" class="error-msg">Password field is empty.</small><br v-if="EmptyPassword"/>
            <small v-if="InternalError" class="error-msg">Internal Server Error. Please try later or contact us.</small>
            <small v-else-if="Forbidden" class="error-msg">Your credentials to this service have expired.</small> <!-- boolean who states if credentials are valid or not, manual stuff -->
            <small v-else-if="NotFound" class="error-msg">Your credentials does not match existing records. Please check the data you have entered.</small>
            <small v-else-if="InvalidPassword" class="error-msg">Password is not valid.</small>
            <small v-else-if="LogInFailed" class="error-msg">The logging in process has not worked correctly. If this persists, contact an administrator.</small><br/>
            <input type="submit" value="Submit"></input>
        </form>
    </section>

</template>

<script setup>

import { useRouter } from 'vue-router'
import axios from 'axios'
import VueJwtDecode from 'vue-jwt-decode'
import { ref } from 'vue'
import {user_login, LoadUserLogin} from '../login_info'

const email = defineModel('email')
const password = defineModel('password')
const router = useRouter()

const InternalError = ref(false)
const Forbidden = ref(false)
const NotFound = ref(false)
const InvalidPassword = ref(false)
const EmptyPassword = ref(false)
const EmptyEmail = ref(false)
const LogInFailed = ref(false)
var ErrorVariables = [InternalError, Forbidden, NotFound, InvalidPassword, EmptyPassword, EmptyEmail, LogInFailed]

function tryLog() {
    console.log(email.value)
    ErrorVariables.forEach((elem) => elem.value = false) //Sets to false every error flag before attempting new request

    if (email.value === "" | email.value === undefined) {
        EmptyEmail.value = true
        return
    }
    if (password.value === "" | password.value === undefined) {
        EmptyPassword.value = true
        return
    }

    axios({
        method: "post",
        url: "http://127.0.0.1:8000/users/",
        data: { email: email.value, password: password.value},
    }).then(res => {
        console.log(res.data);
        if (localStorage.getItem('user') != null) {
            localStorage.removeItem("user") //Removes token if was already logged in, to prevent simultaneous sessions
        }
        localStorage.setItem("user", res.data.token)
        try {
	        LoadUserLogin()
            router.push("/dashboard")
        } catch(error) {
            LogInFailed.value = true
        }
    }).catch (err => {
        console.error(err);
        console.log(err.response.data)
        console.log(err.response.status)
        switch (err.response.status) {
            case 500:
                InternalError.value = true
                break
            case 404:
                NotFound.value = true
                break
            case 401:
                InvalidPassword.value = true
                break
            case 403:
                Forbidden.value = true
                break
            default:
                console.error("Invalid HTTP response status")
                LogInFailed.value = true
                break
        }
    })
}

</script>
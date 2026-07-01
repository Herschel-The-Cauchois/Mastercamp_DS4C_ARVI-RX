<template>
    <header>
        <h1>MedRad</h1>
        <nav>
            <RouterLink to="/connect" v-if="!user_login.isLoggedIn"> <img src="../assets/login.svg" class="icon"> <span class="slide-in">Log In</span></RouterLink>
            <!-- Part for when logged in -->
            <RouterLink to="/dashboard" v-if="user_login.isLoggedIn"> <img src="../assets/chart-pie.svg" class="icon"> <span class="slide-in">Dashboard</span></RouterLink>
            <RouterLink to="/cases" v-if="user_login.isLoggedIn"> <img src="../assets/pencil.svg" class="icon"> <span class="slide-in">Annotate Cases</span></RouterLink>
            <RouterLink to="/evaluate" v-if="user_login.isLoggedIn"> <img src="../assets/note-plus.svg" class="icon"> <span class="slide-in">Evaluate Runs</span></RouterLink>
            <RouterLink to="/" v-if="user_login.isLoggedIn" @click="UnloadUserLogin()"> <img src="../assets/logout.svg" class="icon"> <span class="slide-in">Disconnect</span></RouterLink> 
            <RouterLink to="/"> <img src="../assets/home.svg" class="icon"> <span class="slide-in">Home</span> </RouterLink>
        </nav>
    </header>
</template>

<script setup>
    import {user_login, UnloadUserLogin} from '../login_info'
    import {useRoute} from 'vue-router'



</script>
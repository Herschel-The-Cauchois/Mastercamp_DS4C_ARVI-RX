<template>

  <Header/>

  <RouterView/>

  <Footer/>

</template>


<script setup>

  import HelloWorld from './components/HelloWorld.vue'
  import Header from './components/header.vue'
  import Footer from './components/footer.vue'
  import { RouterLink } from 'vue-router';
  import { useRouter } from 'vue-router'
  import { ref } from 'vue'

  const router = useRouter()

</script>
<template>

  <RouterView/>

</template>


<script setup>

  import HelloWorld from './components/HelloWorld.vue'
  import { RouterLink } from 'vue-router';
  import { useRouter } from 'vue-router'
  import { ref } from 'vue'

  const router = useRouter()

</script>
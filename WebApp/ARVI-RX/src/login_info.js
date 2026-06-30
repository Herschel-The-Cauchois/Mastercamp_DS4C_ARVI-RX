import VueJwtDecode from 'vue-jwt-decode'
import { defineProps, ref } from 'vue'

var user_login = ref({isLoggedIn: false, username: "None", id: "None"});

function LoadUserLogin() {
	// get token from localstorage
	let token = localStorage.getItem("user");
	try {
		//decode token here and attach to the user object
		let decoded = VueJwtDecode.decode(token);
		user_login.value = decoded;
		user_login.value.isLoggedIn = true;
		console.log('user is logged in')
	} catch (error) {
		// return error in production env
		console.log(error, 'user is not logged in')
	}
}

function UnloadUserLogin() {
	user_login.value = {isLoggedIn: false, isAdmin: false, isProvider:false, username: "None", id: "None"};
}

export {user_login, LoadUserLogin, UnloadUserLogin}
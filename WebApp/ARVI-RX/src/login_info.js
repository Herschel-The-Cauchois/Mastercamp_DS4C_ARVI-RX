import { jwtDecode } from 'jwt-decode'
import { defineProps, ref } from 'vue'

var user_login = ref({isLoggedIn: false, id: "None"});

function LoadUserLogin() {
	// get token from localstorage
	let token = localStorage.getItem("user");
	try {
		//decode token here and attach to the user object
		let decoded = jwtDecode(token);
		user_login.value = decoded;
		user_login.value.isLoggedIn = true;
		console.log('user is logged in')
	} catch (error) {
		// return error in production env
		console.log(error, 'user is not logged in')
	}
}

function UnloadUserLogin() {
	user_login.value = {isLoggedIn: false, id: "None"};
	try {
		localStorage.removeItem("user")
	} catch(error) {
		console.log(error)
	}
}

export {user_login, LoadUserLogin, UnloadUserLogin}
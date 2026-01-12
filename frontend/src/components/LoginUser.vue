<template>
    <div class="d-flex justify-content-center align-items-center vh-100">
        <div class="p-4 border rounded shadow-sm" style="min-width: 300px;">
        <h2 class="text-center">Login</h2><br>
            <form @submit.prevent="loginUser">
                <div>
                    <label for="username"> Username : </label>
                    <input type="text" id="username" v-model="username" required> 
                </div>
                <br>
                <div id="Password">
                    <label for="password"> Password : </label>
                    <input type="password" id="password" v-model="password" required>
                </div>
                <br>
                <router-link to="/signup">
                    Create Account ?
                </router-link> &nbsp;&nbsp;
                <button type="submit" class="login_button"> Login </button> 
            </form>
            <div v-if="errorMessage">
                {{ errorMessage }}
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default{
    data(){
        return{
            username:'',
            password:'',
            errorMessage:''
        }

    },
    methods:{
        async loginUser(){                                            // async under the hood ( await is acting like .then)
            try{
                const response = await axios.post("http://127.0.0.1:5000/api/signin", {
                    username : this.username,
                    password : this.password
                });
                
                const {access_token,user} = response.data;

                localStorage.setItem('user',JSON.stringify(user));   // Converting into string (json), for further use
                localStorage.setItem('access_token', access_token);

                if (user.role === 'admin'){
                    this.$router.push('/adminHome')
                }else{
                    this.$router.push(`/userHome/${this.username}`)
                }
            }
            catch(error){
                if(error.response){
                    this.errorMessage = error.response.data.message;
                }
                else{
                    this.errorMessage = 'Login failed try again';
                }
        }
    }
}
}
</script>

<style>

.submit{
    align-items: center;
}

.login_button{
    padding:15px;
    padding-top: 10px;
    padding-bottom:10px;
}

.text-center{
    font-family: Georgia, 'Times New Roman', Times, serif;
}

.p-4{
    background-color: rgb(201, 179, 226);
}
</style>
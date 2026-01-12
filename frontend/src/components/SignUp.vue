<template>
    <div class="d-flex justify-content-center align-items-center vh-100">
        <div class="p-4 border rounded shadow-sm" style="min-width: 300px;">
        <h2 class="text-center mb-4"> SignUp </h2>
            <form @submit.prevent="signUpUser">
                <div>
                    <label for="email-id"> Email-id: </label>
                    <input type="text" id="email-id" v-model="emailid" required> 
                </div>
                <div>
                    <label for="username"> Username: </label>
                    <input type="text" id="username" v-model="username" required> 
                </div>
                <div id="Password">
                    <label for="password"> Password : </label>
                    <input type="password" id="password" v-model="password" required>
                </div>
                <div>
                    <label for="fullname"> Full Name : </label>
                    <input type="text" id="fullname" v-model="fullname" required> 
                </div>
                <div>
                    <label for="address"> Address : </label>
                    <input type="text" id="address" v-model="address" required> 
                </div>
                <div>
                    <label for="pincode"> Pincode : </label>
                    <input type="number" id="pincode" v-model="pincode" required> 
                </div>
                <br>
                <router-link to="/login">
                    Back to Signin 
                </router-link> &nbsp;&nbsp;
                <button type="submit" class="submit"> SignUp </button> 
                
            </form>
            <div v-if="Message">
                {{ Message }}
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'

export default{

    data(){
        return{
            emailid:'',
            username:'',
            password:'',
            fullname:'',
            address:'',
            pincode: '',
            Message:''
        }
    },
    methods:{
        async signUpUser(){
            try{
                if (!this.pincode || isNaN(this.pincode)) {
                    this.Message = "Please enter a valid pincode";
                    return;
                }

                const response = await axios.post('http://127.0.0.1:5000/api/signup',{
                    email_id : this.emailid,
                    username : this.username,
                    password: this.password,
                    full_name: this.fullname,
                    address: this.address,
                    pincode: this.pincode
                });

                if(response.data.message){
                    this.Message = response.data.message
                    this.$router.push('/login')
                }
            }
            catch(error){
                if(error.response){
                    this.Message = error.response.data.message;
                }
                else{
                    this.Message = 'SignUp failed try again';
                    console.log(error);
                }
            }
            


        }
    }
}

</script>

<style>

input{
    top: 5px;
    right: 10px;
}

</style>
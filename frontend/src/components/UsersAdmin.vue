<template>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css">
    <p class="Registered_Users">Registered Users</p>
    <table border="3" class="user_details">
        <thead>
            <tr>
                <th id="id">User ID</th>
                <th id="email_id">Email Id</th>
                <th>Full Name</th>
                <th>Address</th>
                <th>Pincode</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="row in data"
                :key="`${row.id}-${row.email_id}-${row.full_name}-${row.address}-${row.pincode}`">
                <td >
                    <input id="id" v-model="row.id" readonly style="cursor:pointer" required/>
                </td>
                <td>
                    <input id="email_id" v-model="row.email_id" readonly style="cursor:pointer" required/>
                </td>
                <td>
                    <input v-model="row.full_name" readonly style="cursor:pointer" required/>
                </td>
                <td>
                    <input v-model="row.address" readonly style="cursor:pointer" required/>
                </td>
                <td>
                    <input v-model="row.pincode" readonly style="cursor:pointer" required/>
                </td>
            </tr>
        </tbody>
    </table>

</template>

<script>
import axios from 'axios'

export default{
    data(){
        return{
            data:null
        }    
    },
    created(){
        this.userListData();
    },
    methods:{
        async userListData(){
            const access_token = localStorage.getItem("access_token");
            axios.get("http://127.0.0.1:5000/api/userInfo",{
                headers:{
                    Authorization: `Bearer ${access_token}`
                }
            }).then(res => {
                this.data = res.data;
            })  
        }
    }
}
</script>

<style>

.Registered_Users{
  background-color: #7fffd4; 
  color: #111;               
  padding: 12px 600px;
  border-radius: 40px;
  text-align: center;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 1.5rem;
  font-weight: 600;
  width: fit-content;
  margin: 40px auto;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  letter-spacing: 1px;
  transition: all 0.3s ease-in-out;
}

.Registered_Users:hover {
  background-color: #5efcc7;
  transform: scale(1.03);
  cursor: pointer;
}

.user_details {
  width: 90%;
  margin: 30px auto;
  background: white;
  box-shadow: 0 3px 12px rgba(0,0,0,0.1);
  border-bottom-left-radius: 40px;
  border-top-right-radius: 40px;
  border-top-left-radius: 0px;
  border-bottom-right-radius: 0px;
  overflow: hidden;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.user_details th {
  background-color: #3bdca6;
  color: white;
  padding: 12px;
  text-align: left;
  text-decoration:solid;
}

.user_details td {
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.user_details input {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 10px;
  background: #fafafa;
  transition: all 0.2s ease;
}

</style>
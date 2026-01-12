<template>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css">
    <form @submit.prevent="searchData">
        &nbsp;&nbsp;&nbsp;
        <label for="search" class="label"> Select a category </label>
        <select name="search" id="search" v-model="selected">
            <option value="location" selected> Location </option>
            <option value="pincode"> Pincode </option>
        </select>
        &nbsp;&nbsp;
        <input type="search" placeholder="Search" aria-label="Search" v-model="searched" class="search-input">&nbsp;&nbsp;
        <button class="btn btn-outline-success my-2 my-sm-0" @click="SearchSubmit()">Search</button>
    </form>
    
    <div v-if="!this.message">
        <table border="3" class="lot_details">
            <thead>
                <tr>
                    <th id="id">Lot ID</th>
                    <th id="address">Address</th>
                    <th id="availables">Availability</th>
                    <th id="action">Action</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="row in lot_info"
                    :key="`${row.id}-${row.address}-${row.availables}-${row.action}`">
                    <td >
                        <input id="id" v-model="row.id" readonly style="cursor:pointer" required/>
                    </td>
                    <td>
                        <input id="address" v-model="row.address" readonly style="cursor:pointer" required/>
                    </td>
                    <td>
                        <input id="availables" v-model="row.availables" readonly style="cursor:pointer" required/>
                    </td>
                    <td>
                        <button class="book" @click="Book(row.id)"> Book </button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    <div v-else>
        <div class="message">
            {{this.message}}
        </div>
    </div>
    <div class="users">
        <div class="content">
            <router-view />
        </div>
    </div>
</template>

<script>
import axios from 'axios'

export default{
    data(){
        return{
            selected: null,
            searched: null,
            lot_info:null,
            message:null,
            selectedLotId:null
        }    
    },
    watch: {
        $route() {
            this.SearchSubmit();
        }
    },
    methods:{
        SearchSubmit(){
            this.message = null;
            const access_token = localStorage.getItem("access_token");
            axios.get("http://127.0.0.1:5000/api/UserSearch",{
                params:{
                    selected: this.selected,
                    searched: this.searched
                },
                headers:{
                    Authorization: `Bearer ${access_token}`
                }
            }).then(res => {
                this.lot_info = res.data;
                console.log(this.lot_info)
                if(this.lot_info?.message){
                    this.message = this.lot_info.message;
                    console.log(this.message)
                }
            })  
        },
        async Book(id){
            this.selectedLotId = id;
            await this.$router.push({
                path: `/userSearch/userBook/${this.selectedLotId}`
            });
        }
    }
}
</script>

<style>

.label{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    text-align: center; 
}

form .search-input{
  width: 700px;
  background-color: rgb(56, 48, 69); 
  color: white;               
  padding: 3px 300px;
  border-radius: 40px;
  text-align: center;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 1.18rem;
  font-weight: 600;
  margin: 40px auto;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  letter-spacing: 1px;
  transition: all 0.3s ease-in-out;
}

.book{
    padding: 15%;
    padding-top: 10%;
    padding-bottom: 10%;
}

select {
  padding: 10px 15px;
  border: 1px solid #ccc;
  border-radius: 40px;
  background-color: #f9f9f9;
  font-size: 1.18rem;
  cursor: pointer;
  transition: border-color 0.3s, box-shadow 0.3s;
}

select:focus {
  border-color: #007BFF;
  box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
  outline: none;
}

.lot_details {
  width: 90%;
  margin: 30px auto;
  background: white;
  box-shadow: 0 3px 12px rgba(0,0,0,0.1);
  border-top-left-radius: 0px;
  border-bottom-right-radius: 0px;
  overflow: hidden;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.lot_details th {
  background-color: #3bdca6;
  color: white;
  padding: 12px;
  text-align: left;
  text-decoration:solid;
}

.lot_details td {
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.lot_details input {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 10px;
  background: #fafafa;
  transition: all 0.2s ease;
}

.message{
    color: blueviolet;
    text-align: center; 
}
</style>
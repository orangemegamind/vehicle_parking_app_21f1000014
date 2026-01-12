<template>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css">
    <form @submit.prevent="searchData">
        &nbsp;&nbsp;&nbsp;
        <label for="search" class="label"> Select a category </label>
        <select name="search" id="search" v-model="selected">
            <option value="user_id" selected> User Id </option>
            <option value="lot_id"> Lot Id </option>
            <option value="spot_id"> Spot Id </option>
            <option value="veh_no"> Vehicle Number </option>
            <option value="loc_name"> Location Name </option>
            <option value="loc_add"> Location Address </option>
            <option value="pincode"> Pincode </option>
            <option value="no_of_spots"> No. of Spots </option>
            <option value="price"> Price </option>
        </select>
        &nbsp;&nbsp;
        <input type="search" placeholder="Search" aria-label="Search" v-model="searched" class="search-input">&nbsp;&nbsp;
        <button class="btn btn-outline-success my-2 my-sm-0" @click="SearchSubmit()">Search</button>
    </form>
    <br><br><br><br>
    <div class="parking-container">
        <div class="lot-data" v-if="spots_info && spots_info.length" >
            <div v-for="lot in spots_info" :key="lot.lot_id" class="parking_lot">
                <h3>{{ lot.lot_id }}</h3>
            
                <div class="actions">
                    <button @click="OpenEdit(lot.lot_id)" class="Edit-btn"> Edit </button>
                    <button @click="DeleteEdit(lot.lot_id)" class="Delete-btn"> Delete </button>
                </div>

                <p class="occupied-status"> 
                    (Occupied Spots: {{ lot.Occupied.length }} / {{ lot.Total }})
                </p>

                <div class="grid">
                    <span 
                    v-for="spot in [...lot.Available.map(id => ({ id, type: 'A' })), 
                                    ...lot.Occupied.map(id => ({ id, type: 'O' }))].sort((a, b) => a.id - b.id).slice(0,16)"
                    :key="spot.id"
                    :class="['spot', spot.type === 'A' ? 'available' : 'occupied']"
                    >
                        <button @click="ViewSpot(spot.id)" class="viewSpot">{{ spot.id }}</button>
                    </span>
                    
                </div>
                <div v-if="(lot.Available.length + lot.Occupied.length) > 16" class="more">
                    <button @click="openSubscreen(lot.lot_id)" class="my-btn">
                        <i class="bi bi-three-dots"></i>
                    </button>
                </div>
            </div>  
        </div>
    </div>
    <div v-if="subscreen" class="overlay">
        <div class="popup">
            <div class="grid">
                <template v-for="lot in spots_info" :key="lot.lot_id">
                    <div v-if="sel_screen==lot.lot_id"  class="parking_lot_pop_up">
                        <p> Occupied Spots : {{ lot.Occupied.length }} / {{ lot.Total }} </p> <br>
                        <button @click="Close()" class="close-btn">
                            <i class="bi bi-x-square"></i>
                        </button>
                        
                        <span 
                        v-for="spot in [...lot.Available.map(id => ({ id, type: 'A' })), 
                                        ...lot.Occupied.map(id => ({ id, type: 'O' }))].sort((a, b) => a.id - b.id)"
                        :key="spot.id"
                        :class="['spot', spot.type === 'A' ? 'available' : 'occupied']"
                        >
                            <button @click="ViewSpot(spot.id)" class="viewSpot">{{ spot.id }}</button>
                        </span>
                    </div>
                    <div v-else>
                    </div>
                </template>
            </div>
        </div>
    </div>
    <div class="message">
        {{this.message}}
    </div>
    <div class="admin">
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
            spots_info:[],
            subscreen : false,
            sel_screen : null,
            message:null
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
            axios.get("http://127.0.0.1:5000/api/Search",{
                params:{
                    selected: this.selected,
                    searched: this.searched
                },
                headers:{
                    Authorization: `Bearer ${access_token}`
                }
            }).then(res => {
                this.spots_info = res.data;
                if(this.spots_info?.message){
                    this.message = this.spots_info.message;
                    console.log(this.message)
                }
            })  
        },
        openSubscreen(lotId){
            this.subscreen = true;
            this.sel_screen = lotId;
        },
        async OpenEdit(id){
            this.selectedLotId = id;
            await this.$router.push({
                path: `/adminSearch/edit/${this.selectedLotId}`,
                query: {sourceScreen:'AdminSearch'}
            });
        },
        DeleteEdit(id){
            this.selectedLotId = id;
            this.$router.push({ 
                path:`/adminSearch/delete/${this.selectedLotId}`,
                query:{sourceScreen:'AdminSearch'}
            });
        },
        ViewSpot(id){
            this.selectedSpotId = id;
            this.$router.push({
                path: `/adminSearch/viewSpot/${this.selectedSpotId}`,
                query:{sourceScreen:'AdminSearch'}
            });
        },
        Close(){
            this.subscreen = false;
            this.sel_screen = null;
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

.message{
    color: blueviolet;
    text-align: center; 
}

.lot-data{
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: center;
}
</style>
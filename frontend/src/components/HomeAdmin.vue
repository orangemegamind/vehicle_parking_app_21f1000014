<template>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css">
    <p class="ParkingName">Parking Lots</p>
  
    <div class="parking-container">
        <div class="lot-data" v-if="spots_info.length > 0">
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
            <div class="Add-lot" >
                <button class="add-lot" @click="this.$router.push('/adminHome/addLot')">+ Add Lot</button>
            </div>
        </div>
        <div class="Add-lot" v-else>
            <button class="add-lot" @click="this.$router.push('/adminHome/addLot')">+ Add Lot</button>
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
            selectedLotId: null,
            selectedSpotId: null,
            spots_info:[],
            subscreen : false,
            sel_screen : null
        }
    },
    created(){
        this.UserList();
    },
    watch: {
        $route() {
            this.UserList();
        }
    },
    methods:{
        OpenEdit(id){
            this.selectedLotId = id;
            console.log('HomeEdit')
            this.$router.push({
                path: `/adminHome/edit/${this.selectedLotId}`,
                query: {sourceScreen:'HomeAdmin'}
        });
        },
        DeleteEdit(id){
            this.selectedLotId = id;
            this.$router.push({ 
                path:`/adminHome/delete/${this.selectedLotId}`,
                query:{sourceScreen:'HomeAdmin'}
            });
        },
        ViewSpot(id){
            this.selectedSpotId = id;
            this.$router.push({
                path: `/adminHome/viewSpot/${this.selectedSpotId}`,
                query:{sourceScreen:'HomeAdmin'}
            });
        },
        UserList(){
            const access_token = localStorage.getItem("access_token");

            axios.get("http://127.0.0.1:5000/api/parkingLotInfo",{
                headers:{
                    Authorization: `Bearer ${access_token}`
                }
            })
            .then(response => {
                this.spots_info = response.data;
            })
        },
        openSubscreen(lotId){
            this.subscreen = true;
            this.sel_screen = lotId;
        },
        Close(){
            this.subscreen = false;
            this.sel_screen = null;
        }
    }
}
</script>

<style>

.ParkingName{
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

.ParkingName:hover {
  background-color: #5efcc7;
  transform: scale(1.03);
  cursor: pointer;
}

.Lot_Cell{
    background-color: rgb(0, 191, 255);
    border-radius: 20%;
    padding: 7px;
}

button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 3px 10px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  background-color: #3498db; 
  color: #fff;
}

button:hover {
  background-color: #2980b9;
  transform: translateY(-1px);
}

button.viewSpot{
  color:black;
  display: inline-flex;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  background-color: transparent;
}

button.viewSpot:hover{
  color:black;
  display: inline-flex;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  background-color: transparent;
}

.occupied{
    background-color: rgb(231, 102, 102);
    border-color: black;
    border-radius: 15%;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 0.70rem;
    width: fit-content;
    color: black;
}

.occupied:hover{
    background-color: rgb(255, 0, 0);
    border-color: black;
    border-radius: 15%;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 0.70rem;
    width: fit-content;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    transform: translateY(-1px);
    color: black;
}

.available{
    background-color: rgb(110, 219, 79);
    border-color: black;
    border-radius: 15%;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 0.70rem;
    width: fit-content;
    color: black;
}

.available:hover{
    background-color: rgb(0, 220, 7);
    border-color: black;
    border-radius: 15%;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 0.70rem;
    width: fit-content;
    transform: translateY(-1px);
    color: black;
}

.spot {
  display: inline-block;
  text-align: center;
  border: 2px solid #1f1f1f;
  margin: 3px;
}

.lot-data{
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: center;
}

.add-lot{
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    justify-content: center;
    border-radius:12%;
    height: 320px;
    width: 300px;
}

.parking_lot {
  padding: 15px;
  border-radius: 15px;
  width: 300px;
  text-align: center;
  background-color: #fff;
}

.parking_lot:hover {
  padding: 15px;
  border-radius: 15px;
  width: 300px;
  text-align: center;
  background-color: #d8d8d8;
  transform: translateY(-1px);
}

.overlay {
  position: fixed;
  top: 0; left: 0;
  width:100%; height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 700;  
}

.popup {
  background: white;
  width: 800px;       
  height: 300px;
  padding: 20px;
  border-radius: 8px;
  overflow-y: auto;   
}

.parking_lot_pop_up {
  padding: 15px;
  border-radius: 15px;
  width: 700px;
  text-align: center;
  position: relative;
}

.Edit-btn{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 3px 10px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  background-color: #3498db; 
  color: #fff;
  margin-right: 10px;
}

.Edit-btn:hover {
  background-color: #2980b9;
  transform: translateY(-1px);
  margin-right: 10px;
}

.Delete-btn{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 3px 10px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  background-color: #ec3d45; 
  color: #fff;
}

.Delete-btn:hover {
  background-color: #df0e0e;
  transform: translateY(-1px);
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease-in-out;
  z-index: 10;
  background-color: None;
}

.close-btn:hover {
  color: #e74c3c;
  transform: scale(1.1);
}

</style>
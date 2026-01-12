<template>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css">
    <div class="book-overlay">
        <div class="pop-up">
            <p class="Release_Parking_Spot"> Release the Parking Spot</p>
            <form @submit.prevent="lotEdit" class="edit-form">
                <div class="form-group">
                    <Label for="spot_id">Spot ID: </Label>
                    <input type="number" id="spot_id" v-model="spot_id" readonly required>
                </div>
                <div class="form-group">
                    <Label for="veh_no">Vehicle No.: </Label>
                    <input type="string" id="veh_no" v-model="vehicle_no" readonly required>
                </div>
                <div class="form-group">
                    <Label for="park_time">Parking Time: </Label>
                    <input type="text" id="park_time" v-model="parking_time" readonly required>
                </div>
                <div class="form-group">
                    <Label for="release_time">Releasing Time: </Label>
                    <input type="string" id="release_time" v-model="leaving_time" readonly required>
                </div>
                <div class="form-group">
                    <Label for="cost">Total Cost: </Label>
                    <input type="string" id="cost" v-model="parking_cost" readonly required>
                </div>
                
                <button type="release" class="release" @click="Release()"> Release </button>
                <button type="button" class="cancel" @click="this.$router.push(`/userHome/${this.username}`)"> Cancel </button>
            </form>
        </div>
        <div class="pop-up-mesg" v-if="this.message">
            <div class="pop-up-box">
                {{ this.message }}
                <button type="button" class="cancel" @click="this.$router.push(`/userHome/${this.username}`)"> Ok </button>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'

export default{
    props:{
        username:{
            type:String,
            required: true
        },
        spotId:{
            type:Number,
            required: true
        },
        vehNo:{
            type:String,
            required:true
        }
    },
    data(){
        return{
            spot_id:null,
            vehicle_no:null,
            parking_time:null,
            leaving_time:null,
            parking_cost:null,
            message:null
        }
    },
    created(){
        try{
            const access_token = localStorage.getItem("access_token");
            axios.get(`http://127.0.0.1:5000/api/reserveParkingSpot`,{
                params:{
                    spot_id: parseInt(this.spotId),
                    veh_no: this.vehNo
                },
                headers:{
                    Authorization: `Bearer ${access_token}`
                }
            }).then(res => {
                const data = res.data;
                this.spot_id = data.spot_id;
                this.vehicle_no = data.vehicle_no;
                this.parking_time = data.parking_time;
                this.leaving_time = data.leaving_time;
                this.parking_cost = data.parking_cost;

                if(data?.message){
                    this.message = data.message;
                }
            });
        }
        catch (error)
        {
            console.log("Error is :", error);
        }
    },
    methods:{
        Release(){
            const access_token = localStorage.getItem("access_token");
            axios.delete(`http://127.0.0.1:5000/api/reserveParkingSpot`,
                {
                    data:{
                        spot_id : parseInt(this.spotId),
                        veh_no: this.vehicle_no
                    },
                    headers:{
                        Authorization: `Bearer ${access_token}`
                    }
                }
            ).then(res=>{
                const data = res.data;
                if(data?.message){
                    this.message = data.message;
                }
            })
        }
    }
}
</script>


<style>

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
  width: 100%; 
}

.form-group {
  display: flex;
  justify-content: space-between; 
  width: 100%;
}

label {
  margin-right: 10px;
  white-space: nowrap; 
}

input {
  width: 200px;
  padding: 5px;
  text-align: left;
}

.Release_Parking_Spot{
  background-color: #7fffd4; 
  color: #111;               
  padding: 12px 150px;
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

.book-overlay{
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.pop-up-mesg{
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.pop-up,
.pop-up-box{
  background: white;
  padding: 20px;
  border-radius: 10px;
  min-width: 400px;
  position: relative;
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

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

</style>
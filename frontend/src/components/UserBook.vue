<template>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css">
    <div class="book-overlay">
        <div class="pop-up">
            <p class="Book_Parking_Spot"> Book Parking Spot </p>
            <form @submit.prevent="lotEdit" class="edit-form">
                <div class="form-group">
                    <Label for="spot_id">Spot ID: </Label>
                    <input type="text" id="spot_id" v-model="spot_id" readonly required>
                </div>
                <div class="form-group">
                    <Label for="lot_id">Lot ID: </Label>
                    <input type="text" id="lot_id" v-model="lot_id" readonly required>
                </div>
                <div class="form-group">
                    <Label for="user_id">User ID: </Label>
                    <input type="number" id="user_id" v-model="user_id" readonly required>
                </div>
                <div class="form-group">
                    <Label for="veh_no">Vehicle No.: </Label>
                    <input type="string" id="veh_no" v-model="veh_no" required>
                </div>
                
                <button type="reserve" class="reserve" @click="Reserve()"> Update </button>
                <button type="button" class="cancel" @click="this.$router.push('/userSearch')"> Cancel </button>
            </form>
        </div>
        <div class="pop-up-mesg" v-if="pop_mesg">
            <div class="pop-up-box">
                {{ pop_mesg }}
                <button type="button" class="cancel" @click="this.$router.push('/userSearch')"> Ok </button>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'

export default{
    props:{
        lotId:{
            type:Number,
            required: true
        }
    },
    data(){
        return{
            spot_id:null,
            lot_id:null,
            user_id:null,
            veh_no:null,
            pop_mesg:null
        }
    },
    created(){
        try{
            const access_token = localStorage.getItem("access_token");
            axios.get(`http://127.0.0.1:5000/api/BookSpot`,{
                params:{
                    lot_id: parseInt(this.lotId)
                },
                headers:{
                    Authorization: `Bearer ${access_token}`
                }
            }).then(res => {
                const data = res.data;
                this.spot_id = data.spot_id
                this.lot_id = this.lotId;
                this.user_id = data.user_id;
            });
        }
        catch (error)
        {
            console.log("Error is :", error);
        }
    },
    methods:{
        Reserve(){
            const access_token = localStorage.getItem("access_token");
            axios.post(`http://127.0.0.1:5000/api/BookSpot`,{
                    lot_id : parseInt(this.lotId),
                    spot_id : this.spot_id,
                    vehicle_no: this.veh_no
                }, 
                {
                    params:{
                        lot_id : parseInt(this.lotId)
                    },
                    headers:{
                        Authorization: `Bearer ${access_token}`
                    }
                }
            ).then(res=>{
                const data =res.data;
                this.pop_mesg = data.message; 
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

.Book_Parking_Spot{
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
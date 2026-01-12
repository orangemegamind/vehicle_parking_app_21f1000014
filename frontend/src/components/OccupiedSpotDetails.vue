<template>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css">
      <div class="edit-overlay">
          <div class="pop-up">
              <p class="Occupied_Spot_Details"> Occupied Spot Details </p>
              <form @submit.prevent="ViewSpot" class="view-form">
                <div class="form-group">
                  <label for="spot_id">Spot Id : </label>
                  <input type="number" id="spot_id" v-model="spot_id" readonly style="cursor:pointer" required>
                </div> 
                <div class="form-group">
                  <label for="user_id">User Id : </label>
                  <input type="number" id="user_id" v-model="user_id" readonly style="cursor:pointer" required>
                </div> 
                <div class="form-group">
                  <label for="veh_no">Vehicle No. : </label>
                  <input type="string" id="veh_no" v-model="veh_no" readonly style="cursor:pointer" required>
                </div> 
                <div class="form-group">
                  <label for="date">Date/Time of Parking : </label>
                  <input type="string" id="date" v-model="date" readonly style="cursor:pointer" required>
                </div> 
                <div class="form-group">
                  <label for="price">Est. Parking Cost : </label>
                  <input type="number" id="price" v-model="price" readonly style="cursor:pointer" required>
                </div> 
                <button type="button" class="cancel" @click="cancel"> Cancel </button>
              </form>
          </div>

        <div class="overlay" v-if="message">
          <div class="pop-up-box">
              {{ message }}
              <button type="button" class="cancel" @click="cancel"> Ok </button>
          </div>
        </div>
      </div>    
</template>

<script>
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router';

export default{
    props:{
      spotId:{
        type: Number,
        required: true
      },
      lotId:{
        type: Number,
        required: true
      },
      statuss:{
        type: String,
        reuired: true
      }
    },
    setup(){
        const route = useRoute()
        const router = useRouter()

        const sourceScreen = route.query.sourceScreen;


        const cancel = () => {
          console.log("inside setup")
            if (sourceScreen === 'AdminSearch') 
            {
                console.log("in search")
                router.push('/adminSearch');
            }
            else if (sourceScreen === 'HomeAdmin')
            {
                console.log("in home")
                router.push('/adminHome');
            }
        };

        return { cancel };
    },
    data(){
        return{
            spot_id: null,
            user_id:null,
            veh_no:null,
            date:null,
            price:null,
            message: null
        }
    },
    created(){
      this.getDetails();
    },
    methods:{
      getDetails(){
        const access_token = localStorage.getItem("access_token");
        axios.get("http://127.0.0.1:5000/api/reserveParkingSpotAdmin",{
          params:{
            spot_id: this.spotId,
            lot_id: this.lotId
          },
          headers:{
            Authorization: `Bearer ${access_token}`
          }
        }).then(res => {
          const data = res.data;
          this.spot_id = data.spot_id;
          this.user_id = data.user_id;
          this.veh_no = data.vehicle_no.toString();
          this.date = data.parking_time;
          this.price = data.parking_cost.toString().substring(0,data.parking_cost.toString().indexOf('.')+3);
          this.message = data.message;
        });
      }
    }

} 
</script>

<style>

.view-form {
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

.Occupied_Spot_Details{
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

.edit-overlay{
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

</style>
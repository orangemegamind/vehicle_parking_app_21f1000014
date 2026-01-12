<template>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css">
    <div class="edit-overlay">
        <div class="pop-up">
            <p class="View_Delete_Parking_Spot"> View/Delete Parking Spot </p>
            <form @submit.prevent="ViewSpot" class="view-form">
              <div class="form-group">
                <label for="id">Id : </label>
                <input type="number" id="id" v-model="spot_id" readonly style="cursor:pointer" required>
              </div> 
              <div class="form-group">
                <label for="status">Status : </label>
                <input type="text" id="status" v-model="statuss" @click="SpotDetails()" readonly style="cursor:pointer" required>
              </div> 
              <button type="button" class="delete" @click="DeleteSpot()"> Delete </button>
              <button type="button" class="cancel" @click="cancel"> Cancel </button>
            </form>
        </div>

      <div class="overlay" v-if="message">
        <div class="pop-up-box">
            {{ message }}
            <button type="button" class="ok1" @click="cancel"> Ok </button>
        </div>
      </div>

    </div>
    <router-view />
    
</template>

<script>
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router';

export default{
    props:{
      spotId:{
        type: Number,
        required: true
      }
    },
    data(){
        return{
            lot_id : null,
            statuss : null,
            message: null
        }
    },
    setup(){
        console.log('inside setup')
        const route = useRoute()
        const router = useRouter()

        const sourceScreen = route.query.sourceScreen;


        const cancel = () => {
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
    created(){
      this.getSpot();
    },
    methods:{
      getSpot(){
        const access_token = localStorage.getItem("access_token");
        axios.get("http://127.0.0.1:5000/api/parkingSpot",{
          params:{
            spot_id: this.spotId
          },
          headers:{
            Authorization: `Bearer ${access_token}`
          }
        }).then(res => {
          const data = res.data;
          this.lot_id = data.lot_id;
          this.spot_id = data.spot_id;
          if(data.is_aval==false){
            this.statuss = "Occupied"
          }else{
            this.statuss = "Available"
          }
        });
      },

      DeleteSpot(){
        const access_token = localStorage.getItem("access_token");
        axios.delete("http://127.0.0.1:5000/api/parkingSpot",{
          data:{
            spot_id: this.spotId
          },
          headers:{
            Authorization: `Bearer ${access_token}`
          }
        }).then(res => {
          const data = res.data;
          this.message = data.message;
        });
      },

      SpotDetails(){
        const sourceScreen = this.$route.query.sourceScreen;
        console.log(sourceScreen)
        if(this.statuss==="Occupied"){
          if (sourceScreen == "HomeAdmin"){
            this.$router.push({
                path: `/adminHome/OccupiedSpotDetials/${this.lot_id}/${this.spot_id}`,
                query: {
                  sourceScreen: sourceScreen
                }
            });
          }
          else{
            this.$router.push({
                path: `/adminSearch/OccupiedSpotDetials/${this.lot_id}/${this.spot_id}`,
                query: {
                  sourceScreen: sourceScreen
                }
            });
          }
        }else{
          this.message = "No vehicles parked!";
        }
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

.View_Delete_Parking_Spot{
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
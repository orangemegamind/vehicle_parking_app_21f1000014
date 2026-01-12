<template>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css">
    <div class="lot-overlay">
        <div class="pop-up">
            <p class="Add_Parking_Lot"> Add Parking Lot </p>
            <form @submit.prevent="addLot" class="add-form">
                <div class="form-group">
                    <Label for="location">Prime Location Name: </Label>
                    <input type="text" id="location" v-model="location" required>
                </div>
                <div class="form-group">
                    <Label for="address">Address: </Label>
                    <input type="text" id="address" v-model="address" required>
                </div>
                <div class="form-group">
                    <Label for="pincode">Pincode: </Label>
                    <input type="number" id="pincode" v-model="pincode" required>
                </div>
                <div class="form-group">
                    <Label for="price">Price (per hour): </Label>
                    <input type="number" id="price" v-model="price" required>
                </div>
                <div class="form-group">
                    <Label for="max_spots">Maximum No. of Spots: </Label>
                    <input type="number" id="max_spots" v-model="max_spots" required>
                </div>
                <button type="add" class="add" @click="AddData()"> Add </button>
                <button type="button" class="cancel" @click="$router.push('/adminHome')"> Cancel </button>
            </form>
        </div>
        <div class="pop-up-mesg" v-if="message">
            <div class="pop-up-box">
                {{ message }}
                <button type="button" class="cancel" @click="$router.push('/adminHome')"> Ok </button>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'

export default{
    data(){
        return{
            loc_name:null,
            price:null,
            lot_address:null,
            lot_pincode:null,
            no_of_spots:null,
            message:null
        }
    },
    methods:{
        AddData(){
            const access_token = localStorage.getItem("access_token");
            axios.post("http://127.0.0.1:5000/api/parkingLot",
            {
                loc_name: this.location,
                price: this.price,
                lot_address: this.address,
                lot_pincode: this.pincode,
                no_of_spots: this.max_spots
            },
            {
                headers:{
                    Authorization: `Bearer ${access_token}`
                }
            }).then(resp => {
              this.message = resp.data.message;
              console.log(this.message)
            })

        }
    }
}

</script>


<style>
.add-form {
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

.Add_Parking_Lot{
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

.lot-overlay{
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

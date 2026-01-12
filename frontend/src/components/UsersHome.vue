<template>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css">
    <p class="Recent_Park">Recent Parking History</p>
    <div class="CSV">
        <button @click="CSV()"> Generate CSV </button>
    </div>
    <br>
    <div v-if="this.message == null">
        <table border="3" class="park_details">
            <thead>
                <tr>
                    <th id="lot_id">Lot ID</th>
                    <th id="spot_id">Spot ID</th>
                    <th id="location">Location</th>
                    <th id="vehicle_no">Vehicle Number</th>
                    <th id="timestamp">Timestamp</th>
                    <th id="action">Action</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="row in park_hist"
                    :key="`${row.id}-${row.location}-${row.vehicle_no}-${row.timestamp}-${row.action}-${row.spot_id}`">
                    <td >
                        <input id="lot_id" v-model="row.id" readonly style="cursor:pointer" required/>
                    </td>
                    <td >
                        <input id="spot_id" v-model="row.spot_id" readonly style="cursor:pointer" required/>
                    </td>
                    <td>
                        <input id="location" v-model="row.location" readonly style="cursor:pointer" required/>
                    </td>
                    <td>
                        <input id="vehicle_no" v-model="row.vehicle_no" readonly style="cursor:pointer" required/>
                    </td>
                    <td>
                        <input id="timestamp" v-model="row.timestamp" readonly style="cursor:pointer" required/>
                    </td>
                    <td>
                        <div v-if="!row.action" class="parkedOut">
                            <td>
                                <button> Parked Out </button>
                            </td>
                        </div>
                        <div v-else class="rel">
                            <td>
                                <button @click="Release(row.spot_id,row.vehicle_no)"> Release </button>
                            </td>
                        </div>
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
    <div class="user">
        <div class="content">
            <router-view />
        </div>
    </div>
</template>

<script>
import axios from 'axios'

export default{
    props:{
        username:{
            type:String,
            required:true
        }
    },
    data(){
        return{
            user_id:null,
            park_hist:null,
            message:null,
            spot_id:null
        }
    },
    created(){
        this.ParkHist();
    },
    watch: {
        $route() {
            this.ParkHist();
        }
    },
    methods:{
        Release(id,veh){
            this.selectedSpotId = id;
            this.veh = veh;
            this.$router.push({
                path: `/userHome/${this.username.toString()}/releaseSpot/${this.selectedSpotId}/${this.veh}`
            });
        },
        ParkHist(){
            const access_token = localStorage.getItem("access_token");
            console.log("home")
            axios.get("http://127.0.0.1:5000/api/ParkingHistory",{
                headers:{
                    Authorization: `Bearer ${access_token}`
                },
                params:{
                    username: this.username.toString()
                }
            })
            .then(response => {
                this.park_hist = response.data;
                if(this.park_hist?.message){
                    this.message = this.park_hist.message;
                    console.log(this.message)
                }
            })
        },
        CSV() {
            const access_token = localStorage.getItem("access_token");

            axios.get("http://127.0.0.1:5000/api/userCsv", {
                headers: {
                    Authorization: `Bearer ${access_token}`
                },
                responseType: "blob"
            })
            .then(response => {
                const url = window.URL.createObjectURL(new Blob([response.data]));
                const a = document.createElement("a");
                a.href = url;
                a.download = "user_parking.csv"; 
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
            })
            .catch(error => {
                console.error("Error downloading CSV:", error);
                alert("Failed to download CSV");
            });
        }
    }
}
</script>

<style>

.Recent_Park{
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

.Recent_Park:hover {
  background-color: #5efcc7;
  transform: scale(1.03);
  cursor: pointer;
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

.rel button{
    background-color:rgb(236, 89, 89);
}

.rel:hover button{
    background-color: red;
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

.park_details {
  width: 90%;
  margin: 30px auto;
  background: white;
  box-shadow: 0 3px 12px rgba(0,0,0,0.1);
  border-top-left-radius: 0px;
  border-bottom-right-radius: 0px;
  overflow: hidden;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.park_details th {
  background-color: #3bdca6;
  color: white;
  padding: 12px;
  text-align: left;
  text-decoration:solid;
}

.park_details td {
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.park_details input {
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

.CSV button{
    position: fixed;
    top: 200px;      
    right: 90px;     
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    background-color: Green;
}
</style>
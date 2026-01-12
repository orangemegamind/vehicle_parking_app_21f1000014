<template>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css">
    <div class="overlay">
        <div class="pop-up-box">
            <p>Do you want to delete parking lot with id : {{ lotId }} ?</p>
            <button type="button" class="ok" @click="DeleteData()"> Yes </button>
            <button type="button" class="cancel" @click="cancel"> No </button>
        </div>
    </div>
    <div class="overlay" v-if="message">
        <div class="pop-up-box">
            {{ message }}
            <button type="button" class="ok1" @click="cancel"> Ok </button>
        </div>
    </div>
</template>

<script>
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router';

export default{
    props:{
        lotId:{
            type:Number,
            required: true
        }
    },
    setup(){
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
    data(){
        return{
            message:null
        }
    },
    methods:{
        async DeleteData(){
            const access_token = localStorage.getItem("access_token");
            const res = await axios.delete(`http://127.0.0.1:5000/api/parkingLot`,{
                data:{
                    lot_id : parseInt(this.lotId)
                },
                headers:{
                    Authorization: `Bearer ${access_token}`
                }})

            this.message = res.data.message;
            console.log(this.message);
            
        }
    }
}
</script>


<style>

.overlay{
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.pop-up-box{
  background: white;
  padding: 20px;
  border-radius: 10px;
  min-width: 400px;
  position: relative;
}

.ok1{
    background-color: green;
}
</style>
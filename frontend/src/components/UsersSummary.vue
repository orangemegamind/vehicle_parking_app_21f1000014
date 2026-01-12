<template>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css">
    <div class="w-full">
        <canvas ref="chartCanvas" width="50" height="50"></canvas>
    </div>
</template>

<script>
import axios from 'axios'
import Chart from "chart.js/auto";

export default{
    data(){
        return{
            data:null,
            label : [],
            value : [],
            chartInstance : null
        }    
    },
    setup(){

    },
    mounted(){
      
    },
    created(){
        this.userChart();
    },
    methods:{
        async userChart(){
            const access_token = localStorage.getItem("access_token");
            axios.get("http://127.0.0.1:5000/api/userChart",{
                headers:{
                    Authorization: `Bearer ${access_token}`
                }
            }).then(res => {
                this.data = res.data;
                this.label = this.data.status;
                this.value = this.data.value;
                console.log(this.label)
                console.log(this.value)

                const ctx = this.$refs.chartCanvas;

                if (this.chartInstance)
                {
                  this.chartInstance.destroy();
                }

                this.chartInstance = new Chart(ctx, {
                  type: "bar",
                  data: {
                    labels: this.label,   
                    datasets: [
                      {
                        label: "User Parking Data",
                        data:this.value, 
                        backgroundColor: "rgba(54, 162, 235, 0.5)",
                        borderColor: "rgba(54, 162, 235, 1)",
                        borderWidth: 1,
                      }
                    ]
                  },
                  options: {
                    responsive: true,
                    scales: {
                      y: { 
                        beginAtZero: true,
                        title: {
                        display: true,
                        text: 'Number of Parking Spots',
                        color: '#000',   
                        font: {
                            size: 16,   
                            weight: 'bold'
                        }
                        }
                      },
                      x: { 
                        beginAtZero: true,
                        title: {
                        display: true,
                        text: 'Status',
                        color: '#000',   
                        font: {
                            size: 16,   
                            weight: 'bold'
                        }
                        }
                      },

                    }
                  }
                });
            })  
        }
    }
}
</script>

<style>
canvas {
  max-width: 600px;
  max-height: 500px;
}

.w-full{
  padding: 50px;
}
</style>
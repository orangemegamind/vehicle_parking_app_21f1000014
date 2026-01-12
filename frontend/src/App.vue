<template>
  <div id="app">
    

    <nav class="navbar navbar-expand-lg bg-body-tertiary" data-bs-theme="dark" v-if="showNav && this.userRole==='admin'">
      <div class="container-fluid">
        <div id="navbarText">
          <ul class="navbar-nav mx-auto mb-2 mb-lg-0">
            <span class="navbar-text" >
              Welcome {{ this.userRole }} !!
            </span>
            <li class="nav-item mx-2"><button @click="HomeScreen" class="btn">Home</button></li>
            <li class="nav-item mx-2"><button @click="Users" class="btn">Users</button></li>
            <li class="nav-item mx-2"><button @click="Search" class="btn">Search</button></li>
            <li class="nav-item mx-2"><button @click="Summary" class="btn">Summary</button></li>
            <li class="nav-item mx-2" v-if="isAuthenticated"><button @click="logout" class="btn">Logout</button></li>
          </ul>
        </div>
      </div>
    </nav>

    <nav class="navbar navbar-expand-lg bg-body-tertiary" data-bs-theme="dark" v-if="showNav && this.userRole==='user'">
      <div class="container-fluid">
        <div id="navbarText">
          <ul class="navbar-nav mx-auto mb-2 mb-lg-0">
            <span class="navbar-text" >
              Welcome {{ this.user.username }} !!
            </span>
            <li class="nav-item mx-2"><button @click="HomeUserScreen" class="btn">Home</button></li>
            <li class="nav-item mx-2"><button @click="UserSearch" class="btn">Search</button></li>
            <li class="nav-item mx-2"><button @click="UserSummary" class="btn">Summary</button></li>
            <li class="nav-item mx-2" v-if="isAuthenticated"><button @click="logout" class="btn">Logout</button></li>
          </ul>
        </div>
      </div>
    </nav>

    <div class="main-content">
      <template v-if = "isAuthenticated && userRole === 'user'">
       
      </template>
      <template v-if = "isAuthenticated && userRole === 'admin'">
       
        </template>
      
      <router-view/>
    </div>
  </div>
    
</template>

<script>
import axios from 'axios';

export default{
  data(){
    return{
      isAuthenticated: false,
      userRole: null,
      user:null
    }
  },

  watch:{
    $route(){
      this.checkAuth();
    }
  },

  computed:{
    showNav(){
      return this.isAuthenticated && this.$route.path!=='/login' && this.$route.path!=='/signup';
    }
  },

  created(){
    this.checkAuth();
  },

  methods:{

    checkAuth(){
      const token = localStorage.getItem("access_token");
      this.user = JSON.parse(localStorage.getItem("user"));
      if (token && this.user)
      {
        this.isAuthenticated= true;
        this.userRole = this.user.role;
      }
      else
      {
        this.isAuthenticated= false;
        this.userRole = null;
      }
    },

    async HomeScreen(){
      this.$router.push('/adminHome')
    },
    async Users(){
      this.$router.push('/userAdmin')
    },
    async Search(){
      this.$router.push('/adminSearch')
    },
    async Summary(){
      this.$router.push('/adminSummary')
    },
    async HomeUserScreen(){
      this.$router.push(`/userHome/${this.user.username}`)
    },
    async UserSearch(){
      this.$router.push('/userSearch')
    },
    async UserSummary(){
      this.$router.push('/usersSummary')
    },

    logout(){
      const access_token = localStorage.getItem("access_token");

      console.log(this.isAuthenticated);
      axios.post("http://127.0.0.1:5000/api/logout",null,{
         headers:{
          Authorization: `Bearer ${access_token}`
         }
      })
      .then(()=>{
        this.clearAuthAndRedirect();
      })
      .catch(error => {
        if (error.response && error.response.status === 401) {
          alert("Token expired, forcing logout.");
          this.clearAuthAndRedirect();
        } else {
          alert("Logout failed:", error);
        }
      })
    },

    clearAuthAndRedirect(){
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      this.isAuthenticated = false;
      this.userRole = null;
      this.$router.push("/login")
    }
  }

}
</script>

<style>

.main-content {
  padding-top: 2rem;
}

*{
  margin: 0px;
  padding: 0px;
  font-family: 'Chivo Mono', monospace;
  font-size: 16px;
}

nav{
  color: white;
}

body{
  background-color: #F8F4EA;
}

.navbar-collapse > p{
  position: relative;
  top: 9px;
}

.nav-link:hover{
  color: white;
}

ul > li > .btn:hover{
  background-color: purple;
}


.container-fluid > h5{
  text-align: center;
  color: purple;
  text-shadow: 2px 2px 2px rgb(0,0,0,0.25)
}


</style>
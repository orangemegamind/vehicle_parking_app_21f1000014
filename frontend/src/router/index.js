import { createRouter, createWebHistory } from 'vue-router'
import LoginUser from '../components/LoginUser.vue'
import SignUp from '../components/SignUp.vue'
import HomeAdmin from '../components/HomeAdmin.vue'
import UsersHome from '../components/UsersHome.vue'
import UsersSummary from '../components/UsersSummary.vue'
import AdminSearch from '../components/SearchAdmin.vue'
import AdminSummary from '../components/SummaryAdmin.vue'
import LotEdit from '../components/LotEdit.vue'
import DeleteLot from '../components/DeleteLot.vue'
import AddLot from '../components/AddLot.vue'
import ViewDeleteParkingSpot from '../components/ViewDeleteParkingSpot.vue'
import OccupiedSpotDetails from '../components/OccupiedSpotDetails.vue'
import UsersAdmin from '../components/UsersAdmin.vue'
import SearchUser from '../components/SearchUser.vue'
import User_Book from '../components/UserBook.vue'
import ReleaseSpot from '../components/ReleaseSpot.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginUser
  },
  {
    path: '/signup',
    name: 'SignUp',
    component: SignUp
  },
  {
    path: '/userHome/:username',
    name: 'UsersHome',
    component: UsersHome,
    props: true,
    meta: { modal: true },
    children:[
      {
        path: 'releaseSpot/:spotId/:vehNo',
        name: 'ReleaseSpot',
        component: ReleaseSpot,
        props: true,
      }
    ]
  },
  {
    path: '/userSearch',
    name: 'userSearch',
    component: SearchUser,
    props: true,
    children:[
      {
        path: 'userBook/:lotId',
        name: 'UserBook',
        component: User_Book,
        props: true
      }
    ]
  },
  {
    path: '/usersSummary',
    name: 'UsersSummary',
    component: UsersSummary,
  },
  {
    path: '/adminHome',
    name: 'HomeAdmin',
    component: HomeAdmin,
    children:[
      {
        path: 'edit/:lotId',
        name: 'LotEditHome',
        component: LotEdit,
        props:true,
        meta: { modal: true }
      },
      {
        path: 'delete/:lotId',
        name: 'DeleteLotHome',
        component: DeleteLot,
        props:true,
        meta: { modal: true }
      },
      {
        path: 'addLot',
        name: 'AddLot',
        component: AddLot
      },
      {
        path: 'viewSpot/:spotId',
        name: 'viewSpotHome',
        component: ViewDeleteParkingSpot,
        props:true,
        meta: { modal: true },
      },
      {
        path: 'OccupiedSpotDetials/:lotId/:spotId',
        name: 'OccupiedSpotDetialsHome',
        component: OccupiedSpotDetails,
        props:true,
        meta: { modal: true }
      }
    ]
  },
  {
    path: '/userHome',
    name: 'HomeUser',
    component: UsersHome
  },
  {
    path: '/userAdmin',
    name: 'UsersAdmin',
    component: UsersAdmin
  },
  {
    path: '/adminSearch',
    name: 'AdminSearch',
    component: AdminSearch,
    children:[
      {
        path: 'edit/:lotId',
        name: 'LotEditSearch',
        component: LotEdit,
        props:true,
        meta: { modal: true }
      },
      {
        path: 'delete/:lotId',
        name: 'DeleteLotSearch',
        component: DeleteLot,
        props:true,
        meta: { modal: true }
      },
      {
        path: 'viewSpot/:spotId',
        name: 'viewSpotSearch',
        component: ViewDeleteParkingSpot,
        props:true,
        meta: { modal: true },
      },
      {
        path: 'OccupiedSpotDetials/:lotId/:spotId',
        name: 'OccupiedSpotDetialsSearch',
        component: OccupiedSpotDetails,
        props:true
      }
    ]
  },
  {
    path:'/adminSummary',
    name: 'AdminSummary',
    component: AdminSummary
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router

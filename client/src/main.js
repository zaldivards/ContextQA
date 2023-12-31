import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'


import PrimeVue from 'primevue/config';
import ToastService from 'primevue/toastservice';
import ConfirmationService from 'primevue/confirmationservice';

import 'primevue/resources/themes/saga-blue/theme.css'       //theme
import 'primevue/resources/primevue.min.css'                 //core css
import 'primeicons/primeicons.css'
import '/node_modules/primeflex/primeflex.css'


export const app = createApp(App);

app.use(PrimeVue).use(ToastService).use(ConfirmationService).use(store).use(router).mount('#app');

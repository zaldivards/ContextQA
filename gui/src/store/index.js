import { createStore } from 'vuex'

export default createStore({
    state: {
        identifier: ""
    },
    mutations: {
        updateIdentifier(state, payload) {
            state.identifier = payload;
        }
    },
    actions: {
        setIdentifier({ commit }, payload) {
            commit('updateIdentifier', payload);
        }
    }
});

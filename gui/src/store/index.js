import { createStore } from 'vuex'

export default createStore({
    state: {
        identifier: "",
        messages: [],
        showSpinner: false,
        lastMessageText: ''
    },
    mutations: {
        updateIdentifier(state, payload) {
            state.identifier = payload;
        },
        updateMessages(state, payload) {
            state.messages.push(payload)
        },
        updateFlag(state, payload) {
            state.showSpinner = payload
        },
        updateLastMessage(state, payload) {

            state.lastMessageText = payload.content
            if (!payload.isInit) {
                state.messages.pop()
                state.messages.push({ content: payload.content, role: 'bot' })
            }
            state.showSpinner = false
        }
    },
    actions: {
        setIdentifier({ commit }, payload) {
            commit('updateIdentifier', payload);
        },
        setMessage({ commit }, payload) {
            commit('updateMessages', payload);
        },
        activateSpinner({ commit }, payload) {
            commit('updateFlag', payload);
        },
        setLastMessage({ commit }, payload) {
            commit('updateLastMessage', payload);
        }
    }
});

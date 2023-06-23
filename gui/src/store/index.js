import { createStore } from 'vuex'

export default createStore({
    state: {
        identifier: null,
        messages: [],
        showSpinner: false,
        lastMessageText: '',
        vectorStore: ''
    },
    mutations: {
        updateApiParams(state, payload) {
            state.identifier = payload.identifier;
            state.vectorStore = payload.vectorStore;

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
        setApiParams({ commit }, payload) {
            commit('updateApiParams', payload);
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

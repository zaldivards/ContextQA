import { createStore } from 'vuex'

export default createStore({
    state: {
        identifier: null,
        chatMessages: [],
        documentMessages: [],
        showSpinner: false,
        lastDocumentMessageText: '',
        lastChatMessageText: '',
        vectorStore: '',
        internetEnabled: false,
        latestSources: ''
    },
    mutations: {
        updateApiParams(state, payload) {
            state.identifier = payload
        },
        updateChatMessages(state, payload) {
            state.chatMessages.push(payload)
        },
        updateDocumentMessages(state, payload) {
            state.documentMessages.push(payload)
        },
        updateFlag(state, payload) {
            state.showSpinner = payload
        },
        updateLastChatMessage(state, payload) {

            state.lastChatMessageText = payload.content
            const { isInit, ...message } = payload
            if (!isInit) {
                state.chatMessages.pop()
                state.chatMessages.push(message)
            }
        },
        updateLastDocumentMessage(state, payload) {

            state.lastDocumentMessageText = payload.content
            const { isInit, ...message } = payload
            if (!isInit) {
                state.documentMessages.pop()
                state.documentMessages.push(message)
            }
        },
        updateInternetAccess(state, payload) {
            state.internetEnabled = payload
        },
        updateSources(state, payload) {
            state.latestSources = payload
        }
    },
    actions: {
        setApiParams({ commit }, payload) {
            commit('updateApiParams', payload);
        },
        setDocumentMessage({ commit }, payload) {
            commit('updateDocumentMessages', payload);
        },
        setChatMessage({ commit }, payload) {
            commit('updateChatMessages', payload);
        },
        activateSpinner({ commit }, payload) {
            commit('updateFlag', payload);
        },
        setLastChatMessage({ commit }, payload) {
            commit('updateLastChatMessage', payload);
        },
        setLastDocumentMessage({ commit }, payload) {
            commit('updateLastDocumentMessage', payload);
        },
        setInternetAccess({ commit }, payload) {
            commit('updateInternetAccess', payload);
        },
        setLatestSources({ commit }, payload) {
            commit('updateSources', payload);
        }
    }
});

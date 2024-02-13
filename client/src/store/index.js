import { createStore } from 'vuex'

export default createStore({
    state: {
        sourcesReady: false,
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
        },
        updateSourcesFlag(state, payload) {
            state.sourcesReady = payload
        }
    },
    actions: {
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
        },
        setSourcesFlag({ commit }, payload) {
            commit('updateSourcesFlag', payload);
        }
    }
});

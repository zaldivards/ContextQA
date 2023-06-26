import { ToastSeverity } from 'primevue/api';
import { app } from '@/main';


const API_BASE_URL = process.env.VUE_APP_API_BASE_URL

export function getDateTimeStr() {
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    const [date, time] = now.toISOString().split("T");
    return `${date} ${time.slice(0, -5)}`;
}

async function handleResponse(res) {
    const responseText = await res.text()
    const errorMessage = responseText.includes('ECONNREFUSED') ? "The server refused the connection" : "The LLM server did not process the message properly"
    throw new Error(errorMessage)
}


export async function setContext(endpoint, data) {
    const formData = new FormData()
    formData.append('separator', data.separator)
    formData.append('chunk_size', data.chunkSize)
    formData.append('chunk_overlap', data.overlap)
    formData.append('similarity_processor', 'local')
    formData.append('document', data.file)

    const response = await fetch(
        API_BASE_URL + endpoint, {
        method: 'POST',
        body: formData
    }
    );
    if (!response.ok)
        await handleResponse(response)
    const json_ = await response.json();
    return json_.response;
}

export async function askLLM(endpoint, params) {
    const response = await fetch(
        API_BASE_URL + endpoint + "?" +
        new URLSearchParams(params)
    );
    if (!response.ok)
        await handleResponse(response)

    const json_ = await response.json();
    return json_.response;
}


export const showSuccess = (message) => {
    app.config.globalProperties.$toast.add({ severity: ToastSeverity.SUCCESS, summary: 'Success', detail: message, life: 3000 });
};

export const showInfo = (message) => {
    app.config.globalProperties.$toast.add({ severity: ToastSeverity.INFO, summary: 'Info', detail: message, life: 3000 });
};

export const showError = (message) => {
    app.config.globalProperties.$toast.add({ severity: ToastSeverity.ERROR, summary: 'Error', detail: message, life: 10000 });
};

export const showWarning = (message, life = 30000) => {
    app.config.globalProperties.$toast.add({ severity: ToastSeverity.WARN, summary: 'Warning', detail: message, life: life });
};
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
    let errorMessage = ""
    if (responseText.includes('ECONNREFUSED'))
        errorMessage = "The server refused the connection"
    else {
        const json_ = JSON.parse(responseText)
        errorMessage = json_.detail.message
    }
    throw new Error(errorMessage)
}


export async function setContext(endpoint, data) {
    const formData = new FormData()
    formData.append('separator', data.separator)
    formData.append('chunk_size', data.chunkSize)
    formData.append('chunk_overlap', data.overlap)
    formData.append('similarity_processor', data.processor)
    formData.append('document', data.file)

    const response = await fetch(
        API_BASE_URL + endpoint, {
        method: 'POST',
        body: formData
    }
    );
    if (response.ok) {
        const json_ = await response.json();
        return json_.response
    }
    else {
        await handleResponse(response)
    }
}

export async function askLLM(endpoint, params) {
    const response = await fetch(
        API_BASE_URL + endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(params)
    }
    );
    if (response.ok) {
        const json_ = await response.json();
        return json_.response
    }
    else
        await handleResponse(response)
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
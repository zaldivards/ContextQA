import { ToastSeverity } from 'primevue/api';
import { app } from '@/main';
import {API_BASE_URL} from './constants'

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


export async function fetchResource(endpoint, data) {
    const response = await fetch(
        API_BASE_URL + endpoint, data
    );
    if (response.ok) {
        return await response.json();
    }
    else {
        await handleResponse(response)
        return;
    }
}

export async function ingestSources(endpoint, data) {
    const formData = new FormData()
    data.files.forEach(file => {
        formData.append("documents", file)
    })
    return await fetchResource(
        endpoint, {
        method: 'POST',
        body: formData
    }
    );
}


export async function* askLLM(endpoint, params) {
    let sources = []
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
        const decoder = new TextDecoder()
        const reader = response.body.getReader();
        try {
            while (true) {
                const { value, done } = await reader.read();
                if (done)
                    break
                const data = decoder.decode(value);
                if (data.includes("<source>")) {
                    sources.push(...value)
                }
                else
                    yield data;
            }

        } finally {
            reader.releaseLock();
        }
        const resultarray = new Uint8Array(sources)
        const result = decoder.decode(resultarray).replaceAll("<source>", "")
        yield "<sources>" + result
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
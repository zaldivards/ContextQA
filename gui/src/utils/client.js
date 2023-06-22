import { ToastSeverity } from 'primevue/api';
import { app } from '@/main';


async function handleResponse(res) {
    const responseText = await res.text()
    if (responseText.includes('ECONNREFUSED'))
        throw new Error("The server refused the connection")
    else {
        console.log(responseText);
        return "Something went wrong in the server"
    }
}


export async function setContext(url, data) {
    const formData = new FormData()
    formData.append('separator', data.separator)
    formData.append('chunk_size', data.chunkSize)
    formData.append('chunk_overlap', data.overlap)
    formData.append('similarity_processor', 'local')
    formData.append('document', data.file)

    const response = await fetch(
        url, {
        method: 'POST',
        body: formData
    }
    );
    if (!response.ok)
        return handleResponse(response)
    const json_ = await response.json();
    return json_.response;
}

export async function askLLM(url, params) {
    const response = await fetch(
        url + "?" +
        new URLSearchParams(params)
    );
    if (!response.ok)
        return handleResponse(response)

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
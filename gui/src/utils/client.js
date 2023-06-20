import { ToastSeverity } from 'primevue/api';
import { app } from '@/main';

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
    const json_ = await response.json();
    console.log(json_)
    return json_.response;
}


export const showSuccess = (message) => {
    app.config.globalProperties.$toast.add({ severity: ToastSeverity.SUCCESS, summary: 'Success', detail: message, life: 3000 });
};

export const showInfo = (message) => {
    app.config.globalProperties.$toast.add({ severity: ToastSeverity.INFO, summary: 'Info', detail: message, life: 3000 });
};

export const showError = (message) => {
    app.config.globalProperties.$toast.add({ severity: ToastSeverity.ERROR, summary: 'Error', detail: message, life: 3000 });
};
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';

export interface TranscriptResponse {
    transcript: string;
    video_id: string;
}

export interface Excerpt {
    title: string;
    content: string;
}

export interface ExcerptList {
    insights: Excerpt[];
}

export interface DownloadResponse {
    data: string;
    filename: string;
    content_type: string;
}

export const getTranscript = async (url: string): Promise<TranscriptResponse> => {
    const response = await fetch(`${API_BASE_URL}/transcript`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch transcript');
    }
    return response.json();
};

export const generateExcerpts = async (transcript: string): Promise<ExcerptList> => {
    const response = await fetch(`${API_BASE_URL}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transcript }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to generate excerpts');
    }
    return response.json();
};

export const downloadExcerpt = async (
    title: string,
    content: string,
    format: 'pdf' | 'image'
): Promise<DownloadResponse> => {
    const response = await fetch(`${API_BASE_URL}/download`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content, format }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to generate download');
    }
    return response.json();
};

export const triggerDownload = (base64Data: string, filename: string, contentType: string) => {
    const link = document.createElement('a');
    link.href = `data:${contentType};base64,${base64Data}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};

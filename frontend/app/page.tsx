'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Search,
    Sparkles,
    FileText,
    Download,
    Image as ImageIcon,
    Youtube,
    Instagram,
    Linkedin,
    ChevronRight,
    Loader2,
    CheckCircle2,
    AlertCircle
} from 'lucide-react';

// TikTok Icon Component since it's not in standard Lucide set yet
const Tiktok = ({ className }: { className?: string }) => (
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className={className}
    >
        <path d="M9 12a4 4 0 1 0 4 4V4a5 5 0 0 0 5 5" />
    </svg>
);

import { getTranscript, generateExcerpts, downloadExcerpt, triggerDownload, Excerpt } from '@/lib/api';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Helper for Tailwind classes
function cn(...inputs: (string | undefined | null | false)[]) {
    return twMerge(clsx(inputs));
}

export default function Home() {
    const [url, setUrl] = useState('');
    const [transcript, setTranscript] = useState('');
    const [excerpts, setExcerpts] = useState<Excerpt[]>([]);
    const [loading, setLoading] = useState(false);
    const [generating, setGenerating] = useState(false);
    const [status, setStatus] = useState<{ type: 'loading' | 'success' | 'error'; message: string } | null>(null);
    const [downloadingIndex, setDownloadingIndex] = useState<{ idx: number; type: 'pdf' | 'image' } | null>(null);

    const [selectedPlatform, setSelectedPlatform] = useState<'youtube' | 'instagram' | 'linkedin' | 'tiktok'>('youtube');

    const platforms = [
        { id: 'youtube', name: 'YouTube', icon: Youtube, color: '#FF0000', placeholder: 'Paste YouTube URL here...' },
        { id: 'instagram', name: 'Instagram', icon: Instagram, color: '#E1306C', placeholder: 'Paste Instagram Reel/Video URL...' },
        { id: 'linkedin', name: 'LinkedIn', icon: Linkedin, color: '#0A66C2', placeholder: 'Paste LinkedIn Video Post URL...' },
        { id: 'tiktok', name: 'TikTok', icon: Tiktok, color: '#00F2EA', placeholder: 'Paste TikTok Video URL...' },
    ] as const;

    const currentPlatform = platforms.find(p => p.id === selectedPlatform)!;

    const handleGetTranscript = async () => {
        if (!url.trim()) return;

        setLoading(true);
        setStatus({ type: 'loading', message: `Fetching transcript from ${currentPlatform.name}...` });
        setExcerpts([]);

        try {
            const data = await getTranscript(url);
            setTranscript(data.transcript);
            setStatus({ type: 'success', message: 'Transcript ready!' });
        } catch (error: any) {
            setStatus({ type: 'error', message: error.message || 'Failed to fetch transcript' });
            setTranscript('');
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateExcerpts = async () => {
        if (!transcript) return;

        setGenerating(true);
        setStatus({ type: 'loading', message: 'Analyzing content...' });

        try {
            const data = await generateExcerpts(transcript);
            setExcerpts(data.insights);
            setStatus({ type: 'success', message: `Generated ${data.insights.length} insights` });
        } catch (error: any) {
            setStatus({ type: 'error', message: error.message || 'Failed to generate excerpts' });
        } finally {
            setGenerating(false);
        }
    };

    const handleDownload = async (excerpt: Excerpt, format: 'pdf' | 'image', index: number) => {
        setDownloadingIndex({ idx: index, type: format });
        try {
            const data = await downloadExcerpt(excerpt.title, excerpt.content, format);
            triggerDownload(data.data, data.filename, data.content_type);
        } catch (error: any) {
            setStatus({ type: 'error', message: 'Download failed' });
        } finally {
            setDownloadingIndex(null);
        }
    };

    return (
        <div className="min-h-screen bg-[#09090b] text-neutral-200 selection:bg-indigo-500/30">
            {/* Dynamic Background */}
            <div className="fixed inset-0 z-0">
                <div className="absolute inset-0 bg-grid opacity-20" />
                <div className="absolute -top-40 -left-40 w-96 h-96 bg-indigo-600/20 rounded-full blur-[128px] animate-pulse" />
                <div className="absolute top-40 right-40 w-96 h-96 bg-purple-600/10 rounded-full blur-[128px]" />
            </div>

            <main className="relative z-10 max-w-7xl mx-auto px-6 py-20">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-20"
                >
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-sm font-medium mb-8 backdrop-blur-sm">
                        <Sparkles className="w-4 h-4" />
                        <span>AI-Powered Content Extraction</span>
                    </div>

                    <h1 className="text-6xl md:text-8xl font-bold tracking-tight mb-6">
                        Transcrib<span className="gradient-text">ai</span>
                    </h1>

                    <p className="text-xl text-neutral-400 max-w-2xl mx-auto leading-relaxed mb-10">
                        Transform lengthy videos into concise, actionable insights in seconds.
                    </p>

                    <div className="flex items-center justify-center gap-8 text-neutral-500">
                        {platforms.map((platform) => {
                            const Icon = platform.icon;
                            const isSelected = selectedPlatform === platform.id;
                            return (
                                <button
                                    key={platform.id}
                                    onClick={() => setSelectedPlatform(platform.id as any)}
                                    className={cn(
                                        "flex flex-col items-center gap-2 transition-all duration-300 group",
                                        isSelected ? "text-white scale-110" : "hover:text-white hover:scale-105"
                                    )}
                                >
                                    <div
                                        className={cn(
                                            "p-4 rounded-2xl border transition-all duration-300",
                                            isSelected
                                                ? `bg-[${platform.color}]/10 border-[${platform.color}]/50 shadow-[0_0_20px_${platform.color}40]`
                                                : "bg-white/5 border-white/5 group-hover:bg-white/10"
                                        )}
                                        style={isSelected ? { borderColor: platform.color, backgroundColor: `${platform.color}15` } : {}}
                                    >
                                        <Icon
                                            className="w-7 h-7 transition-colors"
                                            style={isSelected ? { color: platform.color } : {}}
                                        />
                                    </div>
                                    <span className={cn(
                                        "text-xs font-medium transition-colors",
                                        isSelected ? "text-white" : "group-hover:text-white/80"
                                    )}>
                                        {platform.name}
                                    </span>
                                </button>
                            );
                        })}
                    </div>
                </motion.div>

                {/* Search Input */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="max-w-4xl mx-auto mb-20"
                >
                    <div className="relative group">
                        <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl opacity-20 group-hover:opacity-40 transition duration-500 blur-lg" />
                        <div className="relative flex items-center bg-[#18181b]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-2 shadow-2xl transition-all duration-500">
                            <div className="pl-6 text-neutral-400 transition-colors duration-300">
                                <currentPlatform.icon
                                    className="w-6 h-6"
                                    style={{ color: currentPlatform.color }}
                                />
                            </div>
                            <input
                                type="text"
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleGetTranscript()}
                                placeholder={currentPlatform.placeholder}
                                className="flex-1 bg-transparent border-none outline-none text-white placeholder-neutral-500 focus:ring-0 focus:outline-none text-lg py-3 px-6 rounded-xl"
                            />
                            <button
                                onClick={handleGetTranscript}
                                disabled={loading || !url.trim()}
                                className="btn-glow px-6 py-3 rounded-xl font-bold text-lg text-white disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-transform active:scale-95"
                            >
                                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
                                <span>Fetch</span>
                            </button>
                        </div>
                    </div>

                    {/* Status Message */}
                    <AnimatePresence mode="wait">
                        {status && (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                className={cn(
                                    "mt-6 flex items-center justify-center gap-2 text-sm font-medium",
                                    status.type === 'error' ? "text-red-400" :
                                        status.type === 'success' ? "text-emerald-400" : "text-indigo-400"
                                )}
                            >
                                {status.type === 'loading' && <Loader2 className="w-4 h-4 animate-spin" />}
                                {status.type === 'success' && <CheckCircle2 className="w-4 h-4" />}
                                {status.type === 'error' && <AlertCircle className="w-4 h-4" />}
                                {status.message}
                            </motion.div>
                        )}
                    </AnimatePresence>
                </motion.div>

                {/* Content Area */}
                <AnimatePresence>
                    {transcript && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="space-y-12"
                        >
                            {/* Transcript Preview */}
                            <div className="glass-card rounded-3xl p-8 md:p-10 relative overflow-hidden">
                                <div className="flex items-center justify-between mb-8">
                                    <div className="flex items-center gap-4">
                                        <div className="p-3 rounded-2xl bg-indigo-500/10 text-indigo-400">
                                            <FileText className="w-6 h-6" />
                                        </div>
                                        <div>
                                            <h2 className="text-xl font-semibold text-white">{currentPlatform.name} Summary</h2>
                                            <p className="text-sm text-neutral-500">{transcript.split(' ').length.toLocaleString()} words found</p>
                                        </div>
                                    </div>

                                    <button
                                        onClick={handleGenerateExcerpts}
                                        disabled={generating}
                                        className="hidden md:flex bg-white/5 hover:bg-white/10 active:scale-95 transition-all text-white px-6 py-3 rounded-xl font-medium items-center gap-2 border border-white/5"
                                    >
                                        {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4 text-amber-300" />}
                                        Generate Excerpts
                                    </button>
                                </div>

                                <div className="relative">
                                    <div className="absolute top-0 left-0 right-0 h-8 bg-gradient-to-b from-[#18181b] to-transparent z-10 opacity-50" />
                                    <div className="h-48 overflow-y-auto pr-4 text-neutral-400 leading-relaxed scrollbar-thin">
                                        {transcript}
                                    </div>
                                    <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-[#18181b]/90 to-transparent pointer-events-none" />
                                </div>

                                <button
                                    onClick={handleGenerateExcerpts}
                                    className="md:hidden mt-6 w-full btn-glow py-4 rounded-xl font-semibold text-white flex items-center justify-center gap-2"
                                >
                                    <Sparkles className="w-4 h-4" /> Generate Excerpts
                                </button>
                            </div>

                            {/* Generated Excerpts */}
                            {excerpts.length > 0 && (
                                <div className="space-y-8">
                                    <div className="flex items-center gap-3 text-2xl font-semibold text-white">
                                        <Sparkles className="w-6 h-6 text-indigo-400" />
                                        <h3>Generated Insights</h3>
                                    </div>

                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                        {excerpts.map((excerpt, idx) => (
                                            <motion.div
                                                key={idx}
                                                initial={{ opacity: 0, scale: 0.95 }}
                                                animate={{ opacity: 1, scale: 1 }}
                                                transition={{ delay: idx * 0.1 }}
                                                className="glass-card rounded-3xl p-8 hover:border-indigo-500/30 transition-all duration-300 group"
                                            >
                                                <div className="flex justify-between items-start mb-6">
                                                    <span className="text-5xl font-bold text-indigo-500/10 group-hover:text-indigo-500/20 transition-colors">
                                                        {String(idx + 1).padStart(2, '0')}
                                                    </span>
                                                    <div className="flex gap-2">
                                                        <button
                                                            onClick={() => handleDownload(excerpt, 'pdf', idx)}
                                                            disabled={downloadingIndex?.idx === idx}
                                                            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-neutral-400 hover:text-white transition-colors"
                                                            title="Download PDF"
                                                        >
                                                            {downloadingIndex?.idx === idx && downloadingIndex.type === 'pdf' ?
                                                                <Loader2 className="w-5 h-5 animate-spin" /> :
                                                                <FileText className="w-5 h-5" />
                                                            }
                                                        </button>
                                                        <button
                                                            onClick={() => handleDownload(excerpt, 'image', idx)}
                                                            disabled={downloadingIndex?.idx === idx}
                                                            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-neutral-400 hover:text-white transition-colors"
                                                            title="Download Image"
                                                        >
                                                            {downloadingIndex?.idx === idx && downloadingIndex.type === 'image' ?
                                                                <Loader2 className="w-5 h-5 animate-spin" /> :
                                                                <ImageIcon className="w-5 h-5" />
                                                            }
                                                        </button>
                                                    </div>
                                                </div>

                                                <h4 className="text-xl font-bold text-white mb-4 line-clamp-2">{excerpt.title}</h4>
                                                <p className="text-neutral-400 mb-6 leading-relaxed line-clamp-4 hover:line-clamp-none transition-all duration-300">
                                                    {excerpt.content}
                                                </p>
                                            </motion.div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </motion.div>
                    )}
                </AnimatePresence>
            </main>
        </div>
    );
}

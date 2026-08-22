import React from 'react';
import { LucideIcon, FileText } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

// Loading Components
export const LoadingSpinner: React.FC<{ size?: 'sm' | 'md' | 'lg'; className?: string }> = ({
    size = 'md',
    className = ''
}) => {
    const sizeClasses = {
        sm: 'w-4 h-4',
        md: 'w-6 h-6',
        lg: 'w-8 h-8'
    };

    return (
        <div className={`${sizeClasses[size]} ${className}`}>
            <div className="animate-spin rounded-full border-2 border-gray-300 border-t-primary-600 dark:border-gray-600 dark:border-t-primary-400"></div>
        </div>
    );
};

export const LoadingDots: React.FC<{ className?: string }> = ({ className = '' }) => (
    <span className={`loading-dots ${className}`}>Loading</span>
);

// Button Components
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
    size?: 'sm' | 'md' | 'lg';
    icon?: LucideIcon;
    iconPosition?: 'left' | 'right';
    loading?: boolean;
    children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
    variant = 'primary',
    size = 'md',
    icon: Icon,
    iconPosition = 'left',
    loading = false,
    children,
    className = '',
    disabled,
    ...props
}) => {
    const baseClasses = 'inline-flex items-center justify-center font-medium transition-all duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

    const variantClasses = {
        primary: 'btn-primary',
        secondary: 'btn-secondary',
        ghost: 'btn-ghost',
        danger: 'bg-gradient-danger text-white hover:scale-105 active:scale-95'
    };

    const sizeClasses = {
        sm: 'px-3 py-2 text-sm rounded-lg',
        md: 'px-4 py-2.5 text-sm rounded-xl',
        lg: 'px-6 py-3 text-base rounded-xl'
    };

    const iconSizeClasses = {
        sm: 'w-4 h-4',
        md: 'w-4 h-4',
        lg: 'w-5 h-5'
    };

    return (
        <button
            className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
            disabled={disabled || loading}
            {...props}
        >
            {loading ? (
                <>
                    <LoadingSpinner size="sm" className="mr-2" />
                    {children}
                </>
            ) : (
                <>
                    {Icon && iconPosition === 'left' && (
                        <Icon className={`${iconSizeClasses[size]} mr-2`} />
                    )}
                    {children}
                    {Icon && iconPosition === 'right' && (
                        <Icon className={`${iconSizeClasses[size]} ml-2`} />
                    )}
                </>
            )}
        </button>
    );
};

// Card Components
interface CardProps {
    children: React.ReactNode;
    className?: string;
    variant?: 'default' | 'glass' | 'glass-strong';
    hoverable?: boolean;
    animate?: boolean;
}

export const Card: React.FC<CardProps> = ({
    children,
    className = '',
    variant = 'default',
    hoverable = false,
    animate = false
}) => {
    const baseClasses = 'rounded-2xl transition-all duration-300';

    const variantClasses = {
        default: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-lg',
        glass: 'glass-card',
        'glass-strong': 'glass-card-strong'
    };

    const hoverClasses = hoverable ? 'hover:scale-105 hover:shadow-xl cursor-pointer' : '';
    const animateClasses = animate ? 'animate-fade-in-up' : '';

    return (
        <div className={`${baseClasses} ${variantClasses[variant]} ${hoverClasses} ${animateClasses} ${className}`}>
            {children}
        </div>
    );
};

// Status Badge Component
interface StatusBadgeProps {
    status: 'online' | 'offline' | 'checking';
    children: React.ReactNode;
    className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, children, className = '' }) => {
    const statusClasses = {
        online: 'status-online',
        offline: 'status-offline',
        checking: 'status-checking'
    };

    return (
        <span className={`status-badge ${statusClasses[status]} ${className}`}>
            {children}
        </span>
    );
};

// Input Components
interface InputFieldProps extends React.InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
    icon?: LucideIcon;
    iconPosition?: 'left' | 'right';
}

export const InputField: React.FC<InputFieldProps> = ({
    label,
    error,
    icon: Icon,
    iconPosition = 'left',
    className = '',
    ...props
}) => {
    return (
        <div className="w-full">
            {label && (
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {label}
                </label>
            )}
            <div className="relative">
                {Icon && iconPosition === 'left' && (
                    <Icon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                )}
                <input
                    className={`input-field ${Icon && iconPosition === 'left' ? 'pl-10' : ''} ${Icon && iconPosition === 'right' ? 'pr-10' : ''} ${error ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''} ${className}`}
                    {...props}
                />
                {Icon && iconPosition === 'right' && (
                    <Icon className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                )}
            </div>
            {error && (
                <p className="mt-2 text-sm text-red-600 dark:text-red-400">{error}</p>
            )}
        </div>
    );
};

// Tab Components
interface TabButtonProps {
    active: boolean;
    icon: LucideIcon;
    children: React.ReactNode;
    onClick: () => void;
}

export const TabButton: React.FC<TabButtonProps> = ({ active, icon: Icon, children, onClick }) => {
    return (
        <button
            onClick={onClick}
            className={`tab-button ${active ? 'active' : 'inactive'}`}
        >
            <Icon className="w-4 h-4" />
            <span className="font-medium">{children}</span>
        </button>
    );
};

// Progress Bar Component
interface ProgressBarProps {
    progress: number; // 0-100
    className?: string;
    showLabel?: boolean;
    animated?: boolean;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
    progress,
    className = '',
    showLabel = false,
    animated = false
}) => {
    return (
        <div className={`w-full ${className}`}>
            {showLabel && (
                <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
                    <span>Progress</span>
                    <span>{progress}%</span>
                </div>
            )}
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                <div
                    className={`bg-gradient-primary h-2.5 rounded-full transition-all duration-500 ease-out ${animated ? 'animate-pulse' : ''}`}
                    style={{ width: `${Math.min(Math.max(progress, 0), 100)}%` }}
                />
            </div>
        </div>
    );
};

// Toast/Notification Component
interface ToastProps {
    type: 'success' | 'error' | 'warning' | 'info';
    title: string;
    message?: string;
    onClose?: () => void;
    autoClose?: boolean;
    duration?: number;
}

export const Toast: React.FC<ToastProps> = ({
    type,
    title,
    message,
    onClose,
    autoClose = true,
    duration = 5000
}) => {
    React.useEffect(() => {
        if (autoClose && onClose) {
            const timer = setTimeout(onClose, duration);
            return () => clearTimeout(timer);
        }
    }, [autoClose, duration, onClose]);

    const typeClasses = {
        success: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800',
        error: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800',
        warning: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800',
        info: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
    };

    const iconClasses = {
        success: 'text-green-600 dark:text-green-400',
        error: 'text-red-600 dark:text-red-400',
        warning: 'text-yellow-600 dark:text-yellow-400',
        info: 'text-blue-600 dark:text-blue-400'
    };

    return (
        <div className={`${typeClasses[type]} border rounded-xl p-4 animate-slide-in-down`}>
            <div className="flex items-start">
                <div className="flex-1">
                    <h4 className={`font-medium ${iconClasses[type]}`}>{title}</h4>
                    {message && (
                        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">{message}</p>
                    )}
                </div>
                {onClose && (
                    <button
                        onClick={onClose}
                        className="ml-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                    >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                )}
            </div>
        </div>
    );
};

// Modal Component
interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
    title?: string;
    children: React.ReactNode;
    size?: 'sm' | 'md' | 'lg' | 'xl';
}

export const Modal: React.FC<ModalProps> = ({
    isOpen,
    onClose,
    title,
    children,
    size = 'md'
}) => {
    if (!isOpen) return null;

    const sizeClasses = {
        sm: 'max-w-md',
        md: 'max-w-lg',
        lg: 'max-w-2xl',
        xl: 'max-w-4xl'
    };

    React.useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };
        document.addEventListener('keydown', handleEscape);
        return () => document.removeEventListener('keydown', handleEscape);
    }, [onClose]);

    return (
        <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex min-h-screen items-center justify-center p-4">
                <div
                    className="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity animate-fade-in"
                    onClick={onClose}
                />
                <div className={`${sizeClasses[size]} w-full mx-4 md:mx-0 animate-scale-in`}>
                    <Card variant="glass-strong" className="relative">
                        <div className="p-6">
                            {title && (
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                                        {title}
                                    </h3>
                                    <button
                                        onClick={onClose}
                                        className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                                    >
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>
                                </div>
                            )}
                            {children}
                        </div>
                    </Card>
                </div>
            </div>
        </div>
    );
};

// Empty State Component
interface EmptyStateProps {
    icon: LucideIcon;
    title: string;
    description?: string;
    action?: {
        label: string;
        onClick: () => void;
    };
}

export const EmptyState: React.FC<EmptyStateProps> = ({
    icon: Icon,
    title,
    description,
    action
}) => {
    return (
        <div className="text-center py-8 md:py-12">
            <Icon className="w-16 h-16 mx-auto mb-4 text-gray-400 dark:text-gray-500" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">{title}</h3>
            {description && (
                <p className="text-gray-600 dark:text-gray-400 mb-6">{description}</p>
            )}
            {action && (
                <Button onClick={action.onClick}>{action.label}</Button>
            )}
        </div>
    );
};

// File List Item Component
interface FileListItemProps {
    filename: string;
    isSelected: boolean;
    onClick: () => void;
    icon?: LucideIcon;
}

export const FileListItem: React.FC<FileListItemProps> = ({
    filename,
    isSelected,
    onClick,
    icon: Icon
}) => {
    return (
        <div
            onClick={onClick}
            className={`
        p-4 rounded-xl cursor-pointer transition-all duration-200 border
        ${isSelected
                    ? 'bg-primary-50 dark:bg-primary-900/20 border-primary-200 dark:border-primary-800 text-primary-700 dark:text-primary-300'
                    : 'bg-white/50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-white/80 dark:hover:bg-gray-800/80 hover:border-gray-300 dark:hover:border-gray-600'
                }
      `}
        >
            <div className="flex items-center space-x-3">
                {Icon && <Icon className="w-5 h-5 flex-shrink-0" />}
                <span className="text-sm font-medium truncate">{filename}</span>
            </div>
        </div>
    );
};

// Content Display Components
interface ContentViewerProps {
    content: string;
    isMarkdown?: boolean;
    maxHeight?: string;
    showCopyButton?: boolean;
    title?: string;
}

export const ContentViewer: React.FC<ContentViewerProps> = ({
    content,
    isMarkdown = false,
    maxHeight = '600px',
    showCopyButton = true,
    title
}) => {
    const [copied, setCopied] = React.useState(false);

    const copyToClipboard = async (text: string) => {
        try {
            await navigator.clipboard.writeText(text);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
        }
    };

    const formatMarkdown = (text: string) => {
        // Simple markdown-like formatting
        return text
            .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold mb-4 text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">$1</h1>')
            .replace(/^## (.*$)/gm, '<h2 class="text-xl font-semibold mb-3 text-gray-800 dark:text-gray-200 mt-6">$1</h2>')
            .replace(/^### (.*$)/gm, '<h3 class="text-lg font-medium mb-2 text-gray-700 dark:text-gray-300 mt-4">$1</h3>')
            .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900 dark:text-white">$1</strong>')
            .replace(/\*(.*?)\*/g, '<em class="italic text-gray-700 dark:text-gray-300">$1</em>')
            .replace(/`([^`]+)`/g, '<code class="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded text-sm font-mono text-pink-600 dark:text-pink-400 border">$1</code>')
            .replace(/^- (.*$)/gm, '<li class="ml-4 mb-1 text-gray-700 dark:text-gray-300">• $1</li>')
            .replace(/^\d+\. (.*$)/gm, '<li class="ml-4 mb-1 text-gray-700 dark:text-gray-300 list-decimal">$1</li>')
            .replace(/\n\n/g, '</p><p class="mb-4 text-gray-700 dark:text-gray-300 leading-relaxed">')
            .replace(/^(?!<[h|l|c])/gm, '<p class="mb-4 text-gray-700 dark:text-gray-300 leading-relaxed">');
    };

    return (
        <div className="relative">
            {(title || showCopyButton) && (
                <div className="flex items-center justify-between mb-4 pb-2 border-b border-gray-200 dark:border-gray-700">
                    {title && (
                        <h4 className="text-sm font-semibold text-gray-900 dark:text-white">{title}</h4>
                    )}
                    {showCopyButton && (
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => copyToClipboard(content)}
                            className={`transition-colors ${copied
                                ? 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20'
                                : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                                }`}
                        >
                            {copied ? '✓ Copied!' : '📋 Copy'}
                        </Button>
                    )}
                </div>
            )}
            <div
                className="overflow-y-auto p-4 md:p-6 rounded-2xl border bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700 custom-scrollbar"
                style={{ maxHeight }}
            >
                {isMarkdown ? (
                    <div
                        className="prose prose-sm max-w-none"
                        dangerouslySetInnerHTML={{ __html: formatMarkdown(content) }}
                    />
                ) : (
                    <pre className="whitespace-pre-wrap text-sm text-gray-800 dark:text-gray-200 font-mono leading-relaxed">
                        {content}
                    </pre>
                )}
            </div>
        </div>
    );
};

// Markdown Viewer Component
interface MarkdownViewerProps {
    content: string;
    filename: string;
    theme: 'light' | 'dark';
}

export const MarkdownViewer: React.FC<MarkdownViewerProps> = ({
    content,
    filename,
    theme
}) => {
    const [copied, setCopied] = React.useState(false);

    const copyToClipboard = async (text: string) => {
        try {
            await navigator.clipboard.writeText(text);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
        }
    };

    const copySelection = () => {
        const selection = window.getSelection();
        if (selection && selection.toString().trim()) {
            copyToClipboard(selection.toString());
        }
    };

    return (
        <Card variant="glass" className="p-4 md:p-6 h-full">
            <div className="flex items-center justify-between mb-4 pb-2 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center space-x-3">
                    <div className="p-2 bg-gradient-primary rounded-lg">
                        <FileText className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h3 className={`text-lg font-semibold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                            {filename}
                        </h3>
                        <p className={`text-sm ${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}>
                            Full Markdown Content
                        </p>
                    </div>
                </div>
                <div className="flex space-x-2">
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={copySelection}
                        className={`transition-colors ${copied ? 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20' : ''}`}
                        title="Copy selected text"
                    >
                        {copied ? '✓ Copied!' : '📋 Copy Selection'}
                    </Button>
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => copyToClipboard(content)}
                        title="Copy all content"
                    >
                        📄 Copy All
                    </Button>
                </div>
            </div>

            <div className="overflow-y-auto max-h-[85vh] min-h-[400px] md:min-h-[600px] p-4 md:p-6 rounded-2xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 custom-scrollbar">
                <div className="prose prose-sm max-w-none dark:prose-invert">
                    <ReactMarkdown
                        components={{
                            h1: ({ children }) => (
                                <h1 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2 mt-6 first:mt-0">
                                    {children}
                                </h1>
                            ),
                            h2: ({ children }) => (
                                <h2 className="text-xl font-semibold mb-3 text-gray-800 dark:text-gray-200 mt-6">
                                    {children}
                                </h2>
                            ),
                            h3: ({ children }) => (
                                <h3 className="text-lg font-medium mb-2 text-gray-700 dark:text-gray-300 mt-4">
                                    {children}
                                </h3>
                            ),
                            code: ({ className, children, ...props }) => {
                                const match = /language-(\w+)/.exec(className || '');
                                return match ? (
                                    <pre className="mb-4 p-4 bg-gray-100 dark:bg-gray-800 rounded-xl border overflow-x-auto">
                                        <code className={`${className} text-sm font-mono text-pink-600 dark:text-pink-400`} {...props}>
                                            {children}
                                        </code>
                                    </pre>
                                ) : (
                                    <code className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded-lg text-sm font-mono text-pink-600 dark:text-pink-400 border" {...props}>
                                        {children}
                                    </code>
                                );
                            },
                            blockquote: ({ children }) => (
                                <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-600 dark:text-gray-400 my-4">
                                    {children}
                                </blockquote>
                            ),
                            a: ({ href, children }) => (
                                <a
                                    href={href}
                                    className="text-blue-600 dark:text-blue-400 hover:underline"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    {children}
                                </a>
                            ),
                        }}
                    >
                        {content}
                    </ReactMarkdown>
                </div>
            </div>

            <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
                <p className={`text-xs ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                    💡 Tip: Select any text and click "Copy Selection" to copy portions easily. Use "Copy All" for the entire content.
                </p>
            </div>
        </Card>
    );
};

// Enhanced File Content Item
interface FileContentItemProps {
    url: string;
    content: string;
    theme: 'light' | 'dark';
    onCopyUrl?: (url: string) => void;
    onCopyContent?: (content: string) => void;
}

export const FileContentItem: React.FC<FileContentItemProps> = ({
    url,
    content,
    theme,
    onCopyUrl,
    onCopyContent
}) => {
    const [viewMode, setViewMode] = React.useState<'formatted' | 'raw'>('formatted');
    const [isExpanded, setIsExpanded] = React.useState(true); // Default to expanded
    const [copied, setCopied] = React.useState<{ url: boolean; content: boolean }>({ url: false, content: false });

    const isMarkdown = content.includes('#') || content.includes('**') || content.includes('- ');
    const truncatedContent = isExpanded ? content : content.substring(0, 800);
    const shouldTruncate = content.length > 800;

    const copyToClipboard = async (text: string, type: 'url' | 'content') => {
        try {
            await navigator.clipboard.writeText(text);
            setCopied(prev => ({ ...prev, [type]: true }));
            setTimeout(() => setCopied(prev => ({ ...prev, [type]: false })), 2000);
            if (type === 'url' && onCopyUrl) onCopyUrl(text);
            if (type === 'content' && onCopyContent) onCopyContent(text);
        } catch (err) {
            console.error('Failed to copy text: ', err);
        }
    };

    return (
        <Card variant="default" className="p-4 md:p-6 animate-scale-in">
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                    <div className="w-3 h-3 bg-green-500 rounded-full flex-shrink-0 animate-pulse"></div>
                    <div className="min-w-0 flex-1">
                        <h3 className={`font-medium text-sm mb-1 ${theme === 'dark' ? 'text-blue-400' : 'text-blue-600'
                            }`}>
                            📄 {url.replace(/https?:\/\//, '').split('/').pop() || 'Document'}
                        </h3>
                        <p className={`text-xs truncate ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
                            }`}>
                            {url}
                        </p>
                    </div>
                </div>
                <div className="flex space-x-1 flex-shrink-0">
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setViewMode(viewMode === 'formatted' ? 'raw' : 'formatted')}
                        className={`text-xs px-3 py-1 ${viewMode === 'formatted' ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400' : ''
                            }`}
                    >
                        {viewMode === 'formatted' ? '🔤 Raw' : '✨ Format'}
                    </Button>
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => window.open(url, '_blank')}
                        className="text-xs px-3 py-1"
                    >
                        🔗 Open
                    </Button>
                </div>
            </div>

            <div className="mb-4">
                <div className="flex space-x-2 mb-3">
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => copyToClipboard(url, 'url')}
                        className={`text-xs px-3 py-1 ${copied.url
                            ? 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400'
                            : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                            }`}
                    >
                        {copied.url ? '✅ URL Copied!' : '📋 Copy URL'}
                    </Button>
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => copyToClipboard(content, 'content')}
                        className={`text-xs px-3 py-1 ${copied.content
                            ? 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400'
                            : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                            }`}
                    >
                        {copied.content ? '✅ Content Copied!' : '📝 Copy Content'}
                    </Button>
                    <span className={`text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-800 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'
                        }`}>
                        {content.length.toLocaleString()} chars
                    </span>
                </div>

                <ContentViewer
                    content={shouldTruncate && !isExpanded ? truncatedContent + '\n\n...' : content}
                    isMarkdown={viewMode === 'formatted' && isMarkdown}
                    maxHeight="600px"
                    showCopyButton={false}
                />
            </div>

            {shouldTruncate && (
                <div className="text-center pt-3 border-t border-gray-200 dark:border-gray-700">
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setIsExpanded(!isExpanded)}
                        className="text-xs"
                    >
                        {isExpanded
                            ? '👆 Show Less'
                            : `👇 Show More (+${(content.length - 800).toLocaleString()} characters)`
                        }
                    </Button>
                </div>
            )}
        </Card>
    );
};

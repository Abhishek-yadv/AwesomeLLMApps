import type { Metadata } from "next";
import { Outfit, Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const outfit = Outfit({
    subsets: ["latin"],
    variable: "--font-display",
    weight: ["300", "400", "500", "600", "700", "800"],
});

const plusJakartaSans = Plus_Jakarta_Sans({
    subsets: ["latin"],
    variable: "--font-body",
    weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
    title: "Transcribai - AI Content Extraction",
    description: "Transform YouTube videos into beautifully formatted insights powered by AI.",
    icons: {
        icon: '/favicon.ico',
    },
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en" suppressHydrationWarning>
            <body
                className={`${outfit.variable} ${plusJakartaSans.variable} antialiased`}
                suppressHydrationWarning
            >
                {children}
            </body>
        </html>
    );
}

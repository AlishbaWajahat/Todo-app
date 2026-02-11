import type { Metadata } from "next";
import Script from "next/script";
// Temporarily disabled due to Turbopack font loading issue
// import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/components/auth/AuthProvider";
import { ToastProvider } from "@/components/ui/Toast";

// Temporarily disabled due to Turbopack font loading issue
// const geistSans = Geist({
//   variable: "--font-geist-sans",
//   subsets: ["latin"],
// });

// const geistMono = Geist_Mono({
//   variable: "--font-geist-mono",
//   subsets: ["latin"],
// });

export const metadata: Metadata = {
  title: {
    default: "Todo App - Manage Your Tasks",
    template: "%s | Todo App",
  },
  description: "A modern, multi-user todo application with task management, priorities, and due dates. Built with Next.js and FastAPI.",
  keywords: ["todo", "task management", "productivity", "tasks", "organizer"],
  authors: [{ name: "Todo App Team" }],
  creator: "Todo App Team",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "http://localhost:3000",
    title: "Todo App - Manage Your Tasks",
    description: "A modern, multi-user todo application with task management, priorities, and due dates.",
    siteName: "Todo App",
  },
  twitter: {
    card: "summary_large_image",
    title: "Todo App - Manage Your Tasks",
    description: "A modern, multi-user todo application with task management, priorities, and due dates.",
  },
  viewport: {
    width: "device-width",
    initialScale: 1,
    maximumScale: 1,
  },
  themeColor: "#9B5DE0",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        <AuthProvider>
          <ToastProvider>
            {children}
          </ToastProvider>
        </AuthProvider>
        {/* ChatKit Web Component Script - Required for <openai-chatkit> element */}
        <Script
          src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
          strategy="lazyOnload"
        />
      </body>
    </html>
  );
}

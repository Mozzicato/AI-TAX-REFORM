import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ 
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

export const metadata: Metadata = {
  title: 'AI Tax Reform - Nigerian Tax Assistant | Tax Calculator & Q&A',
  description: 'AI-powered tax assistant for Nigerian tax law. Calculate personal income tax, get answers about the Nigeria Tax Act 2025, and understand tax reliefs and exemptions.',
  keywords: ['Nigerian tax', 'tax calculator', 'Nigeria Tax Act 2025', 'personal income tax', 'FIRS', 'tax relief', 'AI tax assistant'],
  authors: [{ name: 'AI Tax Reform' }],
  openGraph: {
    title: 'AI Tax Reform - Nigerian Tax Assistant',
    description: 'AI-powered tax assistant for Nigerian tax law with calculator and Q&A features.',
    type: 'website',
    locale: 'en_NG',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AI Tax Reform - Nigerian Tax Assistant',
    description: 'AI-powered tax assistant for Nigerian tax law with calculator and Q&A features.',
  },
  robots: {
    index: true,
    follow: true,
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#0284c7',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className={`${inter.className} antialiased`}>{children}</body>
    </html>
  )
}

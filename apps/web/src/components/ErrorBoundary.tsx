'use client'

import { Component, ReactNode } from 'react'
import type { ErrorInfo } from 'react'

interface Props {
    children: ReactNode
    fallback?: ReactNode
}

interface State {
    hasError: boolean
    error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props)
        this.state = { hasError: false }
    }

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error }
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Error caught by boundary:', error, errorInfo)
        // TODO: Send to error tracking service (e.g., Sentry) when implemented
    }

    render() {
        if (this.state.hasError) {
            return this.props.fallback || (
                <div className="min-h-screen flex items-center justify-center bg-gray-50">
                    <div className="max-w-md w-full p-8 bg-white rounded-lg shadow-md">
                        <h1 className="text-2xl font-bold text-gray-900 mb-4">
                            Something went wrong
                        </h1>
                        <p className="text-gray-600 mb-6">
                            We&apos;re sorry for the inconvenience. Please try refreshing the page.
                        </p>
                        <button
                            onClick={() => window.location.reload()}
                            className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                        >
                            Refresh Page
                        </button>
                    </div>
                </div>
            )
        }

        return this.props.children
    }
}

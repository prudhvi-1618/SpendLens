import { useState } from 'react';
import client from '../api/client';

export default function ConnectPage() {
    const [loading, setLoading] = useState(false);

    const handleConnect = async () => {
        try {
            setLoading(true);
            const { data } = await client.get('/auth/google');
            window.location.href = data.url;
        } catch (error) {
            console.error('Failed to initiate auth', error);
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
            <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
                <h2 className="mt-6 text-3xl font-extrabold text-gray-900">SpendLens</h2>
                <p className="mt-2 text-sm text-gray-600">
                    Connect your Gmail to automatically track and categorize your spending.
                </p>
                <div className="mt-8">
                    <button
                        onClick={handleConnect}
                        disabled={loading}
                        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition-colors duration-200"
                    >
                        {loading ? 'Connecting...' : 'Connect Gmail'}
                    </button>
                </div>
            </div>
        </div>
    );
}

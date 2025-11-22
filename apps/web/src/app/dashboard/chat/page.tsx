'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Send, UserCheck, Bot } from 'lucide-react';
import { format } from 'date-fns';

// TODO: Replace with real data from API
const mockConversations = [
    {
        phone: '+5491112345678',
        name: 'Juan Pérez',
        lastMessage: 'Hola, quiero información sobre...',
        timestamp: new Date(),
        unread: 2,
        isHandedOff: false,
    },
    {
        phone: '+5491187654321',
        name: 'María González',
        lastMessage: 'Gracias por la información',
        timestamp: new Date(Date.now() - 3600000),
        unread: 0,
        isHandedOff: true,
    },
];

const mockMessages = [
    {
        id: 1,
        text: 'Hola, quiero información sobre sus productos',
        sender: 'customer',
        timestamp: new Date(Date.now() - 7200000),
    },
    {
        id: 2,
        text: '¡Hola! Claro, con gusto te ayudo. ¿Qué producto te interesa?',
        sender: 'bot',
        timestamp: new Date(Date.now() - 7100000),
    },
    {
        id: 3,
        text: 'Me interesa el plan premium',
        sender: 'customer',
        timestamp: new Date(Date.now() - 3600000),
    },
];

export default function ChatPage() {
    const [selectedConversation, setSelectedConversation] = useState(mockConversations[0]);
    const [message, setMessage] = useState('');
    const [messages, setMessages] = useState(mockMessages);

    // TODO: Connect to real API
    const handleTakeControl = async () => {
        console.log('Taking control of conversation:', selectedConversation.phone);
        // await takeControl(selectedConversation.phone);
    };

    const handleReturnToBot = async () => {
        console.log('Returning conversation to bot:', selectedConversation.phone);
        // await returnToBot(selectedConversation.phone);
    };

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!message.trim()) return;

        console.log('Sending message:', message);
        // TODO: Connect to real API
        // await sendManualMessage(selectedConversation.phone, message);

        // Add message to local state (temporary)
        setMessages([
            ...messages,
            {
                id: messages.length + 1,
                text: message,
                sender: 'agent',
                timestamp: new Date(),
            },
        ]);
        setMessage('');
    };

    return (
        <div className="flex gap-4 h-full">
            {/* Conversations List */}
            <div className="w-80 bg-white rounded-lg shadow-md overflow-hidden">
                <div className="p-4 border-b">
                    <h3 className="font-semibold text-gray-800">Conversations</h3>
                </div>

                <div className="overflow-y-auto" style={{ maxHeight: 'calc(100vh - 200px)' }}>
                    {mockConversations.map((conv) => (
                        <div
                            key={conv.phone}
                            onClick={() => setSelectedConversation(conv)}
                            className={`p-4 border-b cursor-pointer hover:bg-gray-50 transition-colors ${selectedConversation.phone === conv.phone ? 'bg-blue-50' : ''
                                }`}
                        >
                            <div className="flex items-start justify-between">
                                <div className="flex-1">
                                    <div className="flex items-center gap-2">
                                        <h4 className="font-medium text-gray-900">{conv.name}</h4>
                                        {conv.isHandedOff && (
                                            <UserCheck size={16} className="text-green-600" />
                                        )}
                                        {!conv.isHandedOff && (
                                            <Bot size={16} className="text-blue-600" />
                                        )}
                                    </div>
                                    <p className="text-sm text-gray-600 truncate">{conv.lastMessage}</p>
                                    <p className="text-xs text-gray-400 mt-1">
                                        {format(conv.timestamp, 'HH:mm')}
                                    </p>
                                </div>
                                {conv.unread > 0 && (
                                    <span className="bg-blue-600 text-white text-xs rounded-full px-2 py-1">
                                        {conv.unread}
                                    </span>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Chat Panel */}
            <div className="flex-1 bg-white rounded-lg shadow-md flex flex-col">
                {/* Chat Header */}
                <div className="p-4 border-b flex items-center justify-between">
                    <div>
                        <h3 className="font-semibold text-gray-800">{selectedConversation.name}</h3>
                        <p className="text-sm text-gray-600">{selectedConversation.phone}</p>
                    </div>

                    <div className="flex gap-2">
                        {selectedConversation.isHandedOff ? (
                            <Button variant="secondary" onClick={handleReturnToBot}>
                                <Bot size={18} className="mr-2" />
                                Return to Bot
                            </Button>
                        ) : (
                            <Button onClick={handleTakeControl}>
                                <UserCheck size={18} className="mr-2" />
                                Take Control
                            </Button>
                        )}
                    </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {messages.map((msg) => (
                        <div
                            key={msg.id}
                            className={`flex ${msg.sender === 'customer' ? 'justify-start' : 'justify-end'}`}
                        >
                            <div
                                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${msg.sender === 'customer'
                                        ? 'bg-gray-200 text-gray-800'
                                        : msg.sender === 'bot'
                                            ? 'bg-blue-100 text-blue-900'
                                            : 'bg-green-600 text-white'
                                    }`}
                            >
                                <p>{msg.text}</p>
                                <p className="text-xs mt-1 opacity-70">
                                    {format(msg.timestamp, 'HH:mm')}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Message Input */}
                <form onSubmit={handleSendMessage} className="p-4 border-t">
                    <div className="flex gap-2">
                        <input
                            type="text"
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            placeholder="Type a message..."
                            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            disabled={!selectedConversation.isHandedOff}
                        />
                        <Button
                            type="submit"
                            disabled={!selectedConversation.isHandedOff || !message.trim()}
                        >
                            <Send size={18} />
                        </Button>
                    </div>
                    {!selectedConversation.isHandedOff && (
                        <p className="text-xs text-gray-500 mt-2">
                            Take control of the conversation to send messages
                        </p>
                    )}
                </form>
            </div>
        </div>
    );
}

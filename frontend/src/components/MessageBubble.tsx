import React from 'react';

interface Source {
  title: string;
  section?: string;
}

interface MessageBubbleProps {
  message: string;
  isBot: boolean;
  sources?: Array<Source>;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, isBot, sources }) => {
  return (
    <div className={`flex ${isBot ? "justify-start" : "justify-end"} mb-4`}>
      <div
        className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
          isBot
            ? "bg-gray-200 text-gray-900"
            : "bg-blue-600 text-white"
        }`}
      >
        <div className="text-sm whitespace-pre-wrap">{message}</div>

        {/* Show sources for bot messages */}
        {isBot && sources && sources.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-300 text-xs text-gray-600">
            <strong>Sources:</strong>
            {sources.map((source, idx) => (
              <div key={idx} className="text-gray-600 mt-1">
                • {typeof source === 'string' ? source : source.title}
                {typeof source === 'object' && source.section && (
                  <span className="ml-1 text-blue-600 font-medium">({source.section})</span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
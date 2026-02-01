import type { ComparisonQuestion } from '@/types';

interface QuestionCardProps {
  question: ComparisonQuestion;
  index: number;
  selectedChoice: 'a' | 'b' | 'none' | null;
  onSelect: (choice: 'a' | 'b' | 'none') => void;
  disabled?: boolean;
}

// Category icons/labels
const categoryLabels: Record<string, string> = {
  typography: 'Font',
  color: 'Color',
  shape: 'Shape',
  spacing: 'Spacing',
};

export default function QuestionCard({
  question,
  index,
  selectedChoice,
  onSelect,
  disabled,
}: QuestionCardProps) {
  const categoryLabel = categoryLabels[question.category] || question.category;

  return (
    <div
      className={`bg-white rounded-lg p-3 border ${
        disabled ? 'opacity-50' : ''
      }`}
      agent-handle={`extraction-question-${index}`}
    >
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xs font-medium text-gray-400 bg-gray-100 px-2 py-0.5 rounded">
          {categoryLabel}
        </span>
        <span className="text-sm text-gray-700">{question.question_text}</span>
      </div>

      <div className="flex gap-2">
        {/* Option A */}
        <button
          className={`flex-1 py-2 px-3 rounded text-sm font-medium transition-all ${
            selectedChoice === 'a'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
          onClick={() => !disabled && onSelect('a')}
          disabled={disabled}
          agent-handle={`extraction-question-${index}-a`}
        >
          A
        </button>

        {/* Option B */}
        <button
          className={`flex-1 py-2 px-3 rounded text-sm font-medium transition-all ${
            selectedChoice === 'b'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
          onClick={() => !disabled && onSelect('b')}
          disabled={disabled}
          agent-handle={`extraction-question-${index}-b`}
        >
          B
        </button>

        {/* Either/No Preference */}
        <button
          className={`py-2 px-3 rounded text-sm font-medium transition-all ${
            selectedChoice === 'none'
              ? 'bg-gray-500 text-white'
              : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
          }`}
          onClick={() => !disabled && onSelect('none')}
          disabled={disabled}
          agent-handle={`extraction-question-${index}-none`}
        >
          Either
        </button>
      </div>
    </div>
  );
}

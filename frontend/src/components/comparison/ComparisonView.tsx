import { useState, useEffect } from 'react';
import type { Comparison, QuestionAnswer } from '@/types';
import { Button } from '@/components/ui/shadcn/Button';
import ComponentRenderer from './ComponentRenderer';
import QuestionCard from './QuestionCard';

interface ComparisonViewProps {
  comparison: Comparison;
  onChoice: (choice: 'a' | 'b' | 'none', answers?: QuestionAnswer[]) => void;
  disabled?: boolean;
}

export default function ComparisonView({
  comparison,
  onChoice,
  disabled,
}: ComparisonViewProps) {
  // Track answers for multi-question mode
  const [answers, setAnswers] = useState<Record<string, 'a' | 'b' | 'none'>>({});

  // Reset answers when comparison changes
  useEffect(() => {
    setAnswers({});
  }, [comparison.comparison_id]);

  // Check if multi-question mode (has questions array)
  const hasQuestions = comparison.questions && comparison.questions.length > 0;

  // Check if all questions are answered
  const allQuestionsAnswered = hasQuestions
    ? comparison.questions!.every((q) => answers[q.property] !== undefined)
    : true;

  // Handle question answer
  const handleQuestionAnswer = (property: string, choice: 'a' | 'b' | 'none') => {
    setAnswers((prev) => ({ ...prev, [property]: choice }));
  };

  // Handle submit (multi-question mode)
  const handleSubmit = () => {
    if (!hasQuestions) return;

    // Convert answers to QuestionAnswer array
    const answerArray: QuestionAnswer[] = comparison.questions!.map((q) => ({
      category: q.category,
      property: q.property,
      choice: answers[q.property] || 'none',
    }));

    // Determine overall choice based on majority of answers
    const counts = { a: 0, b: 0, none: 0 };
    answerArray.forEach((a) => counts[a.choice]++);

    let overallChoice: 'a' | 'b' | 'none' = 'none';
    if (counts.a > counts.b && counts.a > counts.none) overallChoice = 'a';
    else if (counts.b > counts.a && counts.b > counts.none) overallChoice = 'b';

    onChoice(overallChoice, answerArray);
  };

  // Handle legacy single-choice click
  const handleLegacyChoice = (choice: 'a' | 'b' | 'none') => {
    if (hasQuestions) {
      // In multi-question mode, clicking option sets all answers to that choice
      const newAnswers: Record<string, 'a' | 'b' | 'none'> = {};
      comparison.questions!.forEach((q) => {
        newAnswers[q.property] = choice;
      });
      setAnswers(newAnswers);
    } else {
      // Legacy mode: immediate submit
      onChoice(choice);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      {/* Options - Visual comparison */}
      <div className="flex-1 grid grid-cols-2 gap-1 p-1">
        {/* Option A */}
        <div
          className={`bg-white rounded-lg overflow-hidden cursor-pointer transition-all hover:ring-2 hover:ring-primary ${
            disabled ? 'opacity-50 pointer-events-none' : ''
          }`}
          onClick={() => !disabled && handleLegacyChoice('a')}
          agent-handle="extraction-comparison-option-a"
        >
          <div className="h-full p-4 flex flex-col">
            <div className="text-sm font-medium text-gray-500 mb-2 text-center">
              Option A
            </div>
            <div className="flex-1 flex items-center justify-center">
              <ComponentRenderer
                componentType={comparison.component_type}
                styles={comparison.option_a.styles}
                context={comparison.context}
              />
            </div>
          </div>
        </div>

        {/* Option B */}
        <div
          className={`bg-white rounded-lg overflow-hidden cursor-pointer transition-all hover:ring-2 hover:ring-primary ${
            disabled ? 'opacity-50 pointer-events-none' : ''
          }`}
          onClick={() => !disabled && handleLegacyChoice('b')}
          agent-handle="extraction-comparison-option-b"
        >
          <div className="h-full p-4 flex flex-col">
            <div className="text-sm font-medium text-gray-500 mb-2 text-center">
              Option B
            </div>
            <div className="flex-1 flex items-center justify-center">
              <ComponentRenderer
                componentType={comparison.component_type}
                styles={comparison.option_b.styles}
                context={comparison.context}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Multi-question cards */}
      {hasQuestions && (
        <div className="p-4 bg-gray-50 border-t space-y-2" agent-handle="extraction-questions">
          <div className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
            Answer each question
          </div>
          {comparison.questions!.map((question, index) => (
            <QuestionCard
              key={question.property}
              question={question}
              index={index}
              selectedChoice={answers[question.property] || null}
              onSelect={(choice) => handleQuestionAnswer(question.property, choice)}
              disabled={disabled}
            />
          ))}
        </div>
      )}

      {/* Bottom action bar */}
      <div className="p-4 bg-white border-t flex justify-between items-center">
        {hasQuestions ? (
          <>
            <Button
              variant="ghost"
              onClick={() => !disabled && handleLegacyChoice('none')}
              disabled={disabled}
              agent-handle="extraction-comparison-button-nopreference"
            >
              No Preference (All)
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={disabled || !allQuestionsAnswered}
              agent-handle="extraction-comparison-button-continue"
            >
              Continue ({Object.keys(answers).length}/{comparison.questions!.length})
            </Button>
          </>
        ) : (
          <div className="w-full text-center">
            <Button
              variant="ghost"
              onClick={() => !disabled && onChoice('none')}
              disabled={disabled}
              agent-handle="extraction-comparison-button-nopreference"
            >
              No Preference
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}

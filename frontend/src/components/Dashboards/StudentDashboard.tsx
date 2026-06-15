'use client';

import React, { useState } from 'react';
import { BookOpen, GraduationCap, ChevronLeft, ChevronRight, CheckCircle2, XCircle, Award } from 'lucide-react';

interface LessonSlide {
  title: string;
  content: string;
  concept: string;
  illustration: string[];
}

interface LessonTopic {
  id: string;
  title: string;
  icon: string;
  shortDesc: string;
  slides: LessonSlide[];
  quiz: {
    question: string;
    options: string[];
    correctIndex: number;
    explanation: string;
  };
}

const LESSON_TOPICS: LessonTopic[] = [
  {
    id: 'inflation',
    title: 'Understanding Inflation & Prices',
    icon: '📈',
    shortDesc: 'Learn how CPI/WPI measures money value degradation.',
    slides: [
      {
        title: 'What is Inflation?',
        concept: 'Beginner',
        content: 'Inflation is the rate at which the general level of prices for goods and services is rising, and subsequently, purchasing power is falling. In India, retail inflation is tracked by the Consumer Price Index (CPI), compiled monthly by MoSPI.',
        illustration: [
          '🛍️ Basket of Goods (100 INR in 2020)',
          '⬇️ Same Basket costs 125 INR in 2025',
          '📉 Real purchasing value of money has dropped by 20%!'
        ]
      },
      {
        title: 'Demand-Pull vs. Cost-Push',
        concept: 'Intermediate',
        content: 'Demand-Pull occurs when consumer demand grows faster than production capacities ("too much money chasing too few goods"). Cost-Push is triggered when raw material costs spike, e.g., Brent Crude surging due to Middle East geopolitics, forcing producers to raise prices.',
        illustration: [
          '🔥 Demand-Pull: Low EMIs -> high spending -> prices surge',
          '⚡ Cost-Push: High oil -> transport costs rise -> food prices rise',
          '🇮🇳 India imported inflation is mostly Cost-Push (Crude Oil)!'
        ]
      }
    ],
    quiz: {
      question: 'Which index is primarily used by the RBI Monetary Policy Committee to target inflation in India?',
      options: [
        'Wholesale Price Index (WPI)',
        'Consumer Price Index (CPI)',
        'Gross Domestic Product Deflator',
        'Index of Industrial Production (IIP)'
      ],
      correctIndex: 1,
      explanation: 'The RBI transitioned to targeting CPI (Retail) inflation in 2014 under Governor Raghuram Rajan, as it directly reflects the cost-of-living impacts on everyday households.'
    }
  },
  {
    id: 'monetary',
    title: 'Monetary Policy & Central Banking',
    icon: '🏦',
    shortDesc: 'Understand how RBI manages interest rates and liquidity.',
    slides: [
      {
        title: 'The Role of the RBI',
        concept: 'Beginner',
        content: 'The Reserve Bank of India (RBI) controls monetary liquidity to ensure price stability while supporting growth. Its primary tool is the Repo Rate—the rate at which commercial banks borrow money from the central bank.',
        illustration: [
          '🏦 RBI Repo Rate: 6.50% (Borrowing baseline)',
          '➡️ Commercial Banks: Lending rate rises to 9% (EMIs grow)',
          '🛑 Result: Credit slows down, anchoring high inflation.'
        ]
      },
      {
        title: 'Transmission Stance',
        concept: 'Advanced',
        content: 'When RBI hikes the repo rate, it takes time for retail banks to transmit the hike to consumers (interest rate transmission lag). The MPC communicates its stance (e.g. "Accommodative" meaning cuts are likely, or "Withdrawal of Accommodation" meaning rates will remain high or rise).',
        illustration: [
          '📢 MPC Stance: "Withdrawal of Accommodation" (High Rates Stance)',
          '⌛ Transmission Lag: Takes 3-6 months to hit home loan EMIs',
          '📉 Yield Curve: Bond market yields shift instantly.'
        ]
      }
    ],
    quiz: {
      question: 'When the RBI hikes the Repo Rate, what is the typical consequence on corporate profits and stock markets?',
      options: [
        'Corporate borrowing costs drop, leading to stock market rallies.',
        'Corporate borrowing costs rise, discounting future earnings at a higher rate and depressing stock valuations.',
        'Foreign capital flows out of India instantly, lowering inflation but boosting exporters.',
        'No direct impact; stock markets are independent of policy rates.'
      ],
      correctIndex: 1,
      explanation: 'A rate hike increases interest expenses for corporations, shrinking net margins, while raising the equity discount rate, which compresses stock valuation multiples (P/E).'
    }
  },
  {
    id: 'geopolitics',
    title: 'Geopolitical Shocks & India',
    icon: '🌍',
    shortDesc: 'Trace how international conflicts disrupt local pocketbooks.',
    slides: [
      {
        title: 'The Energy Channel',
        concept: 'Beginner',
        content: 'India imports over 80% of its crude oil. When geopolitical conflicts occur in oil-producing regions (Middle East), supply routes face risk premiums. Crude prices rise, forcing India to spend foreign exchange (USD), weakening the Rupee.',
        illustration: [
          '🚢 Strait of Hormuz: High risk premium',
          '💸 Oil surges to $100/barrel',
          '🇮🇳 Rupee depreciates to purchase high-cost fuel imports'
        ]
      },
      {
        title: 'Global Supply Chain Chains',
        concept: 'Intermediate',
        content: 'Geopolitics also triggers supply chain disruptions. Tensions around shipping corridors (e.g., Suez Canal rerouting via South Africa) increase container freight shipping rates. This adds "freight inflation" to import items like semiconductors, fertilizers, and technology components.',
        illustration: [
          '⚓ Suez Canal disruption -> cargo ships rerouted around Africa (+14 days)',
          '📦 Container rates jump 300%',
          '🔋 Local electronics and car makers face components delays and cost hikes'
        ]
      }
    ],
    quiz: {
      question: 'Why does a Middle East conflict often weaken the Indian Rupee against the US Dollar?',
      options: [
        'FII capital flows into India increase due to safe-haven status.',
        'India’s oil import bill surges, necessitating massive dollar purchases to pay global oil markets.',
        'The US Federal Reserve automatically cuts interest rates during oil shocks.',
        'Gold prices plummet, causing capital flights.'
      ],
      correctIndex: 1,
      explanation: 'Oil is priced in USD. When oil surges, India’s oil marketing firms must buy massive volumes of US Dollars to pay for imports, creating strong selling pressure on the Rupee.'
    }
  }
];

export default function StudentDashboard() {
  const [activeTopicIdx, setActiveTopicIdx] = useState(0);
  const [currentSlideIdx, setCurrentSlideIdx] = useState(0);
  
  // Quiz state
  const [selectedAnsIdx, setSelectedAnsIdx] = useState<number | null>(null);
  const [quizSubmitted, setQuizSubmitted] = useState(false);
  const [quizScore, setQuizScore] = useState<Record<string, boolean>>({});

  const topic = LESSON_TOPICS[activeTopicIdx];
  const slideCount = topic.slides.length;
  // Total steps in lesson = slides count + 1 quiz step
  const totalSteps = slideCount + 1;

  const handleNext = () => {
    if (currentSlideIdx < totalSteps - 1) {
      setCurrentSlideIdx(prev => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentSlideIdx > 0) {
      setCurrentSlideIdx(prev => prev - 1);
    }
  };

  const handleTopicChange = (idx: number) => {
    setActiveTopicIdx(idx);
    setCurrentSlideIdx(0);
    setSelectedAnsIdx(null);
    setQuizSubmitted(false);
  };

  const handleAnswerSelect = (idx: number) => {
    if (quizSubmitted) return;
    setSelectedAnsIdx(idx);
  };

  const submitQuiz = () => {
    if (selectedAnsIdx === null) return;
    setQuizSubmitted(true);
    const isCorrect = selectedAnsIdx === topic.quiz.correctIndex;
    setQuizScore(prev => ({ ...prev, [topic.id]: isCorrect }));
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-3 h-full overflow-y-auto pr-1">
      {/* Topics Sidebar Left Panel */}
      <div className="border border-gray-800 rounded bg-[#090d16]/30 p-2.5 flex flex-col gap-2 lg:col-span-1 min-h-[200px]">
        <h3 className="text-[10px] text-gray-500 font-bold uppercase tracking-wider mb-1.5 flex items-center">
          <GraduationCap className="w-4 h-4 text-emerald-500 mr-1.5" />
          STUDENT LEARNING SYLLABUS
        </h3>
        
        <div className="space-y-1.5 flex-1">
          {LESSON_TOPICS.map((t, idx) => {
            const isSelected = activeTopicIdx === idx;
            const completed = quizScore[t.id] !== undefined;
            const correct = quizScore[t.id] === true;

            return (
              <div
                key={t.id}
                onClick={() => handleTopicChange(idx)}
                className={`p-2 rounded cursor-pointer transition-colors border flex items-start justify-between ${
                  isSelected ? 'bg-emerald-600/15 border-emerald-500/50' : 'bg-gray-950/20 border-transparent hover:bg-gray-800/30'
                }`}
              >
                <div className="flex gap-2">
                  <span className="text-sm">{t.icon}</span>
                  <div className="flex flex-col">
                    <span className="text-[10.5px] font-bold text-gray-250 leading-tight">{t.title}</span>
                    <span className="text-[8px] text-gray-500 font-sans mt-0.5">{t.shortDesc}</span>
                  </div>
                </div>
                {completed && (
                  <span className="ml-1">
                    {correct ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    ) : (
                      <XCircle className="w-3.5 h-3.5 text-red-400" />
                    )}
                  </span>
                )}
              </div>
            );
          })}
        </div>
        
        {/* Progress box */}
        <div className="border-t border-gray-900 pt-2 flex items-center justify-between text-[10px] text-gray-500">
          <span>Syllabus Completed:</span>
          <span className="text-emerald-400 font-bold">
            {Object.keys(quizScore).length} / {LESSON_TOPICS.length} Lessons
          </span>
        </div>
      </div>

      {/* Main Interactive Slide Screen Panel */}
      <div className="lg:col-span-3 flex flex-col gap-3 min-h-[350px]">
        <div className="terminal-panel p-4 flex-1 flex flex-col justify-between bg-gradient-to-br from-[#0a0f1d] to-[#04080e]">
          
          {/* Header */}
          <div className="flex items-center justify-between border-b border-gray-850 pb-2 mb-3">
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] text-emerald-400 bg-emerald-950/50 border border-emerald-900/40 px-1.5 py-0.2 rounded font-bold uppercase">
                {currentSlideIdx < slideCount ? topic.slides[currentSlideIdx].concept : 'EXAMINATION'}
              </span>
              <span className="text-gray-300 font-bold text-xs uppercase">{topic.title}</span>
            </div>
            <span className="text-[9px] text-gray-500">
              Step {currentSlideIdx + 1} of {totalSteps}
            </span>
          </div>

          {/* Slide Body */}
          <div className="flex-1 my-2 grid grid-cols-1 md:grid-cols-5 gap-4">
            
            {/* Slide Text Content */}
            <div className="md:col-span-3 flex flex-col justify-center gap-3">
              {currentSlideIdx < slideCount ? (
                // Educational slide content
                <div>
                  <h3 className="text-sm font-bold text-gray-150 mb-2">
                    {topic.slides[currentSlideIdx].title}
                  </h3>
                  <p className="text-gray-400 text-xs leading-relaxed">
                    {topic.slides[currentSlideIdx].content}
                  </p>
                </div>
              ) : (
                // Quiz Question content
                <div>
                  <h3 className="text-sm font-bold text-yellow-400 mb-2.5 flex items-center">
                    <Award className="w-4.5 h-4.5 mr-1.5 text-yellow-400" />
                    Interactive Quiz Challenge
                  </h3>
                  <p className="text-gray-350 text-xs font-semibold leading-relaxed mb-3">
                    {topic.quiz.question}
                  </p>
                  
                  {/* Options */}
                  <div className="space-y-1.5">
                    {topic.quiz.options.map((opt, oIdx) => {
                      const isSelected = selectedAnsIdx === oIdx;
                      const showCorrect = quizSubmitted && oIdx === topic.quiz.correctIndex;
                      const showIncorrect = quizSubmitted && isSelected && oIdx !== topic.quiz.correctIndex;

                      let btnBorder = 'border-gray-800 hover:bg-gray-800/20 text-gray-400';
                      if (isSelected) btnBorder = 'border-yellow-500 text-yellow-300 bg-yellow-500/5';
                      if (showCorrect) btnBorder = 'border-emerald-500 text-emerald-400 bg-emerald-950/20 font-bold';
                      if (showIncorrect) btnBorder = 'border-red-500 text-red-400 bg-red-955/20';

                      return (
                        <button
                          key={oIdx}
                          disabled={quizSubmitted}
                          onClick={() => handleAnswerSelect(oIdx)}
                          className={`w-full text-left p-2 border rounded text-xs transition-colors font-mono flex items-center justify-between ${btnBorder}`}
                        >
                          <span>{opt}</span>
                          {showCorrect && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                          {showIncorrect && <XCircle className="w-3.5 h-3.5 text-red-400" />}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>

            {/* Slide Visual Illustration Side */}
            <div className="md:col-span-2 border border-gray-850 bg-gray-950/45 rounded p-3 flex flex-col justify-center">
              {currentSlideIdx < slideCount ? (
                // Graphic layout
                <div className="space-y-3">
                  <span className="text-[9px] text-gray-500 font-bold uppercase tracking-wider block">
                    Macro Visualization:
                  </span>
                  <div className="space-y-2.5 text-[11px] font-sans">
                    {topic.slides[currentSlideIdx].illustration.map((item, i) => (
                      <div key={i} className="bg-[#0c1322] border border-gray-900/80 rounded p-2 text-gray-300 leading-normal">
                        {item}
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                // Quiz result & feedback
                <div className="space-y-3">
                  <span className="text-[9px] text-gray-500 font-bold uppercase tracking-wider block">
                    Evaluation Feedback:
                  </span>
                  {quizSubmitted ? (
                    <div className="space-y-2 text-xs">
                      <span className={`font-bold block ${selectedAnsIdx === topic.quiz.correctIndex ? 'text-emerald-400' : 'text-red-400'}`}>
                        {selectedAnsIdx === topic.quiz.correctIndex ? 'Correct Answer! +10 Points' : 'Incorrect Answer.'}
                      </span>
                      <p className="text-gray-400 leading-normal text-[11px] font-sans">
                        {topic.quiz.explanation}
                      </p>
                    </div>
                  ) : (
                    <div className="text-center py-6 text-gray-500 text-[10px] leading-normal font-sans">
                      Select your answer on the left and press "Submit Assessment" to check your economic understanding.
                    </div>
                  )}
                </div>
              )}
            </div>

          </div>

          {/* Navigation controls */}
          <div className="flex justify-between items-center border-t border-gray-850 pt-2.5 mt-3">
            <button
              onClick={handlePrev}
              disabled={currentSlideIdx === 0}
              className="flex items-center gap-1 text-[10px] font-bold text-gray-400 disabled:opacity-30 disabled:cursor-not-allowed hover:text-gray-200"
            >
              <ChevronLeft className="w-4 h-4" /> Previous Step
            </button>

            {currentSlideIdx < totalSteps - 1 ? (
              <button
                onClick={handleNext}
                className="flex items-center gap-1 text-[10px] font-bold text-emerald-400 hover:text-emerald-350"
              >
                Next Step <ChevronRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={submitQuiz}
                disabled={selectedAnsIdx === null || quizSubmitted}
                className="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 text-white rounded text-[10px] font-bold uppercase transition-colors disabled:opacity-35 disabled:cursor-not-allowed"
              >
                Submit Assessment
              </button>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}

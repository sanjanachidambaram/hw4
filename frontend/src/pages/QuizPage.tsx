// "Find your fit" quiz. Three button questions, then matching products.
// No AI: the backend just filters the catalogue (GET /api/quiz/results).
import { useEffect, useState } from "react";
import { fetchQuizOptions, fetchQuizResults, type QuizItem, type QuizOptions } from "../api";
import ProductCard from "../components/ProductCard";
import type { CardProduct } from "../types";

type Answers = { kind: string; color: string; budget: string };
type Field = keyof Answers;

const ANY = "any";
const STEPS: { field: Field; question: string; anyLabel: string }[] = [
  { field: "kind", question: "What are you looking for?", anyLabel: "Surprise me" },
  { field: "color", question: "Pick a color", anyLabel: "No preference" },
  { field: "budget", question: "What's your budget?", anyLabel: "Any price" },
];

/** How many products match the answers so far plus one more choice. */
function countMatches(items: QuizItem[], answers: Partial<Answers>): number {
  return items.filter((item) =>
    (Object.entries(answers) as [Field, string][]).every(
      ([field, value]) => value === ANY || item[field] === value,
    ),
  ).length;
}

export default function QuizPage() {
  const [options, setOptions] = useState<QuizOptions | null>(null);
  const [answers, setAnswers] = useState<Partial<Answers>>({});
  const [results, setResults] = useState<CardProduct[] | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetchQuizOptions().then(setOptions).catch(() => setError(true));
  }, []);

  const step = STEPS.findIndex((s) => !(s.field in answers));
  const done = step === -1;

  // Once all three are answered, ask the backend for the matching products.
  useEffect(() => {
    if (!done) return;
    setResults(null);
    fetchQuizResults(answers as Answers)
      .then(setResults)
      .catch(() => setError(true));
  }, [done, answers]);

  function startOver() {
    setAnswers({});
    setResults(null);
    setError(false);
  }

  if (error) {
    return (
      <div className="quiz">
        <p className="error">Sorry, the quiz couldn't load. Please try again.</p>
        <button type="button" className="quiz-restart" onClick={startOver}>
          Start over
        </button>
      </div>
    );
  }
  if (!options) return <p className="muted">Loading the quiz…</p>;

  const choicesFor = (field: Field) =>
    field === "kind" ? options.kinds : field === "color" ? options.colors : options.budgets;

  return (
    <div className="quiz">
      <h1>Find your fit</h1>
      <p className="muted">Three quick questions and we'll pick out Campus Customs gear for you.</p>

      {!done && (
        <section className="quiz-card">
          <p className="quiz-progress">
            Question {step + 1} of {STEPS.length}
          </p>
          <h2>{STEPS[step].question}</h2>
          <div className="quiz-choices">
            {[...choicesFor(STEPS[step].field), ANY].map((choice) => {
              const field = STEPS[step].field;
              const count = countMatches(options.items, { ...answers, [field]: choice });
              return (
                <button
                  key={choice}
                  type="button"
                  disabled={count === 0}
                  onClick={() => setAnswers((a) => ({ ...a, [field]: choice }))}
                >
                  {choice === ANY ? STEPS[step].anyLabel : choice}
                  <span className="quiz-count">{count === 0 ? "none" : `${count} ${count === 1 ? "item" : "items"}`}</span>
                </button>
              );
            })}
          </div>
          {step > 0 && (
            <button
              type="button"
              className="quiz-back"
              onClick={() =>
                setAnswers((a) => {
                  const copy = { ...a };
                  delete copy[STEPS[step - 1].field];
                  return copy;
                })
              }
            >
              ← Back
            </button>
          )}
        </section>
      )}

      {done && (
        <section>
          <p className="quiz-summary">
            {STEPS.map((s) => (answers[s.field] === ANY ? s.anyLabel : answers[s.field])).join(" · ")}
          </p>
          {results === null ? (
            <p className="muted">Finding your picks…</p>
          ) : results.length === 0 ? (
            <div className="empty-state">
              <p>We don't have anything matching all of those right now. Try a different color or budget!</p>
            </div>
          ) : (
            <>
              <h2>
                Your picks ({results.length})
              </h2>
              <div className="product-grid">
                {results.map((p) => (
                  <ProductCard key={p.product_id} product={p} />
                ))}
              </div>
            </>
          )}
          <button type="button" className="quiz-restart" onClick={startOver}>
            Start over
          </button>
        </section>
      )}
    </div>
  );
}

import { useMutation, useQuery } from "@tanstack/react-query";
import { type FormEvent, useEffect, useRef, useState } from "react";

import {
  askHalQuestion,
  createHalConversationId,
  executeMonitorReviewAction,
  fetchFinancialSummary,
} from "../api/client";

const HAL_SPEECH_VOICE_KEY = "halSpeechVoice";
const HAL_SPEECH_RATE_KEY = "halSpeechRate";

function humanizeLabel(value: string) {
  return value.replaceAll("_", " ");
}

function humanizeLaneLabel(value: string) {
  return value.replaceAll("_", " ");
}

function humanizeGuardrail(flag: string) {
  switch (flag) {
    case "approved local read-only scope":
      return "Uses only approved local read-only data";
    case "deterministic server facts first":
      return "Starts with verified system facts";
    case "sanitized retrieval only":
      return "Uses sanitized retrieval only";
    case "read-only data boundary":
      return "Stays inside a read-only data boundary";
    case "approved summary queries only":
      return "Uses approved summary queries only";
    case "truthful runtime claims only":
      return "Describes runtime status only when the backend verified it";
    case "audit log recorded":
      return "Records an audit trail";
    case "hardware mutations require human confirmation":
      return "Any hardware change still needs your approval";
    case "tier-1 critical actions require explicit confirmation":
      return "Critical actions stay proposal-only until you confirm them";
    case "tier-2 mismatches raise [ALERT]":
      return "Raises an alert when reviewed facts do not line up";
    case "tier-3 assistance stays concise":
      return "Keeps routine help brief";
    case "raw identifiers processed only in local patient tool":
      return "Raw patient identifiers stay inside the local patient tool";
    default:
      return flag;
  }
}

function getSpeechSynthesis(): SpeechSynthesis | null {
  if (typeof window === "undefined" || !("speechSynthesis" in window)) {
    return null;
  }
  return window.speechSynthesis;
}

function isAutomatedBrowserSession(): boolean {
  return typeof navigator !== "undefined" && navigator.webdriver;
}

export default function AskHal9000Page() {
  const [question, setQuestion] = useState("");
  const [lastRequestLane, setLastRequestLane] = useState<"primary" | "second_opinion">("primary");
  const [speechError, setSpeechError] = useState<string | null>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [speechRate, setSpeechRate] = useState(() => {
    if (typeof window === "undefined") {
      return 1;
    }
    const savedRate = Number(window.localStorage.getItem(HAL_SPEECH_RATE_KEY));
    return Number.isFinite(savedRate) && savedRate >= 0.7 && savedRate <= 1.4 ? savedRate : 1;
  });
  const [availableVoices, setAvailableVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoiceName, setSelectedVoiceName] = useState(() => {
    if (typeof window === "undefined") {
      return "";
    }
    return window.localStorage.getItem(HAL_SPEECH_VOICE_KEY) || "";
  });
  const askInFlightRef = useRef(false);
  const conversationIdRef = useRef(createHalConversationId());
  const financialSummaryQuery = useQuery({
    queryKey: ["financial-summary"],
    queryFn: fetchFinancialSummary,
  });
  const halMutation = useMutation({
    mutationFn: ({ nextQuestion, lane }: { nextQuestion: string; lane: "primary" | "second_opinion" }) =>
      askHalQuestion(nextQuestion, {
        summary: financialSummaryQuery.data ?? null,
        lane,
        conversationId: conversationIdRef.current,
      }),
    onSettled: () => {
      askInFlightRef.current = false;
    },
  });
  const actionMutation = useMutation({
    mutationFn: executeMonitorReviewAction,
  });

  function submitHalQuestion(lane: "primary" | "second_opinion") {
    if (!question.trim() || halMutation.isPending || askInFlightRef.current) {
      return;
    }
    askInFlightRef.current = true;
    setLastRequestLane(lane);
    actionMutation.reset();
    setSpeechError(null);
    setIsSpeaking(false);
    halMutation.mutate({ nextQuestion: question.trim(), lane });
  }

  function handleAsk(e: FormEvent) {
    e.preventDefault();
    submitHalQuestion("primary");
  }

  function handleSecondOpinionAsk() {
    submitHalQuestion("second_opinion");
  }

  function handleRetryAsk() {
    submitHalQuestion(lastRequestLane);
  }

  const response = halMutation.data;
  const reviewAction = response?.review_actions.find((item) => item.action_type === "SET_LUMINANCE");

  useEffect(() => {
    if (isAutomatedBrowserSession()) {
      return;
    }

    const synthesis = getSpeechSynthesis();
    if (!synthesis) {
      return;
    }

    const syncVoices = () => {
      const voices = synthesis.getVoices();
      setAvailableVoices(voices);
      setSelectedVoiceName((currentName) => {
        if (currentName && voices.some((voice) => voice.name === currentName)) {
          return currentName;
        }
        if (typeof window !== "undefined") {
          const savedVoice = window.localStorage.getItem(HAL_SPEECH_VOICE_KEY);
          if (savedVoice && voices.some((voice) => voice.name === savedVoice)) {
            return savedVoice;
          }
        }
        const chromeVoice = voices.find((voice) => /google|chrome/i.test(`${voice.name} ${voice.voiceURI}`));
        return chromeVoice?.name || voices[0]?.name || "";
      });
    };

    syncVoices();
    synthesis.onvoiceschanged = syncVoices;

    return () => {
      synthesis.onvoiceschanged = null;
      synthesis.cancel();
    };
  }, []);

  useEffect(() => {
    if (isAutomatedBrowserSession()) {
      return;
    }

    return () => {
      const synthesis = getSpeechSynthesis();
      if (synthesis) {
        synthesis.cancel();
      }
    };
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    if (!selectedVoiceName) {
      window.localStorage.removeItem(HAL_SPEECH_VOICE_KEY);
      return;
    }
    window.localStorage.setItem(HAL_SPEECH_VOICE_KEY, selectedVoiceName);
  }, [selectedVoiceName]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    window.localStorage.setItem(HAL_SPEECH_RATE_KEY, speechRate.toString());
  }, [speechRate]);

  function handleSpeakResponse() {
    if (!response?.answer) {
      return;
    }
    const synthesis = getSpeechSynthesis();
    if (!synthesis || typeof SpeechSynthesisUtterance === "undefined") {
      setSpeechError("Chrome speech is unavailable in this browser session.");
      return;
    }

    synthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(response.answer);
    utterance.rate = speechRate;
    const selectedVoice = availableVoices.find((voice) => voice.name === selectedVoiceName);
    if (selectedVoice) {
      utterance.voice = selectedVoice;
    }
    utterance.onstart = () => {
      setSpeechError(null);
      setIsSpeaking(true);
    };
    utterance.onend = () => {
      setIsSpeaking(false);
    };
    utterance.onerror = () => {
      setIsSpeaking(false);
      setSpeechError("Chrome could not speak the HAL response.");
    };
    synthesis.speak(utterance);
  }

  function handleStopSpeaking() {
    const synthesis = getSpeechSynthesis();
    if (!synthesis) {
      return;
    }
    synthesis.cancel();
    setIsSpeaking(false);
  }

  function handleApproveDisplayAdjustment() {
    if (!reviewAction) {
      return;
    }

    actionMutation.mutate({
      action_type: reviewAction.action_type,
      target_value: reviewAction.target_value,
      human_review_required: reviewAction.human_review_required,
      status: reviewAction.status,
      user_confirmed: true,
    });
  }

  return (
    <div className="dashboard-page dashboard-page--hal">
      <div className="page-content">
        <header className="page-header">
          <p className="eyebrow">Dashboard / HAL Workspace</p>
          <h1>Ask HAL</h1>
          <p>
            Ask HAL a question in plain language. HAL answers from the verified information on this system, and anything that could change
            hardware still waits for your approval first.
          </p>
        </header>
        <form className="hal-form hal-form--narrative" onSubmit={handleAsk}>
          <label htmlFor="hal-question">What do you want HAL to help with?</label>
          <textarea
            className="hal-form__textarea"
            id="hal-question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={4}
            placeholder="e.g. What needs my attention today, or lower the primary monitor brightness to 30%."
            required
          />
          <br />
          <div className="hal-form__actions">
            <button type="submit" className="refresh-button" disabled={!question.trim() || halMutation.isPending}>
              {halMutation.isPending && lastRequestLane === "primary" ? "Asking HAL..." : "Ask HAL"}
            </button>
            <button
              type="button"
              className="refresh-button"
              onClick={handleSecondOpinionAsk}
              disabled={!question.trim() || halMutation.isPending}
            >
              {halMutation.isPending && lastRequestLane === "second_opinion" ? "Getting second opinion..." : "Get second opinion"}
            </button>
          </div>
        </form>

        {halMutation.isError && (
          <div className="hal-answer-card">
            <h2>That request did not go through</h2>
            <div>{halMutation.error instanceof Error ? halMutation.error.message : "HAL could not finish that request."}</div>
            <button type="button" className="refresh-button" onClick={handleRetryAsk} disabled={!question.trim() || halMutation.isPending}>
              {halMutation.isPending ? "Retrying..." : "Try Again"}
            </button>
          </div>
        )}

        {response && (
          <div className="hal-answer-card">
            <h2>HAL's Response</h2>
            <div className="hal-answer-card__section">
              <strong>Review depth:</strong> {lastRequestLane === "second_opinion" ? "Second opinion" : "Primary response"}
            </div>
            <div className="hal-answer-card__section">
              <strong>Response profile:</strong> {response.voice_profile.label} · {response.voice_profile.tone}
            </div>
            <div className="hal-answer-card__section hal-answer-card__section--lead">{response.answer}</div>
            <div className="hal-answer-card__section">
              <label htmlFor="hal-response-voice">Voice</label>
              <select
                id="hal-response-voice"
                className="hal-form__textarea"
                value={selectedVoiceName}
                onChange={(event) => setSelectedVoiceName(event.target.value)}
              >
                {availableVoices.length === 0 ? <option value="">Browser default</option> : null}
                {availableVoices.map((voice) => (
                  <option key={`${voice.name}-${voice.lang}`} value={voice.name}>
                    {voice.name} ({voice.lang})
                  </option>
                ))}
              </select>
              <label htmlFor="hal-response-rate">Speech rate</label>
              <input
                id="hal-response-rate"
                type="range"
                min="0.7"
                max="1.4"
                step="0.1"
                value={speechRate}
                onChange={(event) => setSpeechRate(Number(event.target.value))}
              />
              <div>{speechRate.toFixed(1)}x</div>
              <button type="button" className="refresh-button" onClick={handleSpeakResponse}>
                Read It Aloud
              </button>
              {isSpeaking ? (
                <button type="button" className="refresh-button" onClick={handleStopSpeaking}>
                  Stop Reading
                </button>
              ) : null}
            </div>
            {speechError ? <div className="hal-answer-card__section">{speechError}</div> : null}
            <div className="hal-answer-card__section">
              <strong>Answer lane:</strong> {humanizeLaneLabel(response.voice_profile.lane)}
            </div>
            {(response.voice_profile.style_notes ?? []).length ? (
              <div className="hal-answer-card__section">
                <strong>Style notes:</strong> {response.voice_profile.style_notes.join(" ")}
              </div>
            ) : null}
            <div className="hal-answer-card__section">
              <strong>Saved question:</strong> {response.sanitized_question}
            </div>
            <div className="hal-answer-card__section">
              <strong>Reference ID:</strong> {response.audit_id}
            </div>
            <div className="hal-answer-card__section">
              <strong>Built-in safeguards:</strong> {response.guardrails.map(humanizeGuardrail).join(", ")}
            </div>
            {(response.governance_notes ?? []).length ? (
              <div className="hal-answer-card__section">
                <strong>Governance:</strong> {response.governance_notes.map((item) => `${item.label}: ${item.detail}`).join(" | ")}
              </div>
            ) : null}
            {reviewAction ? (
              <section className="hal-review-actions">
                <h3>Before Anything Changes</h3>
                <div className="hal-review-actions__card">
                  <div className="hal-answer-card__section hal-answer-card__section--lead">{reviewAction.title}</div>
                  <div className="hal-answer-card__section">{reviewAction.confirmation_message}</div>
                  <div className="hal-answer-card__section">
                    <strong>Approval status:</strong> {humanizeLabel(reviewAction.status)}
                  </div>
                  <button
                    type="button"
                    className="refresh-button"
                    onClick={handleApproveDisplayAdjustment}
                    disabled={actionMutation.isPending}
                  >
                    {actionMutation.isPending ? "Approving..." : `Approve brightness change to ${reviewAction.target_value}%`}
                  </button>
                  {actionMutation.data ? (
                    <div className="hal-review-actions__result">
                      <strong>Action result:</strong> {humanizeLabel(actionMutation.data.status)}
                      {actionMutation.data.applied_value !== null ? ` (${actionMutation.data.applied_value}%)` : ""}
                      {actionMutation.data.error ? ` - ${actionMutation.data.error}` : ""}
                    </div>
                  ) : null}
                  {actionMutation.isError ? (
                    <div className="hal-review-actions__result hal-review-actions__result--error">
                      {actionMutation.error instanceof Error ? actionMutation.error.message : "Unable to execute the reviewed action."}
                    </div>
                  ) : null}
                </div>
              </section>
            ) : null}
            <h3>What HAL Looked At</h3>
            {response.retrieved_context.length === 0 ? <div>No supporting details were needed for this answer.</div> : null}
            {response.retrieved_context.map((item) => (
              <div key={item.source_id} className="hal-supporting-context-item">
                <strong>{item.title}</strong>
                <div>{item.excerpt}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

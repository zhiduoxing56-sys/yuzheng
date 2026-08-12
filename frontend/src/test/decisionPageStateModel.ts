import type { AdaptedCommandResponse } from "../adapters/commandResponseAdapter";
import type { PipelineEvent, TurnPresentationResponse } from "../types/contract";

export interface DecisionPageStateModel {
  sessionEpoch: number;
  submissionGeneration: number;
  activeTurnId: string | null;
  expectedTurnId: string | null;
  immediateResult: AdaptedCommandResponse | null;
  finalResult: TurnPresentationResponse | null;
  previousFinalResult: TurnPresentationResponse | null;
  eventSequenceBaseline: number;
  eventsByTurn: Record<string, PipelineEvent[]>;
}

export function createDecisionPageStateModel(): DecisionPageStateModel {
  return {
    sessionEpoch: 0,
    submissionGeneration: 0,
    activeTurnId: null,
    expectedTurnId: null,
    immediateResult: null,
    finalResult: null,
    previousFinalResult: null,
    eventSequenceBaseline: 0,
    eventsByTurn: {},
  };
}

export function beginModelSession(state: DecisionPageStateModel): DecisionPageStateModel {
  return {
    ...createDecisionPageStateModel(),
    sessionEpoch: state.sessionEpoch + 1,
    submissionGeneration: state.submissionGeneration + 1,
  };
}

export function beginModelSubmission(state: DecisionPageStateModel): DecisionPageStateModel {
  const highestSequence = Object.values(state.eventsByTurn).flat().reduce((max, event) => Math.max(max, event.sequence), 0);
  return {
    ...state,
    submissionGeneration: state.submissionGeneration + 1,
    expectedTurnId: null,
    immediateResult: null,
    previousFinalResult: state.finalResult ?? state.previousFinalResult,
    finalResult: null,
    eventSequenceBaseline: highestSequence,
  };
}

export function acceptModelSubmission(state: DecisionPageStateModel, result: AdaptedCommandResponse): DecisionPageStateModel {
  return { ...state, activeTurnId: result.turnId, expectedTurnId: result.turnId, immediateResult: result };
}

export function acceptModelFinalResult(state: DecisionPageStateModel, result: TurnPresentationResponse): DecisionPageStateModel {
  if (!state.expectedTurnId || result.turn_id !== state.expectedTurnId) return state;
  return { ...state, finalResult: result };
}

export function addModelEvent(state: DecisionPageStateModel, event: PipelineEvent): DecisionPageStateModel {
  if (event.sequence <= state.eventSequenceBaseline) return state;
  const current = state.eventsByTurn[event.turn_id] ?? [];
  if (current.some((item) => item.event_id === event.event_id)) return state;
  return {
    ...state,
    eventsByTurn: {
      ...state.eventsByTurn,
      [event.turn_id]: [...current, event].sort((left, right) => left.sequence - right.sequence),
    },
  };
}

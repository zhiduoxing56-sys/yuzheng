import type { TimelineResponse, TurnWorkflowStatus } from "../types/contract";
import { array, boolean, nonEmptyString, number, record, string } from "./runtime";

export function adaptWorkflowStatus(raw: unknown): TurnWorkflowStatus {
  const root = record(raw, "workflowStatus");
  nonEmptyString(root.root_turn_id, "workflowStatus.root_turn_id");
  nonEmptyString(root.current_turn_id, "workflowStatus.current_turn_id");
  string(root.status, "workflowStatus.status");
  number(root.review_attempts, "workflowStatus.review_attempts");
  number(root.max_review_attempts, "workflowStatus.max_review_attempts");
  string(root.latest_decision, "workflowStatus.latest_decision");
  number(root.event_count, "workflowStatus.event_count");
  boolean(root.terminal, "workflowStatus.terminal");
  return raw as TurnWorkflowStatus;
}

export function adaptTimeline(raw: unknown): TimelineResponse {
  const root = record(raw, "timeline");
  nonEmptyString(root.root_turn_id, "timeline.root_turn_id");
  if (!("audits" in root)) {
    const items = array(root.items, "timeline.items").map((value, index) => {
      const item = record(value, `timeline.items[${index}]`);
      for (const key of ["turn_id", "stage", "status", "timestamp", "summary"])
        string(item[key], `timeline.items[${index}].${key}`);
      return {
        sequence: index + 1,
        stage: string(item.stage, `timeline.items[${index}].stage`),
        timestamp: string(item.timestamp, `timeline.items[${index}].timestamp`),
        status: string(item.status, `timeline.items[${index}].status`),
        summary: string(item.summary, `timeline.items[${index}].summary`),
        turn_id: string(item.turn_id, `timeline.items[${index}].turn_id`),
        event_id: typeof item.event_id === "string" ? item.event_id : null,
      };
    });
    return { root_turn_id: string(root.root_turn_id, "timeline.root_turn_id"), items };
  }
  for (const key of ["audits", "ordered_items", "items", "workflow_events", "historical_execution_state"])
    array(root[key], `timeline.${key}`);
  record(root.current_simulator_state, "timeline.current_simulator_state");
  return raw as TimelineResponse;
}

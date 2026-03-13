/**
 * leadsStore.ts — Global singleton for prompt-matched ICP leads
 *
 * Data comes ONLY from /leads, which is populated by /run-strategy.
 * Before any run: has_runs = false, leads = []
 * After run(s):   has_runs = true,  leads = agent-matched results
 */

import { getLeads, type IcpLead, type LeadsResponse } from "@/lib/api";

// ─── Types ────────────────────────────────────────────────────────────────────

export type LeadsStoreState = {
    leads: IcpLead[];
    totalQualified: number;
    /** false = no strategy run yet; true = at least one run completed */
    hasRuns: boolean;
    lastFetchedAt: number | null;
    status: "idle" | "loading" | "ready" | "error";
    error: string | null;
};

// ─── Priority ordering (matches backend) ─────────────────────────────────────

const PRIORITY_ORDER: Record<string, number> = { High: 3, Medium: 2, Low: 1 };

function sortLeads(leads: IcpLead[]): IcpLead[] {
    return [...leads].sort((a, b) => {
        const pA = PRIORITY_ORDER[a.priority] ?? 0;
        const pB = PRIORITY_ORDER[b.priority] ?? 0;
        if (pB !== pA) return pB - pA;
        if (b.match_score !== a.match_score) return b.match_score - a.match_score;
        return b.engagement_score - a.engagement_score;
    });
}

// ─── Singleton store ──────────────────────────────────────────────────────────

let _state: LeadsStoreState = {
    leads: [],
    totalQualified: 0,
    hasRuns: false,
    lastFetchedAt: null,
    status: "idle",
    error: null,
};

const _listeners = new Set<() => void>();

function notify() {
    _listeners.forEach((fn) => fn());
}

export function subscribeLeadsStore(fn: () => void): () => void {
    _listeners.add(fn);
    return () => _listeners.delete(fn);
}

export function getLeadsStoreSnapshot(): LeadsStoreState {
    return _state;
}

/** Force-invalidate so next loadLeads() will re-fetch from server */
export function invalidateLeadsStore() {
    _state = { ..._state, lastFetchedAt: null, status: "idle" };
    notify();
}

/**
 * Load ICP leads from the backend.
 * - If cache is fresh and `force` is false, returns immediately.
 * - The backend returns only leads matched against the user's actual prompt(s).
 * - If no strategy has been run yet, has_runs = false and leads = [].
 */
export async function loadLeads(force = false): Promise<void> {
    if (!force && _state.status === "ready" && _state.lastFetchedAt !== null) {
        console.log(`[LeadsStore] Cache hit — ${_state.leads.length} leads`);
        return;
    }

    _state = { ..._state, status: "loading", error: null };
    notify();

    try {
        const data: LeadsResponse = await getLeads();

        const sorted = sortLeads(data.leads);

        console.group("[LeadsStore] Prompt-matched ICP leads");
        console.log("  has_runs            :", data.has_runs);
        console.log("  total_qualified     :", data.total_qualified);
        console.log("  displayed (sorted)  :", sorted.length);
        if (sorted.length > 0) {
            console.log(
                "  Top lead            :",
                `${sorted[0].name} | match=${sorted[0].match_score} | priority=${sorted[0].priority}`
            );
        }
        console.groupEnd();

        _state = {
            leads: sorted,
            totalQualified: sorted.length,
            hasRuns: data.has_runs,
            lastFetchedAt: Date.now(),
            status: "ready",
            error: null,
        };
    } catch (err) {
        const msg = err instanceof Error ? err.message : "Failed to load leads";
        console.error("[LeadsStore] Error:", msg);
        _state = { ..._state, status: "error", error: msg };
    }

    notify();
}

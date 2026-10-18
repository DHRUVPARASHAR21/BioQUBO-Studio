"""Local session result-history and re-export view."""

from __future__ import annotations

import streamlit as st

from bioqubo.models import ResultEnvelope
from bioqubo.result_history import HistoryEntry, create_history_entry, serialize_history

HISTORY_KEY = "bioqubo_result_history"


def record_result(
    result: ResultEnvelope, rows: list[dict[str, object]], file_stem: str
) -> HistoryEntry:
    """Keep a completed local result available through Streamlit session reruns."""

    entry = create_history_entry(result, rows, file_stem)
    history = st.session_state.setdefault(HISTORY_KEY, [])
    history.append(entry)
    return entry


def render_result_history_page() -> None:
    """Render local-only results created during the current browser session."""

    st.header("Result history and exports")
    st.info(
        "This history is stored only in the current local browser session. "
        "Download results to preserve them after the session ends."
    )
    history: list[HistoryEntry] = st.session_state.get(HISTORY_KEY, [])
    if not history:
        st.caption("Run HP folding, inverse design, residue selection, or molecule prioritization.")
        return
    st.dataframe(
        [
            {"workflow": entry.workflow, "created_at": entry.created_at}
            for entry in reversed(history)
        ],
        hide_index=True,
        width="stretch",
    )
    st.download_button(
        "Download all recorded results (JSON)",
        data=serialize_history(history),
        file_name="bioqubo_result_history.json",
        mime="application/json",
    )
    for index, entry in enumerate(reversed(history), start=1):
        with st.expander(f"{entry.workflow} — {entry.created_at}"):
            columns = st.columns(2)
            columns[0].download_button(
                "Download JSON",
                data=entry.exports.json_text,
                file_name=entry.json_file_name,
                mime="application/json",
                key=f"history-json-{index}",
            )
            columns[1].download_button(
                "Download CSV",
                data=entry.exports.csv_text,
                file_name=entry.csv_file_name,
                mime="text/csv",
                key=f"history-csv-{index}",
            )
    if st.button("Clear local result history"):
        st.session_state[HISTORY_KEY] = []
        st.rerun()

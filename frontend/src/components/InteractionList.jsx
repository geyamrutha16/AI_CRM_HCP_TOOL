import React, { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  setInteractions,
  deleteInteraction,
  setCurrentInteraction,
  setLoading,
} from "../store/interactionsSlice";
import { interactionsAPI } from "../services/api";
import { toast } from "react-toastify";
import "./InteractionList.css";

/**
 * InteractionList Component
 * Displays interactions in a table format with filtering and actions.
 */
export function InteractionList() {
  const dispatch = useDispatch();
  const { interactions, loading, filter } = useSelector(
    (state) => state.interactions,
  );
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    loadInteractions();
  }, []);

  const loadInteractions = async () => {
    dispatch(setLoading(true));
    try {
      const data = await interactionsAPI.getAll(
        0,
        50,
        filter.doctorName || undefined,
      );
      dispatch(setInteractions(data));
    } catch (error) {
      toast.error("Failed to load interactions", { autoClose: 3000 });
    } finally {
      dispatch(setLoading(false));
    }
  };

  const handleEdit = (interaction) => {
    dispatch(setCurrentInteraction(interaction));
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this interaction?"))
      return;

    try {
      await interactionsAPI.delete(id);
      dispatch(deleteInteraction(id));
      toast.success("Interaction deleted", { autoClose: 3000 });
    } catch (error) {
      toast.error("Failed to delete interaction", { autoClose: 3000 });
    }
  };

  const getSentimentEmoji = (sentiment) => {
    const map = {
      positive: "😊",
      neutral: "😐",
      negative: "😞",
    };
    return map[sentiment] || "😐";
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const filteredInteractions = interactions.filter(
    (interaction) =>
      interaction.doctor_name
        .toLowerCase()
        .includes(searchQuery.toLowerCase()) ||
      interaction.summary.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  return (
    <div className="interaction-list">
      <div className="list-header">
        <h2>📊 Interactions Log</h2>
        <input
          type="text"
          placeholder="🔍 Search by doctor or summary..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
      </div>

      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading interactions...</p>
        </div>
      )}

      {!loading && filteredInteractions.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <p>No interactions found</p>
          <small>Start by creating a new interaction using the form</small>
        </div>
      )}

      {!loading && filteredInteractions.length > 0 && (
        <div className="table-responsive">
          <table className="interactions-table">
            <thead>
              <tr>
                <th>Doctor Name</th>
                <th>Summary</th>
                <th>Sentiment</th>
                <th>Follow-up</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredInteractions.map((interaction) => (
                <tr key={interaction.id} className="interaction-row">
                  <td className="doctor-name">👨‍⚕️ {interaction.doctor_name}</td>
                  <td className="summary">
                    <span title={interaction.summary}>
                      {interaction.summary?.substring(0, 50)}...
                    </span>
                  </td>
                  <td className="sentiment">
                    <span
                      className={`sentiment-badge sentiment-${interaction.sentiment}`}
                    >
                      {getSentimentEmoji(interaction.sentiment)}{" "}
                      {interaction.sentiment}
                    </span>
                  </td>
                  <td className="follow-up">
                    {interaction.follow_up ? (
                      <span>{interaction.follow_up}</span>
                    ) : (
                      <span className="no-followup">No follow-up</span>
                    )}
                  </td>
                  <td className="date">{formatDate(interaction.created_at)}</td>
                  <td className="actions">
                    <button
                      onClick={() => handleEdit(interaction)}
                      className="btn-icon edit-btn"
                      title="Edit"
                    >
                      ✏️
                    </button>
                    <button
                      onClick={() => handleDelete(interaction.id)}
                      className="btn-icon delete-btn"
                      title="Delete"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="list-footer">
        <button onClick={loadInteractions} className="btn-refresh">
          🔄 Refresh
        </button>
        <small>
          {filteredInteractions.length} of {interactions.length} interactions
        </small>
      </div>
    </div>
  );
}

export default InteractionList;

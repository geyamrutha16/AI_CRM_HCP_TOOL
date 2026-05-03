import React, { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  addInteraction,
  updateInteraction,
  setCurrentInteraction,
} from "../store/interactionsSlice";
import { interactionsAPI } from "../services/api";
import { toast } from "react-toastify";
import "./InteractionForm.css";

/**
 * InteractionForm Component
 * Allows structured form-based entry of HCP interactions.
 * Can create new or edit existing interactions.
 */
export function InteractionForm() {
  const dispatch = useDispatch();
  const { currentInteraction } = useSelector((state) => state.interactions);

  const [formData, setFormData] = useState({
    doctor_name: "",
    summary: "",
    sentiment: "neutral",
    follow_up: "",
    interaction_text: "",
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  // Populate form when editing
  useEffect(() => {
    if (currentInteraction) {
      setFormData(currentInteraction);
    }
  }, [currentInteraction]);

  const validateForm = () => {
    const newErrors = {};

    if (!formData.doctor_name.trim()) {
      newErrors.doctor_name = "Doctor name is required";
    }
    if (!formData.interaction_text.trim()) {
      newErrors.interaction_text = "Interaction details are required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear error for this field
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: "",
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    setLoading(true);
    try {
      if (currentInteraction?.id) {
        // Update existing
        const response = await interactionsAPI.update(
          currentInteraction.id,
          formData,
        );
        dispatch(updateInteraction(response));
        toast.success("Interaction updated!", { autoClose: 3000 });
        dispatch(setCurrentInteraction(null));
      } else {
        // Create new
        const response = await interactionsAPI.create(formData);
        dispatch(addInteraction(response));
        toast.success("Interaction created!", { autoClose: 3000 });
      }

      // Reset form
      setFormData({
        doctor_name: "",
        summary: "",
        sentiment: "neutral",
        follow_up: "",
        interaction_text: "",
      });
    } catch (error) {
      const errorMessage =
        error.response?.data?.detail || "Failed to save interaction";
      toast.error(errorMessage, { autoClose: 3000 });
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFormData({
      doctor_name: "",
      summary: "",
      sentiment: "neutral",
      follow_up: "",
      interaction_text: "",
    });
    setErrors({});
    dispatch(setCurrentInteraction(null));
  };

  return (
    <div className="interaction-form">
      <div className="form-header">
        <h2>📋 {currentInteraction?.id ? "Edit" : "New"} Interaction</h2>
        <p>Fill in the details of the HCP interaction</p>
      </div>

      <form onSubmit={handleSubmit} className="form">
        <div className="form-group">
          <label htmlFor="doctor_name">Healthcare Professional Name *</label>
          <input
            id="doctor_name"
            name="doctor_name"
            type="text"
            value={formData.doctor_name}
            onChange={handleInputChange}
            placeholder="Dr. John Smith"
            disabled={loading}
            className={errors.doctor_name ? "input-error" : ""}
          />
          {errors.doctor_name && (
            <span className="error-text">{errors.doctor_name}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="interaction_text">Interaction Details *</label>
          <textarea
            id="interaction_text"
            name="interaction_text"
            value={formData.interaction_text}
            onChange={handleInputChange}
            placeholder="Describe the interaction, topics discussed, outcomes..."
            disabled={loading}
            rows="4"
            className={errors.interaction_text ? "input-error" : ""}
          />
          {errors.interaction_text && (
            <span className="error-text">{errors.interaction_text}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="summary">Summary (Auto-generated)</label>
          <textarea
            id="summary"
            name="summary"
            value={formData.summary}
            onChange={handleInputChange}
            placeholder="AI-generated summary will appear here..."
            disabled={loading}
            rows="3"
          />
          <small>Leave blank for AI to generate automatically</small>
        </div>

        <div className="form-group-row">
          <div className="form-group">
            <label htmlFor="sentiment">Sentiment</label>
            <select
              id="sentiment"
              name="sentiment"
              value={formData.sentiment}
              onChange={handleInputChange}
              disabled={loading}
            >
              <option value="positive">Positive 😊</option>
              <option value="neutral">Neutral 😐</option>
              <option value="negative">Negative 😞</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="follow_up">Follow-up Action</label>
            <input
              id="follow_up"
              name="follow_up"
              type="text"
              value={formData.follow_up}
              onChange={handleInputChange}
              placeholder="e.g., Call in 2 weeks"
              disabled={loading}
            />
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? "⏳ Saving..." : "💾 Save Interaction"}
          </button>
          <button
            type="button"
            onClick={handleReset}
            disabled={loading}
            className="btn-secondary"
          >
            ↺ Clear
          </button>
        </div>
      </form>
    </div>
  );
}

export default InteractionForm;

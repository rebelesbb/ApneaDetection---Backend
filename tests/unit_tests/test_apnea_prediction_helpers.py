import numpy as np
import pytest

from app.service.apnea_prediction_service import ApneaPredictionService


def build_prediction_service_without_loading_model():
    prediction_service = object.__new__(ApneaPredictionService)

    prediction_service.spo2_min = 60.0
    prediction_service.spo2_max = 100.0
    prediction_service.max_interp_gap_sec = 2
    prediction_service.smoothing_window = 3

    return prediction_service


def test_clean_spo2_replaces_invalid_values_with_nan():
    prediction_service = build_prediction_service_without_loading_model()

    values = np.array([95.0, 50.0, 101.0, 90.0], dtype=np.float32)

    cleaned_values = prediction_service._clean_spo2(values)

    assert cleaned_values[0] == 95.0
    assert np.isnan(cleaned_values[1])
    assert np.isnan(cleaned_values[2])
    assert cleaned_values[3] == 90.0


def test_interpolate_short_nan_gaps():
    prediction_service = build_prediction_service_without_loading_model()

    values = np.array([90.0, np.nan, 96.0], dtype=np.float32)

    interpolated_values = prediction_service._interpolate_short_nan_gaps(values)

    assert interpolated_values.tolist() == [90.0, 93.0, 96.0]


def test_interpolation_keeps_long_nan_gaps_unchanged():
    prediction_service = build_prediction_service_without_loading_model()

    values = np.array(
        [90.0, np.nan, np.nan, np.nan, 96.0],
        dtype=np.float32,
    )

    interpolated_values = prediction_service._interpolate_short_nan_gaps(values)

    assert np.isnan(interpolated_values[1])
    assert np.isnan(interpolated_values[2])
    assert np.isnan(interpolated_values[3])


def test_make_sleep_mask_marks_awake_periods_with_zero():
    prediction_service = build_prediction_service_without_loading_model()

    sleep_mask = prediction_service._make_sleep_mask(
        n=4,
        stages=[1, 0, 1, 0],
    )

    assert sleep_mask.tolist() == [1, 0, 1, 0]


def test_make_sleep_mask_rejects_invalid_stage_vector_length():
    prediction_service = build_prediction_service_without_loading_model()

    with pytest.raises(ValueError, match="Stages and SpO2 values must have the same length"):
        prediction_service._make_sleep_mask(
            n=4,
            stages=[1, 0],
        )


def test_smooth_probs_applies_moving_average():
    prediction_service = build_prediction_service_without_loading_model()

    probabilities = np.array([0.0, 0.0, 3.0, 0.0, 0.0], dtype=np.float32)

    smoothed_probabilities = prediction_service._smooth_probs(probabilities)

    assert np.allclose(
        smoothed_probabilities,
        [0.0, 1.0, 1.0, 1.0, 0.0],
    )
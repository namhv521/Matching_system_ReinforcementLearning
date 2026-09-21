from pathlib import Path
import pytest
from src.rl.train import SUPPORTED_ALGORITHMS, load_checkpoint


def test_supported_algorithms_cover_policy_and_value_rl_families():
    assert SUPPORTED_ALGORITHMS == ("ppo", "a2c", "dqn", "qrdqn")


def test_load_checkpoint_rejects_unsupported_algorithm():
    with pytest.raises(ValueError, match="Unsupported algorithm"):
        load_checkpoint("invalid_algo", Path("dummy.zip"))


def test_load_checkpoint_can_load_saved_ppo():
    checkpoint = Path("outputs/models/ppo_seed42_steps200000.zip")
    if checkpoint.exists():
        model = load_checkpoint("ppo", checkpoint)
        assert model is not None

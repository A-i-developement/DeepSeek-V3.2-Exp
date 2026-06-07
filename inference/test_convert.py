import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Mock torch module
mock_torch = MagicMock()
mock_torch.Tensor = MagicMock
sys.modules['torch'] = mock_torch

# Mock safetensors and safe_open
mock_safetensors = MagicMock()
mock_safe_open = MagicMock()
sys.modules['safetensors'] = mock_safetensors
sys.modules['safetensors.torch'] = MagicMock()
sys.modules['safetensors.torch'].safe_open = mock_safe_open
sys.modules['safetensors.torch'].save_file = MagicMock()

# Now it is safe to import from inference.convert
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from inference.convert import main

@patch('inference.convert.safe_open')
@patch('inference.convert.save_file')
@patch('inference.convert.os.makedirs')
@patch('inference.convert.shutil.copyfile')
@patch('inference.convert.glob')
def test_main_key_error(mock_glob, mock_copyfile, mock_makedirs, mock_save_file, mock_safe_open_fn):
    # Mock glob to return one dummy file
    mock_glob.side_effect = lambda path: ["dummy.safetensors"] if "safetensors" in path else []

    # Mock safe_open context manager
    mock_f = MagicMock()
    # Provide a key that will bypass the startswith('model.') and end up with an unknown key
    mock_f.keys.return_value = ["model.layers.0.unknown_key.weight"]
    mock_f.get_tensor.return_value = MagicMock()

    mock_safe_open_fn.return_value.__enter__.return_value = mock_f

    with pytest.raises(KeyError, match="Key unknown_key not found in mapping"):
        main("dummy_hf_path", "dummy_save_path", n_experts=8, mp=2)

@patch('inference.convert.safe_open')
@patch('inference.convert.save_file')
@patch('inference.convert.os.makedirs')
@patch('inference.convert.shutil.copyfile')
@patch('inference.convert.glob')
def test_main_value_error(mock_glob, mock_copyfile, mock_makedirs, mock_save_file, mock_safe_open_fn):
    mock_glob.side_effect = lambda path: ["dummy.safetensors"] if "safetensors" in path else []

    mock_f = MagicMock()
    # Provide a key that is in mapping and has dim is not None
    # "q_proj": ("wq", 0)
    mock_f.keys.return_value = ["model.layers.0.q_proj.weight"]

    mock_tensor = MagicMock()
    # Dim 0 is not divisible by mp=2
    mock_tensor.size.return_value = 3
    mock_f.get_tensor.return_value = mock_tensor

    mock_safe_open_fn.return_value.__enter__.return_value = mock_f

    with pytest.raises(ValueError, match="Dimension 0 must be divisible by 2"):
        main("dummy_hf_path", "dummy_save_path", n_experts=8, mp=2)

def test_cli_parser_error(monkeypatch):

    # Wait, inference/convert.py creates `parser` inside `if __name__ == "__main__":`
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--hf-ckpt-path", type=str, required=True)
    parser.add_argument("--save-path", type=str, required=True)
    parser.add_argument("--n-experts", type=int, required=True)
    parser.add_argument("--model-parallel", type=int, required=True)


    # Mock sys.argv
    monkeypatch.setattr(sys, 'argv', ['convert.py', '--hf-ckpt-path', 'a', '--save-path', 'b', '--n-experts', '3', '--model-parallel', '2'])

    with pytest.raises(SystemExit):
        args = parser.parse_args()
        if args.n_experts % args.model_parallel != 0:
            parser.error("Number of experts must be divisible by model parallelism")

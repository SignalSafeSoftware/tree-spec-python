"""Unknown-field behavior for TreeSpec wire JSON (see docs/compatibility.md)."""

from __future__ import annotations

from deliveryplus_tree_spec import END_NODE_ID
from deliveryplus_tree_spec.models import TreeSpec


def test_parse_ignores_unknown_root_key() -> None:
    raw = {
        "start_node": "s",
        "nodes": {"s": {"type": "prompt", "prompt": "Hi", "choices": []}},
        "transitions": [],
        "experimental_flag": True,
    }
    spec = TreeSpec.model_validate(raw)
    dumped = spec.model_dump(by_alias=True)
    assert "experimental_flag" not in dumped


def test_meta_unknown_nested_keys_preserved() -> None:
    raw = {
        "start_node": "s",
        "nodes": {"s": {"type": "prompt", "prompt": "Hi", "choices": []}},
        "transitions": [],
        "_meta": {"custom_bucket": {"any": "json"}},
    }
    spec = TreeSpec.model_validate(raw)
    dumped = spec.model_dump(by_alias=True)
    assert dumped["_meta"] == {"custom_bucket": {"any": "json"}}


def test_node_render_hints_unknown_nested_keys_preserved() -> None:
    raw = {
        "start_node": "s",
        "nodes": {
            "s": {
                "type": "prompt",
                "prompt": "Hi",
                "choices": [],
                "render_hints": {"vendor_extension": {"x": 1}},
            }
        },
        "transitions": [],
    }
    spec = TreeSpec.model_validate(raw)
    assert spec.nodes["s"].render_hints == {"vendor_extension": {"x": 1}}


def test_parse_ignores_unknown_node_and_choice_keys() -> None:
    raw = {
        "start_node": "s",
        "nodes": {
            "s": {
                "type": "prompt",
                "prompt": "Hi",
                "legacy_flag": True,
                "choices": [{"id": "c1", "label": "Go", "tooltip": "drop me"}],
            }
        },
        "transitions": [{"from": ["s", "c1"], "to": END_NODE_ID, "outcome": "safe"}],
    }
    spec = TreeSpec.model_validate(raw)
    dumped = spec.model_dump(by_alias=True)
    node = dumped["nodes"]["s"]
    assert "legacy_flag" not in node
    choice = node["choices"][0]
    assert choice == {"id": "c1", "label": "Go", "feedback": None}


def test_choice_render_hints_not_modeled_accepted_difference() -> None:
    raw = {
        "start_node": "s",
        "nodes": {
            "s": {
                "type": "prompt",
                "prompt": "Hi",
                "choices": [
                    {
                        "id": "c1",
                        "label": "Go",
                        "render_hints": {"editor": {"strokeColor": "#000"}},
                    }
                ],
            }
        },
        "transitions": [{"from": ["s", "c1"], "to": END_NODE_ID, "outcome": "safe"}],
    }
    spec = TreeSpec.model_validate(raw)
    dumped = spec.model_dump(by_alias=True)
    choice = dumped["nodes"]["s"]["choices"][0]
    assert "render_hints" not in choice


def test_parse_ignores_unknown_transition_key() -> None:
    raw = {
        "start_node": "s",
        "nodes": {
            "s": {
                "type": "prompt",
                "prompt": "Hi",
                "choices": [{"id": "c1", "label": "Go"}],
            }
        },
        "transitions": [
            {
                "from": ["s", "c1"],
                "to": END_NODE_ID,
                "outcome": "safe",
                "internal_note": "drop me",
                "feedback": {"title": "Done", "vendor_tag": "strip-me"},
            }
        ],
    }
    spec = TreeSpec.model_validate(raw)
    dumped = spec.model_dump(by_alias=True)
    transition = dumped["transitions"][0]
    assert "internal_note" not in transition
    feedback = transition["feedback"]
    assert feedback is not None
    assert feedback["title"] == "Done"
    assert "vendor_tag" not in feedback

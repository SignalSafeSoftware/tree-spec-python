from __future__ import annotations
from dataclasses import dataclass
from typing import List
from typing import Optional
from deliveryplus_tree_spec.builder import TreeSpecBuilder
from deliveryplus_tree_spec.constants import END_NODE_ID


@dataclass(frozen=True)
class TreeSpecIssue:
    level: str  # "error" | "warning"
    code: str
    message: str
    node_id: Optional[str] = None
    choice_id: Optional[str] = None


def _find_duplicate_transition_keys(builder: TreeSpecBuilder) -> list[tuple[str, str]]:
    seen: set[tuple[str, str]] = set()
    dupes: set[tuple[str, str]] = set()
    for transition in builder.spec.transitions:
        key = (transition.from_[0], transition.from_[1])
        if key in seen:
            dupes.add(key)
        else:
            seen.add(key)
    return sorted(dupes)


def _build_duplicate_transition_issues(
    duplicate_keys: list[tuple[str, str]],
) -> list[TreeSpecIssue]:
    return [
        TreeSpecIssue(
            level="error",
            code="duplicate_transition",
            message=(
                f"Duplicate transition for ({from_node}, {choice_id}). Each choice must have exactly one transition."
            ),
            node_id=from_node,
            choice_id=choice_id,
        )
        for from_node, choice_id in duplicate_keys
    ]


def _build_transition_map(builder: TreeSpecBuilder) -> dict[tuple[str, str], str]:
    return {
        (transition.from_[0], transition.from_[1]): transition.to
        for transition in builder.spec.transitions
    }


def _find_missing_transition_issues(
    builder: TreeSpecBuilder,
    trans_map: dict[tuple[str, str], str],
) -> list[TreeSpecIssue]:
    issues: list[TreeSpecIssue] = []
    for node_id, node in builder.spec.nodes.items():
        for choice in node.choices:
            if (node_id, choice.id) in trans_map:
                continue
            issues.append(
                TreeSpecIssue(
                    level="error",
                    code="missing_transition",
                    message=f"Missing transition for choice '{choice.id}' on node '{node_id}'.",
                    node_id=node_id,
                    choice_id=choice.id,
                )
            )
    return issues


def _find_missing_target_node_issues(
    builder: TreeSpecBuilder,
    trans_map: dict[tuple[str, str], str],
) -> list[TreeSpecIssue]:
    issues: list[TreeSpecIssue] = []
    for (from_node, choice_id), to_node in trans_map.items():
        if to_node == END_NODE_ID or to_node in builder.spec.nodes:
            continue
        issues.append(
            TreeSpecIssue(
                level="error",
                code="missing_target_node",
                message=f"Transition ({from_node}, {choice_id}) points to missing node '{to_node}'.",
                node_id=from_node,
                choice_id=choice_id,
            )
        )
    return issues


def _collect_reachable_nodes(
    builder: TreeSpecBuilder,
    trans_map: dict[tuple[str, str], str],
) -> set[str]:
    reachable: set[str] = set()
    stack: list[str] = [builder.get_start_node_id()]
    while stack:
        node_id = stack.pop()
        if node_id in reachable:
            continue
        reachable.add(node_id)
        current = builder.spec.nodes.get(node_id)
        if current is None:
            continue
        for choice in current.choices:
            next_node = trans_map.get((node_id, choice.id))
            if not next_node or next_node == END_NODE_ID or next_node in reachable:
                continue
            stack.append(next_node)
    return reachable


def _find_unreachable_node_issues(
    builder: TreeSpecBuilder,
    reachable: set[str],
) -> list[TreeSpecIssue]:
    start_node_id = builder.get_start_node_id()
    return [
        TreeSpecIssue(
            level="warning",
            code="unreachable_node",
            message=f"Node '{node_id}' is unreachable from start node '{start_node_id}'.",
            node_id=node_id,
        )
        for node_id in builder.spec.nodes.keys()
        if node_id not in reachable
    ]


def lint_tree_spec(builder: TreeSpecBuilder) -> List[TreeSpecIssue]:
    """Domain linting beyond Pydantic shape validation.

    The TreeSpec models enforce structural invariants, but lints catch authoring mistakes:
    - missing transitions for choices
    - transitions that point to missing nodes
    - unreachable nodes

    Keep these rules stable and re-use them across:
    - seed_demo (--training-content-only)
    - admin validate endpoint
    - publish gating
    """

    duplicate_keys = _find_duplicate_transition_keys(builder)
    trans_map = _build_transition_map(builder)
    reachable = _collect_reachable_nodes(builder, trans_map)

    return [
        *_build_duplicate_transition_issues(duplicate_keys),
        *_find_missing_transition_issues(builder, trans_map),
        *_find_missing_target_node_issues(builder, trans_map),
        *_find_unreachable_node_issues(builder, reachable),
    ]

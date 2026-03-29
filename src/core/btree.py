from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class BTreeOpResult:
    found: bool
    touched_node_ids: list[int] = field(default_factory=list)


class BTreeNode:
    def __init__(self, node_id: int, leaf: bool = False) -> None:
        self.node_id = node_id
        self.leaf = leaf
        self.keys: list[int] = []
        self.children: list[BTreeNode] = []

class BTree:
    """B-tree following Knuth's order m (where max children = m, max keys = m - 1)."""

    def __init__(self, t: int = 3) -> None:
        if t < 3:
            raise ValueError("B-tree order must be >= 3")
        self.m = t
        self.max_keys = self.m - 1
        self.min_keys = (self.m + 1) // 2 - 1
        self._next_id = 1
        self.root = self._new_node(leaf=True)

    def _new_node(self, leaf: bool) -> BTreeNode:
        node = BTreeNode(self._next_id, leaf)
        self._next_id += 1
        return node

    def search(self, k: int, x: BTreeNode | None = None) -> bool:
        if x is None:
            x = self.root
            
        i = 0
        while i < len(x.keys) and k > x.keys[i]:
            i += 1
        if i < len(x.keys) and k == x.keys[i]:
            return True
        elif x.leaf:
            return False
        else:
            return self.search(k, x.children[i])

    def search_path(self, key: int) -> list[int]:
        path: list[int] = []
        node = self.root
        while True:
            path.append(node.node_id)
            i = 0
            while i < len(node.keys) and key > node.keys[i]:
                i += 1
            if i < len(node.keys) and node.keys[i] == key:
                return path
            if node.leaf:
                return path
            node = node.children[i]

    def insert(self, k: int) -> BTreeOpResult:
        if self.search(k):
            return BTreeOpResult(found=False, touched_node_ids=self.search_path(k))
            
        split_result = self._insert(self.root, k)
        if split_result:
            promoted_key, right_child = split_result
            new_root = self._new_node(leaf=False)
            new_root.keys = [promoted_key]
            new_root.children = [self.root, right_child]
            self.root = new_root
            
        return BTreeOpResult(found=True, touched_node_ids=self._collect_all_node_ids())

    def _insert(self, node: BTreeNode, k: int) -> tuple[int, BTreeNode] | None:
        if node.leaf:
            idx = 0
            while idx < len(node.keys) and k > node.keys[idx]:
                idx += 1
            node.keys.insert(idx, k)
        else:
            idx = 0
            while idx < len(node.keys) and k > node.keys[idx]:
                idx += 1
            
            split_result = self._insert(node.children[idx], k)
            if split_result:
                promoted_key, right_child = split_result
                node.keys.insert(idx, promoted_key)
                node.children.insert(idx + 1, right_child)
        
        if len(node.keys) > self.max_keys:
            return self._split(node)
        return None

    def _split(self, node: BTreeNode) -> tuple[int, BTreeNode]:
        mid = len(node.keys) // 2
        promoted_key = node.keys[mid]
        
        right_node = self._new_node(leaf=node.leaf)
        right_node.keys = node.keys[mid+1:]
        node.keys = node.keys[:mid]
        
        if not node.leaf:
            right_node.children = node.children[mid+1:]
            node.children = node.children[:mid+1]
            
        return promoted_key, right_node

    def delete(self, k: int) -> BTreeOpResult:
        if not self.search(k):
            return BTreeOpResult(found=False, touched_node_ids=self.search_path(k))
            
        self._delete(self.root, k)
        
        if len(self.root.keys) == 0 and not self.root.leaf:
            self.root = self.root.children[0]
            
        return BTreeOpResult(found=True, touched_node_ids=self._collect_all_node_ids())

    def _delete(self, node: BTreeNode, k: int) -> None:
        idx = 0
        while idx < len(node.keys) and k > node.keys[idx]:
            idx += 1
            
        if idx < len(node.keys) and node.keys[idx] == k:
            if node.leaf:
                node.keys.pop(idx)
            else:
                pred_node = node.children[idx]
                while not pred_node.leaf:
                    pred_node = pred_node.children[-1]
                pred_key = pred_node.keys[-1]
                node.keys[idx] = pred_key
                self._delete_in_subtree(node, idx, pred_key)
        else:
            if node.leaf:
                return
            self._delete_in_subtree(node, idx, k)
            
    def _delete_in_subtree(self, node: BTreeNode, child_idx: int, k: int) -> None:
        child = node.children[child_idx]
        self._delete(child, k)
        
        if len(child.keys) < self.min_keys:
            self._fix_underflow(node, child_idx)
            
    def _fix_underflow(self, parent: BTreeNode, i: int) -> None:
        child = parent.children[i]
        
        # Borrow from left sibling
        if i > 0 and len(parent.children[i-1].keys) > self.min_keys:
            left_sibling = parent.children[i-1]
            child.keys.insert(0, parent.keys[i-1])
            parent.keys[i-1] = left_sibling.keys.pop()
            if not child.leaf:
                child.children.insert(0, left_sibling.children.pop())
            return
            
        # Borrow from right sibling
        if i < len(parent.children) - 1 and len(parent.children[i+1].keys) > self.min_keys:
            right_sibling = parent.children[i+1]
            child.keys.append(parent.keys[i])
            parent.keys[i] = right_sibling.keys.pop(0)
            if not child.leaf:
                child.children.append(right_sibling.children.pop(0))
            return
            
        # Merge
        if i > 0:
            self._merge(parent, i-1)
        else:
            self._merge(parent, i)

    def _merge(self, parent: BTreeNode, i: int) -> None:
        left = parent.children[i]
        right = parent.children[i+1]
        
        left.keys.append(parent.keys.pop(i))
        left.keys.extend(right.keys)
        if not left.leaf:
            left.children.extend(right.children)
            
        parent.children.pop(i+1)

    def _collect_all_node_ids(self) -> list[int]:
        snapshot = self.export_snapshot()
        touched: list[int] = []
        for level in snapshot.get("levels", []):
            for node in level:
                node_id = node.get("id")
                if isinstance(node_id, int):
                    touched.append(node_id)
        return touched

    def export_snapshot(self) -> dict:
        if self.root is None:
            return {"root_id": None, "levels": []}

        levels: list[list[dict]] = []
        queue: deque[tuple[BTreeNode, int, int | None]] = deque([(self.root, 0, None)])

        while queue:
            node, depth, parent_id = queue.popleft()
            while len(levels) <= depth:
                levels.append([])

            levels[depth].append(
                {
                    "id": node.node_id,
                    "keys": list(node.keys),
                    "leaf": node.leaf,
                    "parent_id": parent_id,
                    "children_ids": [child.node_id for child in node.children],
                }
            )

            for child in node.children:
                queue.append((child, depth + 1, node.node_id))

        return {"root_id": self.root.node_id, "levels": levels}

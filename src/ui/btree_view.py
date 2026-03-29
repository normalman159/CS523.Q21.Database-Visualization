from __future__ import annotations

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QBrush, QColor, QFont, QFontMetricsF, QPainter, QPen
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsScene, QGraphicsSimpleTextItem, QGraphicsView


class BTreeView(QGraphicsView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.graphics_scene = QGraphicsScene(self)
        self.setScene(self.graphics_scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setMinimumHeight(320)

    def render_tree(self, snapshot: dict, highlighted_node_ids: list[int] | None = None) -> None:
        self.graphics_scene.clear()
        highlighted = set(highlighted_node_ids or [])

        levels = snapshot.get("levels", []) if snapshot else []
        if not levels:
            text = QGraphicsSimpleTextItem("B-tree rong")
            text.setPos(20, 20)
            self.graphics_scene.addItem(text)
            return

        node_positions: dict[int, QPointF] = {}
        level_height = 90
        base_y = 30

        for depth, nodes in enumerate(levels):
            y = base_y + (depth * level_height)
            spacing = 170
            start_x = 30 if len(nodes) == 1 else 60

            for idx, node in enumerate(nodes):
                x = start_x + idx * spacing
                keys = node.get("keys", [])
                label = " | ".join(str(key) for key in keys) if keys else "( )"
                font = QFont("Segoe UI", 9)
                metrics = QFontMetricsF(font)
                width = max(60, int(metrics.horizontalAdvance(label)) + 18)
                height = 40

                rect = QGraphicsRectItem(x, y, width, height)
                rect.setPen(QPen(QColor("#1f2937"), 1.5))
                if node["id"] in highlighted:
                    rect.setBrush(QBrush(QColor("#facc15")))
                else:
                    rect.setBrush(QBrush(QColor("#e5e7eb")))
                self.graphics_scene.addItem(rect)

                text_item = QGraphicsSimpleTextItem(label)
                text_item.setFont(font)
                text_item.setPos(x + 8, y + 10)
                self.graphics_scene.addItem(text_item)

                node_positions[node["id"]] = QPointF(x + width / 2.0, y + height / 2.0)

        for depth in range(1, len(levels)):
            for node in levels[depth]:
                parent_id = node.get("parent_id")
                if parent_id is None:
                    continue
                parent_pos = node_positions.get(parent_id)
                node_pos = node_positions.get(node["id"])
                if parent_pos is None or node_pos is None:
                    continue

                self.graphics_scene.addLine(
                    parent_pos.x(),
                    parent_pos.y() + 20,
                    node_pos.x(),
                    node_pos.y() - 20,
                    QPen(QColor("#6b7280"), 1.2),
                )

        self.setSceneRect(self.graphics_scene.itemsBoundingRect().adjusted(-20, -20, 20, 40))

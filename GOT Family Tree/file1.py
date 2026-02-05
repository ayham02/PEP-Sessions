# =========================
# Person Node
# =========================

class Person:
    def __init__(self, person_id, name, house=None, synthetic=False):
        self.person_id = person_id
        self.name = name
        self.house = house
        self.synthetic = synthetic
        # layout (computed)
        self.x = 0
        self.y = 0
        self._subtree_width = 0
        # spouse layout (visual only)
        self.spouse_positions = []  # list of (spouse, x, y)
        # visual connections (computed)
        self.marriage_lines = []   # list of ((x1, y1), (x2, y2))
        self.child_lines = []      # list of ((x1, y1), (x2, y2))

        # Navigation-only
        self.father = None
        self.mother = None

        # Structural
        self.children = []

        # Non-structural
        self.spouses = []

        # Visualization state
        self.expanded = True   # root & nodes expanded by default
        # bounding box (computed)
        self.width = 1.0   # visual node width
        self.height = 1.0


    def add_spouse(self, spouse):
        if spouse not in self.spouses:
            self.spouses.append(spouse)
            spouse.spouses.append(self)

    def add_child(self, child, father=None, mother=None):
        if child not in self.children:
            self.children.append(child)

        if father:
            child.father = father
        if mother:
            child.mother = mother

    def __repr__(self):
        return f"{self.name} ({self.house})"


# =========================
# Family Tree
# =========================

class FamilyTree:
    def __init__(self, root):
        self.root = root
        self.index = {root.person_id: root}

    def add_person(self, person):
        if person.person_id in self.index:
            raise ValueError("Duplicate person_id")
        self.index[person.person_id] = person

    def get(self, person_id):
        return self.index.get(person_id)
    def collapse_subtree(person):
        person.expanded = False

    def expand_subtree(person):
        person.expanded = True
    
    def search_by_name(self, query):
        q = query.lower()
        return [
            p for p in self.index.values()
            if q in p.name.lower()
        ]

    def get_path_to_root(self, person):
        path = []
        current = person
        visited = set()

        while current and current.person_id not in visited:
            visited.add(current.person_id)
            path.append(current)
            current = current.father or current.mother

        return list(reversed(path))


def collapse_all(tree):
    for p in tree.index.values():
        p.expanded = False


def expand_path(path):
    for p in path:
        p.expanded = True

def compute_view_offset(person, view_width=20, view_height=15):
        """
        Returns dx, dy needed to center person in view
        """
        dx = (view_width / 2) - person.x
        dy = (view_height / 2) - person.y
        return dx, dy

# =========================
# Registry Helper
# =========================

class PersonRegistry:
    def __init__(self, tree):
        self.tree = tree

    def person(self, pid, name, house=None):
        if pid in self.tree.index:
            return self.tree.get(pid)

        p = Person(pid, name, house)
        self.tree.add_person(p)
        return p

    def marry(self, p1, p2):
        p1.add_spouse(p2)


# =========================
# Validator (aligned to YOUR design)
# =========================

class FamilyTreeValidator:
    def __init__(self, tree):
        self.tree = tree
        self.errors = []
        self.warnings = []

    def validate(self):
        self.errors.clear()
        self.warnings.clear()

        self._check_cycles()
        self._check_parent_child_consistency()
        self._check_spouse_consistency()
        self._check_orphans()

        return self.errors, self.warnings

    def _check_cycles(self):
        visited = set()
        stack = set()

        def dfs(node):
            if node.person_id in stack:
                self.errors.append(f"Cycle detected at {node.name}")
                return

            if node.person_id in visited:
                return

            visited.add(node.person_id)
            stack.add(node.person_id)

            for child in node.children:
                dfs(child)

            stack.remove(node.person_id)

        dfs(self.tree.root)

    def _check_parent_child_consistency(self):
        for person in self.tree.index.values():
            for child in person.children:
                if person.synthetic:
                    continue
                if child.father != person and child.mother != person:
                    self.warnings.append(
                        f"{child.name} listed under {person.name} "
                        f"but parent link not set"
                    )

    def _check_spouse_consistency(self):
        for person in self.tree.index.values():
            for spouse in person.spouses:
                if person not in spouse.spouses:
                    self.warnings.append(
                        f"One-way spouse link: {person.name} → {spouse.name}"
                    )

    def _check_orphans(self):
        reachable = set()

        def dfs(node):
            if node.person_id in reachable:
                return
            reachable.add(node.person_id)
            for child in node.children:
                dfs(child)

        dfs(self.tree.root)

        for person in self.tree.index.values():
            if person.synthetic:
                continue
            if person.person_id not in reachable:
                # Allow spouse-only nodes
                if person.spouses:
                    continue
                self.warnings.append(
                    f"Orphan node: {person.name} (not reachable from root)"
                )

class TreeLayoutEngine:
    def __init__(self, horizontal_spacing=2.0, vertical_spacing=2.5):
        self.h_spacing = horizontal_spacing
        self.v_spacing = vertical_spacing

    def layout(self, tree):
        # Step 1: compute subtree widths
        self._compute_width(tree.root)

        # Step 2: assign coordinates
        self._assign_positions(tree.root, x_offset=0, depth=0)

    # ----------------------------
    # Width calculation
    # ----------------------------
    def _compute_width(self, node):
        # Collapsed or leaf → fixed width
        if not node.children or not node.expanded:
            node._subtree_width = 1
            return 1

        width = 0
        for child in node.children:
            width += self._compute_width(child)

        node._subtree_width = max(width, 1)
        return node._subtree_width


    # ----------------------------
    # Position assignment
    # ----------------------------
    def _assign_positions(self, node, x_offset, depth):
        node.y = depth * self.v_spacing

        # Collapsed or leaf
        if not node.children or not node.expanded:
            node.x = x_offset + self.h_spacing / 2
            return

        current_x = x_offset
        child_centers = []

        for child in node.children:
            child_width = child._subtree_width * self.h_spacing
            self._assign_positions(child, current_x, depth + 1)
            child_centers.append(child.x)
            current_x += child_width

        node.x = sum(child_centers) / len(child_centers)


class SpouseLayoutEngine:
    def __init__(self, spouse_spacing=1.2):
        self.spouse_spacing = spouse_spacing

    def layout(self, tree):
        visited = set()

        for person in tree.index.values():
            if person.person_id in visited:
                continue

            if not person.spouses:
                continue

            # Anchor is the person already placed by tree layout
            base_x = person.x
            base_y = person.y

            # Lay spouses alternately left / right
            offset_index = 1
            direction = 1  # right first

            for spouse in person.spouses:
                if spouse.person_id in visited:
                    continue

                spouse.x = base_x + direction * offset_index * self.spouse_spacing
                spouse.y = base_y

                person.spouse_positions.append((spouse, spouse.x, spouse.y))
                spouse.spouse_positions.append((person, base_x, base_y))

                visited.add(spouse.person_id)

                direction *= -1
                if direction > 0:
                    offset_index += 1

            visited.add(person.person_id)

class ConnectionEngine:
    def __init__(self):
        pass

    def build(self, tree):
        # Clear previous connections
        for p in tree.index.values():
            p.marriage_lines.clear()
            p.child_lines.clear()

        self._build_marriages(tree)
        self._build_children(tree)

    # ----------------------------
    # Marriage lines
    # ----------------------------
    def _build_marriages(self, tree):
        seen = set()

        for person in tree.index.values():
            for spouse in person.spouses:
                key = tuple(sorted([person.person_id, spouse.person_id]))
                if key in seen:
                    continue

                seen.add(key)

                line = ((person.x, person.y), (spouse.x, spouse.y))
                person.marriage_lines.append(line)
                spouse.marriage_lines.append(line)

    # ----------------------------
    # Child connections
    # ----------------------------
    def _build_children(self, tree):
        for parent in tree.index.values():

            # Do not draw children if collapsed
            if not parent.expanded:
                continue

            for child in parent.children:
                father = child.father
                mother = child.mother

                # Case 1: married parents
                if father and mother and mother in father.spouses:
                    mx = (father.x + mother.x) / 2
                    my = father.y

                    parent_point = (mx, my)
                    child_point = (child.x, child.y)

                    father.child_lines.append((parent_point, child_point))
                    mother.child_lines.append((parent_point, child_point))

                # Case 2: single parent
                else:
                    parent_point = (parent.x, parent.y)
                    child_point = (child.x, child.y)

                    parent.child_lines.append((parent_point, child_point))


class CollisionEngine:
    def __init__(self, min_gap=0.5):
        self.min_gap = min_gap

    def resolve(self, tree):
        """
        Resolve collisions level-by-level (same y)
        """
        levels = self._group_by_level(tree)

        for y, nodes in levels.items():
            self._resolve_level(nodes)

    # ----------------------------
    # Group nodes by Y (generation)
    # ----------------------------
    def _group_by_level(self, tree):
        levels = {}
        for p in tree.index.values():
            levels.setdefault(p.y, []).append(p)
        return levels

    # ----------------------------
    # Resolve collisions on one row
    # ----------------------------
    def _resolve_level(self, nodes):
        # Sort left → right
        nodes.sort(key=lambda n: n.x)

        for i in range(1, len(nodes)):
            left = nodes[i - 1]
            right = nodes[i]

            overlap = (
                (left.x + left.width / 2 + self.min_gap)
                - (right.x - right.width / 2)
            )

            if overlap > 0:
                self._shift_subtree(right, overlap)

    # ----------------------------
    # Shift node + descendants
    # ----------------------------
    def _shift_subtree(self, node, dx):
        node.x += dx

        for child in node.children:
            self._shift_subtree(child, dx)

        # Shift spouses with anchor
        for spouse, _, _ in node.spouse_positions:
            spouse.x += dx

class SearchController:
    def __init__(self, tree):
        self.tree = tree

    def focus_on(self, person):
        # 1️⃣ Collapse everything
        collapse_all(self.tree)

        # 2️⃣ Expand ancestors
        path = self.tree.get_path_to_root(person)
        expand_path(path)

        # 3️⃣ Expand the person itself
        person.expanded = True

        # 4️⃣ (Optional) expand immediate children
        for child in person.children:
            child.expanded = True

    def search_and_focus(self, query):
        matches = self.tree.search_by_name(query)
        if not matches:
            return None

        # For now: take the first match
        target = matches[0]
        self.focus_on(target)
        return target
    
    
    





# =========================
# Build Game of Thrones Tree
# =========================

def build_got_tree():
    # 🌍 World root
    root = Person("world", "Westeros", synthetic=True)
    tree = FamilyTree(root)
    R = PersonRegistry(tree)

    # ── CREATE HOUSE ANCESTORS ──
    aegon_i = R.person("t1", "Aegon I", "Targaryen")
    rickard = R.person("s3", "Rickard Stark", "Stark")
    steffon = R.person("b1", "Steffon Baratheon", "Baratheon")
    tywin = R.person("l1", "Tywin Lannister", "Lannister")

    # ── ATTACH TO WORLD ROOT ──
    root.add_child(aegon_i)
    root.add_child(rickard)
    root.add_child(steffon)
    root.add_child(tywin)

    # ── TARGARYENS ──
    maekar = R.person("t2", "Maekar I", "Targaryen")
    aegon_i.add_child(maekar, father=aegon_i)

    aerys = R.person("t5", "Aerys II", "Targaryen")
    maekar.add_child(aerys, father=maekar)

    rhaegar = R.person("t6", "Rhaegar Targaryen", "Targaryen")
    viserys = R.person("t7", "Viserys Targaryen", "Targaryen")
    daenerys = R.person("t8", "Daenerys Targaryen", "Targaryen")

    aerys.add_child(rhaegar, father=aerys)
    aerys.add_child(viserys, father=aerys)
    aerys.add_child(daenerys, father=aerys)

    # ── STARKS ──
    eddard = R.person("s4", "Eddard Stark", "Stark")
    benjen = R.person("s5", "Benjen Stark", "Stark")
    lyanna = R.person("s1", "Lyanna Stark", "Stark")

    rickard.add_child(eddard, father=rickard)
    rickard.add_child(benjen, father=rickard)
    rickard.add_child(lyanna, father=rickard)

    catelyn = R.person("tully1", "Catelyn Tully", "Tully")
    eddard.add_spouse(catelyn)

    robb = R.person("s6", "Robb Stark", "Stark")
    sansa = R.person("s7", "Sansa Stark", "Stark")
    arya = R.person("s8", "Arya Stark", "Stark")
    bran = R.person("s9", "Bran Stark", "Stark")
    rickon = R.person("s10", "Rickon Stark", "Stark")

    for child in [robb, sansa, arya, bran, rickon]:
        eddard.add_child(child, father=eddard, mother=catelyn)

    jon = R.person("s2", "Jon Snow", "Stark")
    rhaegar.add_child(jon, father=rhaegar, mother=lyanna)

    # ── BARATHEONS ──
    robert = R.person("b2", "Robert Baratheon", "Baratheon")
    stannis = R.person("b3", "Stannis Baratheon", "Baratheon")
    renly = R.person("b4", "Renly Baratheon", "Baratheon")

    steffon.add_child(robert, father=steffon)
    steffon.add_child(stannis, father=steffon)
    steffon.add_child(renly, father=steffon)

    # ── LANNISTERS ──
    joanna = R.person("l2", "Joanna Lannister", "Lannister")
    tywin.add_spouse(joanna)

    jaime = R.person("l3", "Jaime Lannister", "Lannister")
    cersei = R.person("l4", "Cersei Lannister", "Lannister")
    tyrion = R.person("l5", "Tyrion Lannister", "Lannister")

    tywin.add_child(jaime, father=tywin, mother=joanna)
    tywin.add_child(cersei, father=tywin, mother=joanna)
    tywin.add_child(tyrion, father=tywin, mother=joanna)

    robert.add_spouse(cersei)

    joffrey = R.person("l6", "Joffrey Baratheon", "Baratheon")
    myrcella = R.person("l7", "Myrcella Baratheon", "Baratheon")
    tommen = R.person("l8", "Tommen Baratheon", "Baratheon")

    cersei.add_child(joffrey, father=jaime, mother=cersei)
    cersei.add_child(myrcella, father=jaime, mother=cersei)
    cersei.add_child(tommen, father=jaime, mother=cersei)

    return tree

import json
from datetime import datetime


class JSONExporter:
    def export(self, tree, view_offset=(0, 0)):
        data = {
            "meta": {
                "root": tree.root.person_id,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "view": {
                    "dx": view_offset[0],
                    "dy": view_offset[1]
                }
            },
            "nodes": [],
            "edges": {
                "marriages": [],
                "children": []
            }
        }

        self._export_nodes(tree, data)
        self._export_edges(tree, data)

        return data

    # ----------------------------
    # Nodes
    # ----------------------------
    def _export_nodes(self, tree, data):
        for p in tree.index.values():
            node = {
                "id": p.person_id,
                "name": p.name,
                "house": p.house,
                "synthetic": getattr(p, "synthetic", False),

                # layout
                "x": p.x,
                "y": p.y,

                # state
                "expanded": p.expanded,

                # relationships (IDs only)
                "father": p.father.person_id if p.father else None,
                "mother": p.mother.person_id if p.mother else None,
                "children": [c.person_id for c in p.children],
                "spouses": [s.person_id for s in p.spouses]
            }
            data["nodes"].append(node)

    # ----------------------------
    # Edges
    # ----------------------------
    def _export_edges(self, tree, data):
        seen_marriages = set()

        for p in tree.index.values():

            # marriage lines
            for ((x1, y1), (x2, y2)) in p.marriage_lines:
                key = tuple(sorted([(x1, y1), (x2, y2)]))
                if key in seen_marriages:
                    continue
                seen_marriages.add(key)

                data["edges"]["marriages"].append({
                    "from": {"x": x1, "y": y1},
                    "to": {"x": x2, "y": y2}
                })

            # child lines
            for ((x1, y1), (x2, y2)) in p.child_lines:
                data["edges"]["children"].append({
                    "from": {"x": x1, "y": y1},
                    "to": {"x": x2, "y": y2}
                })

    # ----------------------------
    # Save helper
    # ----------------------------
    def save(self, tree, path, view_offset=(0, 0)):
        data = self.export(tree, view_offset)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

import tkinter as tk


class TkTreeRenderer:
    def __init__(
        self,
        tree,
        view_offset=(0, 0),
        scale=80,
        padding=50,
        node_radius=18
    ):
        self.tree = tree
        self.dx, self.dy = view_offset
        self.scale = scale
        self.padding = padding
        self.node_radius = node_radius

        # Camera state
        self.pan_x = 0
        self.pan_y = 0
        self.zoom = 1.0

        # Highlight / tooltip state
        self.highlighted = set()
        self.tooltip = None
        self.hovered_person = None

        # ---- Tk root ----
        self.root = tk.Tk()
        self.root.title("Game of Thrones Family Tree")

        # ---- Canvas MUST be created before bindings ----
        self.canvas = tk.Canvas(
            self.root,
            width=1200,
            height=800,
            bg="#111"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # ---- Bindings (NOW canvas exists) ----
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Motion>", self._on_hover)

        # Zoom bindings
        self.canvas.bind("<MouseWheel>", self._on_zoom)   # Windows
        self.canvas.bind("<Button-4>", self._on_zoom)     # Linux scroll up
        self.canvas.bind("<Button-5>", self._on_zoom)     # Linux scroll down

        # Pan bindings
        self.root.bind("<Up>",    lambda e: self._pan(0, -1))
        self.root.bind("<Down>",  lambda e: self._pan(0,  1))
        self.root.bind("<Left>",  lambda e: self._pan(-1, 0))
        self.root.bind("<Right>", lambda e: self._pan(1,  0))
        self.canvas.bind("<Shift-Button-1>", self._on_shift_click)



    def _pan(self, dx, dy):
        self.pan_x += dx
        self.pan_y += dy
        self.draw()

    def _compute_lineage(self, person):
        lineage = set()

        # ancestors
        current = person
        while current:
            lineage.add(current)
            current = current.father or current.mother

        # descendants
        def dfs(node):
            for c in node.children:
                lineage.add(c)
                dfs(c)

        dfs(person)
        return lineage

    def _compute_ancestry(self, person):
        ancestry = set()
        current = person

        while current:
            ancestry.add(current)
            current = current.father or current.mother

        return ancestry


    def _on_zoom(self, event):
        if event.num == 4 or event.delta > 0:
            self.zoom *= 1.1
        else:
            self.zoom /= 1.1
        self.draw()

    def _on_hover(self, event):
        wx = (event.x - self.padding) / self.scale / self.zoom - self.dx - self.pan_x
        wy = (event.y - self.padding) / self.scale / self.zoom - self.dy - self.pan_y

        hovered = None
        for p in self.tree.index.values():
            dx = p.x - wx
            dy = p.y - wy
            if dx * dx + dy * dy <= (self.node_radius / self.scale / self.zoom) ** 2:
                hovered = p
                break

        if hovered != self.hovered_person:
            self.hovered_person = hovered
            self._hide_tooltip()

            if hovered:
                self._show_tooltip(event.x, event.y, hovered)

    def _show_tooltip(self, x, y, person):
        text = person.name
        if person.house:
            text += f"\nHouse: {person.house}"
        if person.father:
            text += f"\nFather: {person.father.name}"
        if person.mother:
            text += f"\nMother: {person.mother.name}"

        self.tooltip = self.canvas.create_text(
            x + 10,
            y + 10,
            text=text,
            anchor=tk.NW,
            fill="#fff",
            font=("Helvetica", 10),
            tags="tooltip"
        )

        bg = self.canvas.bbox(self.tooltip)
        self.canvas.create_rectangle(
            bg,
            fill="#000",
            outline="#aaa",
            tags="tooltip_bg"
        )
        self.canvas.tag_raise(self.tooltip)

    def _hide_tooltip(self):
        self.canvas.delete("tooltip")
        self.canvas.delete("tooltip_bg")
    def _on_shift_click(self, event):
        wx = (event.x - self.padding) / (self.scale * self.zoom) - self.dx - self.pan_x
        wy = (event.y - self.padding) / (self.scale * self.zoom) - self.dy - self.pan_y

        for p in self.tree.index.values():
            dx = p.x - wx
            dy = p.y - wy
            if dx * dx + dy * dy <= (self.node_radius / self.scale / self.zoom) ** 2:

                # Toggle expand ONLY
                p.expanded = not p.expanded

                TreeLayoutEngine().layout(self.tree)
                SpouseLayoutEngine().layout(self.tree)
                ConnectionEngine().build(self.tree)
                CollisionEngine().resolve(self.tree)

                self.draw()
                return


    # ----------------------------
    # Coordinate transform
    # ----------------------------
    def world_to_screen(self, x, y):
        sx = (x + self.dx + self.pan_x) * self.scale * self.zoom + self.padding
        sy = (y + self.dy + self.pan_y) * self.scale * self.zoom + self.padding
        return sx, sy


    def _on_click(self, event):
        # Convert screen → world
        wx = (event.x - self.padding) / (self.scale * self.zoom) - self.dx - self.pan_x
        wy = (event.y - self.padding) / (self.scale * self.zoom) - self.dy - self.pan_y

        for p in self.tree.index.values():
            dx = p.x - wx
            dy = p.y - wy
            if dx * dx + dy * dy <= (self.node_radius / self.scale / self.zoom) ** 2:

                # 🔴 ONLY ancestry highlight
                self.highlighted = self._compute_ancestry(p)

                self.draw()
                return


    # ----------------------------
    # Draw pipeline
    # ----------------------------
    def draw(self):
        self.canvas.delete("all")

        self._draw_connections()
        self._draw_nodes()

        self.root.mainloop()

    # ----------------------------
    # Connections
    # ----------------------------
    def _draw_connections(self):
        for p in self.tree.index.values():

            # marriage lines
            for (a, b) in p.marriage_lines:
                x1, y1 = self.world_to_screen(*a)
                x2, y2 = self.world_to_screen(*b)
                self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill="#888",
                    width=2
                )

            # child lines
            for (a, b) in p.child_lines:
                x1, y1 = self.world_to_screen(*a)
                x2, y2 = self.world_to_screen(*b)
                self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill="#aaa",
                    width=2
                )

    # ----------------------------
    # Nodes
    # ----------------------------
    def _draw_nodes(self):
        for p in self.tree.index.values():
            if not p.expanded and p is not self.tree.root:
                continue

            x, y = self.world_to_screen(p.x, p.y)

            if self.highlighted and p not in self.highlighted:
                color = "#444"   # faded
            else:
                color = self._house_color(p.house)


            self.canvas.create_oval(
                x - self.node_radius,
                y - self.node_radius,
                x + self.node_radius,
                y + self.node_radius,
                fill=color,
                outline="#fff",
                width=2
            )

            self.canvas.create_text(
                x,
                y + self.node_radius + 12,
                text=p.name,
                fill="#eee",
                font=("Helvetica", 10),
                anchor=tk.N
            )
            outline_width = 3 if p in self.highlighted else 1



    # ----------------------------
    # House colors
    # ----------------------------
    def _house_color(self, house):
        return {
            "Stark": "#9bb0c1",
            "Targaryen": "#c0392b",
            "Lannister": "#f1c40f",
            "Baratheon": "#f39c12",
            "Tully": "#3498db",
            None: "#666"
        }.get(house, "#888")


# =========================
# Main
# =========================

if __name__ == "__main__":
    tree = build_got_tree()

    validator = FamilyTreeValidator(tree)
    errors, warnings = validator.validate()
    if errors:
        for e in errors:
            print(e)
        exit()
    """
    # 🔍 Search & focus
    search = SearchController(tree)
    target = search.search_and_focus("jon")
    """
    # Expand everything
    for p in tree.index.values():
        p.expanded = True
    target = None

    # 🧱 Layout pipeline
    TreeLayoutEngine().layout(tree)
    SpouseLayoutEngine().layout(tree)
    ConnectionEngine().build(tree)
    CollisionEngine().resolve(tree)

    # 🎥 Camera offset
    view_offset = (0, 0)
    if target:
        view_offset = compute_view_offset(target)

    # 🖼️ Render
    renderer = TkTreeRenderer(tree, view_offset=view_offset)
    renderer.draw()


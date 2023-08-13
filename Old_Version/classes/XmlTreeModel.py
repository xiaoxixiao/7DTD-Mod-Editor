from PySide6.QtCore import Qt, QModelIndex, QAbstractItemModel


class XmlTreeModel(QAbstractItemModel):
    def __init__(self, root, parent=None):
        super().__init__(parent)
        self.root = root
        self.parents = {c: p for p in self.root.iter() for c in p}

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return len(list(parent.internalPointer()))
        return len(list(self.root))

    def columnCount(self, parent=QModelIndex()):
        return 1

    def index(self, row, column, parent=QModelIndex()):
        if parent.isValid():
            parent_element = parent.internalPointer()
            child_element = list(parent_element)[row]
            return self.createIndex(row, column, child_element)
        return self.createIndex(row, column, list(self.root)[row])

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        child_element = index.internalPointer()
        parent_element = self.parents.get(child_element)
        if parent_element is None or parent_element == self.root:
            return QModelIndex()
        grandparent_element = self.parents.get(parent_element)
        if grandparent_element:
            row = list(grandparent_element).index(parent_element)
        else:
            row = list(self.root).index(parent_element)
        return self.createIndex(row, 0, parent_element)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return index.internalPointer().tag
        return None

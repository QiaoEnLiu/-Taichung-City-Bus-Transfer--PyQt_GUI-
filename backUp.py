def a(self):
    self.list_to_table(self.table_A, self.a_list)
    self.table_A.itemSelectionChanged.connect(lambda:self.a_to_b())
def a_to_b(self):
    self.b = self.item_to_list(self.itemAllRow(self.table_A.selectedItems(), self.A))
    self.list_to_table(self.table_B, self.c_list)
    self.table_B.itemSelectionChanged.connect(lambda:self.b_to_c())
def b_to_c(self):
    self.c = self.item_to_list(self.itemAllRow(self.table_B.selectedItems(), self.B))
    self.list_to_table(self.table_C, self.c_list)
    self.table_C.itemSelectionChanged.connect(lambda:self.c_to_d())  
def c_to_d(self):
    self.d = self.item_to_list(self.itemAllRow(self.table_C.selectedItems(), self.C))

def list_to_table(self, table, list):
        table.setRowCount(len(list))
        for i, item in enumerate(list):
            self.listRowToTableItem(table, i, item)

def item_to_list(self, data):
        if not data:
            return []

        dict_list = [{header: value for header, value in zip(self.headers, data)}]

        return dict_list


def itemAllRow(self, selectedItem, table):
        print(selectedItem)
        if selectedItem:
            row = selectedItem[self.headers.index("1")].row()
            take = [table.item(row, column).text() for column in range(table.columnCount())]
            return take
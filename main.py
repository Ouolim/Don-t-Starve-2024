from PySide6.QtWidgets import QFrame, QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, \
	QScrollArea, QGridLayout, QSizePolicy, QSpacerItem, QPushButton
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import data.items
import data.gameConstants
import databaseCommands
import json


def computeSpace():
	space = 50
	items_in_inventory = 0
	inventory = databaseCommands.fetchInventory()
	for id in inventory:
		# 18 = code for chest, it adds inventory space
		if id == 18:
			space += 20 * inventory[id]
			items_in_inventory -= 1
		items_in_inventory += inventory[id]
	return (space, items_in_inventory)

class IconTextWidget(QFrame):
	def __init__(self, icon_path, text, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# Set a grey border
		self.setFrameShape(QFrame.Box)
		layout = QVBoxLayout()

		icon_label = QLabel()
		pixmap = QPixmap(icon_path)
		pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
		icon_label.setPixmap(pixmap)
		icon_label.setAlignment(Qt.AlignCenter)

		text_label = QLabel(text)
		text_label.setAlignment(Qt.AlignCenter)
		text_label.setStyleSheet("font-size: 22pt;")
		layout.addWidget(icon_label)
		layout.addWidget(text_label)

		# Adjust spacing and margins
		layout.setSpacing(2)
		layout.setContentsMargins(5, 5, 5, 5)

		self.setFixedSize(100, 150)
		self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

		self.setLayout(layout)


class AlertWidget(QWidget):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.layout = QHBoxLayout()

		self.alert_label = QLabel("")
		self.alert_label.setStyleSheet("color: red; font-size: 18pt;")  # Make the text larger
		self.alert_label.setAlignment(Qt.AlignCenter)  # Center the text

		self.layout.addWidget(self.alert_label)
		self.setLayout(self.layout)

	def set_alert_text(self, text, color="red"):
		self.alert_label.setText(text)
		self.alert_label.setStyleSheet(f"color: {color}; font-size: 18pt;")


class WrapWidget(QWidget):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		layout = QVBoxLayout()
		self.scroll_area = QScrollArea()
		self.scroll_area.setWidgetResizable(True)

		self.content_widget = QWidget()
		self.grid_layout = QGridLayout(self.content_widget)

		self.scroll_area.setWidget(self.content_widget)
		layout.addWidget(self.scroll_area)

		self.setLayout(layout)
		self.widgets = []

	def add_item(self, icon_path, text):
		item = IconTextWidget(icon_path, text)
		item.setStyleSheet("font-size: 18pt;")
		row = len(self.widgets) // 20
		col = len(self.widgets) % 20
		self.grid_layout.addWidget(item, row, col)
		self.widgets.append(item)

	def clear(self):
		while ((child := self.grid_layout.layout().takeAt(0)) != None):
			child.widget().deleteLater()
		self.widgets.clear()


class MainWindow(QMainWindow):
	def __init__(self):
		self.targetId = None
		self.targetAmount = None
		self.currentRecepie = {}
		self.crafting = False
		self.activeCrafter = None
		super().__init__()

		self.setWindowTitle("Crafter")
		self.showFullScreen()

		# Main widget and layout
		main_widget = QWidget()
		main_layout = QVBoxLayout()
		self.alert_widget = AlertWidget()
		main_widget.setLayout(main_layout)
		main_widget.setStyleSheet("background-color: white;")
		horizontal_spacer = QSpacerItem(40, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
		# Input field
		self.input_field = QLineEdit()
		self.input_field.returnPressed.connect(self.on_enter_pressed)
		main_layout.addWidget(self.input_field)

		self.crafter_widget = AlertWidget()
		main_layout.addWidget(self.crafter_widget)
		main_layout.addItem(horizontal_spacer)

		main_layout.addWidget(self.alert_widget)
		self.alert_widget.set_alert_text("")

		# Large picture with text under it
		crafting_target_layout = QVBoxLayout()

		self.crafting_target = QLabel()
		self.crafting_target.setAlignment(Qt.AlignCenter)
		crafting_target_layout.addWidget(self.crafting_target)

		self.crafting_target_text = QLabel()
		self.crafting_target_text.setStyleSheet("font-size: 18pt;")
		self.crafting_target_text.setAlignment(Qt.AlignCenter)
		crafting_target_layout.addWidget(self.crafting_target_text)
		main_layout.addLayout(crafting_target_layout)

		# Up facing arrow
		self.arrow = QLabel("↑")
		self.arrow.setAlignment(Qt.AlignCenter)
		self.arrow.setStyleSheet("font-size: 40px;")
		main_layout.addWidget(self.arrow)

		# Smaller pictures with text under them
		self.crafting_ingredients_layout = QHBoxLayout()
		main_layout.addLayout(self.crafting_ingredients_layout)

		self.clearCrafting()
		main_layout.addItem(horizontal_spacer)

		# Horizontal line
		horizontal_line = QFrame()
		horizontal_line.setFrameShape(QFrame.HLine)
		horizontal_line.setFrameShadow(QFrame.Sunken)
		main_layout.addWidget(horizontal_line)

		# Bottom section for icons with text
		self.wrap_widget = WrapWidget()

		bottom_layout = QHBoxLayout()
		self.wrap_widget.setLayout(bottom_layout)
		main_layout.addWidget(self.wrap_widget)

		self.inventory_widget = AlertWidget()
		main_layout.addWidget(self.inventory_widget)
		self.updateInventorySpace()
		self.update_wrap_widget()

		self.setCentralWidget(main_widget)

	def on_enter_pressed(self):
		self.alert_widget.set_alert_text("")
		text = self.input_field.text()
		self.input_field.clear()

		if text in data.gameConstants.childrenCraftingCodes.keys():
			self.activeCrafter = data.gameConstants.childrenCraftingCodes[text]
			self.crafter_widget.set_alert_text(f"Uživatel: {self.activeCrafter}")
			return
		# code for confirmation
		if text == data.gameConstants.yesCode:
			if self.activeCrafter is None:
				self.alert_widget.set_alert_text(f"Pro vytvoření předmětu musíš naskenovat svou kartu")
				return

			if not self.crafting:
				self.alert_widget.set_alert_text(f"Nyní nevytváříš předměty, není co potvrdit")
				return

			# check for sufficient items
			inventory = databaseCommands.fetchInventory()
			inventory.setdefault(0)
			print(inventory, self.currentRecepie)
			for id in self.currentRecepie:
				if id not in inventory or self.currentRecepie[id] > inventory[id]:
					self.alert_widget.set_alert_text(f"Nedostatek předmětu {data.items.gameItems[id]}")
					return
			print("OK")
			for id in self.currentRecepie:
				databaseCommands.insertInventory(int(id), -int(self.currentRecepie[id]))
			databaseCommands.insertInventory(self.targetId, self.targetAmount)
			self.alert_widget.set_alert_text(f"Vyroben {self.targetAmount}x {data.items.gameItems[self.targetId]}", "green")

			self.update_wrap_widget()

			return

		if text[1] != 'r':
			self.clearCrafting()
		# code for item
		if text[0] == 'c':
			row = databaseCommands.codeExist(text)
			print(row)
			if row == None:
				# use used Codes database to determine the error
				row = databaseCommands.codeExist(text, 1)
				if row is None:
					self.alert_widget.set_alert_text("Tento kód neexistuje, kontaktuj vedoucího")
				else:
					self.alert_widget.set_alert_text("Tento kód byl již použit")
				return
			# code is ok, lets use it
			id = row[1]
			amount = row[2]
			assert databaseCommands.insertInventory(id, amount)
			assert databaseCommands.useCode(text)
			print("xd")
			self.alert_widget.set_alert_text(f"OK, do inventáře přibylo {amount}x {data.items.gameItems[id]}", "green")

		# code for recepie
		if text[0] == 'r':
			self.crafting = True
			row = databaseCommands.readRecepie(text)
			print(row)
			if row == None:
				self.alert_widget.set_alert_text("Tento recept neexistuje")
				return
			self.targetId = int(row[1])
			self.targetAmount = int(row[2])
			recepie = json.loads(row[3])
			self.currentRecepie = {}
			for id in recepie:
				self.currentRecepie[int(id)] = int(recepie[id])
			self.setCraftingItem(f"icons/{self.targetId}.png", str(self.targetAmount),
								[f"icons/{i}.png" for i in self.currentRecepie.keys()],
								[str(self.currentRecepie[i]) for i in self.currentRecepie.keys()])

		self.update_wrap_widget()

	def update_wrap_widget(self):
		self.wrap_widget.clear()
		inventory = databaseCommands.fetchInventory()
		for id in inventory:
			if inventory[id] == 0:
				continue
			self.wrap_widget.add_item(f"icons/{id}.png", str(inventory[id]))

	def clearCrafting(self):
		self.crafting = False
		self.setCraftingItem("", "", [], [])
		self.arrow.hide()

	def setCraftingItem(self, targetIconPath, targetText, ingredientIconsPaths, ingredientTexts):
		assert len(ingredientIconsPaths) == len(ingredientTexts)
		self.arrow.show()
		self.crafting_target.setPixmap(QPixmap(targetIconPath).scaled(200, 200, Qt.KeepAspectRatio))
		self.crafting_target_text.setText(targetText)

		## EVIL, i need to delete to depth 2
		while self.crafting_ingredients_layout.count():
			item = self.crafting_ingredients_layout.takeAt(0)
			widget = item.widget()
			if widget is not None:
				widget.deleteLater()
			else:
				while ((child := item.layout().takeAt(0)) != None):
					child.widget().deleteLater()
				print(item.layout().count())
				del item

		for i, icon in enumerate(ingredientIconsPaths):
			crafting_ingredient_layout = QVBoxLayout()
			crafting_ingredient = QLabel()
			crafting_ingredient.setPixmap(QPixmap(icon).scaled(100, 100, Qt.KeepAspectRatio))
			crafting_ingredient.setAlignment(Qt.AlignCenter)
			crafting_ingredient_layout.addWidget(crafting_ingredient)

			crafting_ingredient_text = QLabel(ingredientTexts[i])
			crafting_ingredient_text.setAlignment(Qt.AlignCenter)
			crafting_ingredient_text.setStyleSheet("font-size: 18pt;")
			crafting_ingredient_layout.addWidget(crafting_ingredient_text)
			self.crafting_ingredients_layout.addLayout(crafting_ingredient_layout)

	def updateInventorySpace(self):
		space, items = computeSpace()
		self.inventory_widget.set_alert_text(f"{items}/{space}", "blue")

if __name__ == "__main__":
	app = QApplication([])
	window = MainWindow()
	window.show()
	app.exec()

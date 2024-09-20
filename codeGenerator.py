from barcode import Code128
from barcode.writer import SVGWriter
import os
import data.items
import random
from databaseCommands import insertCode

def gen_code_file(text: str, filename: str, under_text: str = None):
	"""
	Generates SVG file with 128 barcode
	
	Keyword arguments:
	text -- text to convert to barcode
	filename -- file to save the SVG to
	under_text -- text under the batches, filled with text if not used
	"""
	options = {}
	if under_text is not None:
		# text under the batches, is set via human option
		options['human'] = under_text

	with open(filename, "wb") as f:
		writer = SVGWriter()
		writer.set_options(options)
		Code128(text, writer=writer).write(f)


def format_number(i: int, n: int):
	"""
	Format number i to n digits

	Keyword arguments:
	i: formated number
	n: number of digits of return string
	"""
	r = str(i)
	return '0' * (n - len(r)) + r

def gen_codes(texts: list[str], filenamePrefix: str, under_text=None):
	"""
	Generate multiple codes with same under_text in same folder

	Keyword arguments:
	texts: List of strings, codes
	filenamePrefix: path to folder for code files
	under_text: optional, text under code
	"""
	for i in range(len(texts)):
		gen_code_file(texts[i], f'{filenamePrefix}{texts[i]}.svg', under_text)


def printBuild(dir, output):
	"""
	Renders codes from folder to printable format and opens it in browser

	Keyword arguments:
	dir - directory with codes
	output - path to output HTML file
	"""

	import os
	import webbrowser

	with open(output, 'w') as f:
		# I HATE HTML
		f.write("<style>")
		f.write("body {display: flex; flex-wrap: wrap;}")
		f.write("img {margin: 0 auto;}")
		f.write("""div {border: 1px red; border-style: dotted; width: 38.480mm;height: 23.764mm;  justify-content: 
				center;  display: flex;}""")
		f.write("</style>")

		for i, file in enumerate(sorted(os.listdir(dir))):
			f.write(f'<div>')
			f.write(f'<img src = "{os.path.join(dir, file)}"/>')
			f.write(f'</div>')
	webbrowser.open_new_tab(output)

def get_all_folders(directory):
	return [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]

if __name__ == "__main__":
	from pathlib import Path
	from PySide6.QtWidgets import (QMainWindow, QPushButton, QApplication, QWidget,
								   QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QMessageBox, QLineEdit, QListWidget)
	from PySide6.QtCore import Qt

	# Make sure the folder with codes exists
	Path("batches").mkdir(parents=True, exist_ok=True)

	class MainWindow(QMainWindow):
		def __init__(self):
			super().__init__()
			self.setWindowTitle("Batch Code Printer")

			main_widget = QWidget()
			self.setCentralWidget(main_widget)

			main_layout = QVBoxLayout()

			# Batch selector
			batch_selector_layour = QHBoxLayout()
			self.batch_selector = QComboBox()
			batch_selector_layour.addWidget(self.batch_selector)
			self.batch_selector.currentIndexChanged.connect(self.on_batch_switched)
			self.new_batch_button = QPushButton("Create New Batch")
			self.new_batch_button.clicked.connect(self.create_new_batch)
			batch_selector_layour.addWidget(self.new_batch_button)
			main_layout.addLayout(batch_selector_layour)

			# Button for batch printing
			self.print_button = QPushButton("Print Build")
			self.print_button.clicked.connect(self.print_build)
			main_layout.addWidget(self.print_button, alignment=Qt.AlignCenter)


			# Form for item input
			form_layout = QHBoxLayout()
			self.item_selector = QComboBox()
			form_layout.addWidget(self.item_selector)
			self.item_selector.addItems([
				f"{item}:{data.items.gameItems[item]}" for item in data.items.gameItems.keys()])

			self.item_name_input = QLineEdit()
			self.item_name_input.setPlaceholderText("Amount on the paper (usually 1)")
			form_layout.addWidget(self.item_name_input)

			self.item_description_input = QLineEdit()
			self.item_description_input.setPlaceholderText("Print amount")
			form_layout.addWidget(self.item_description_input)

			self.add_item_button = QPushButton("Add Item")
			self.add_item_button.clicked.connect(self.add_item)
			form_layout.addWidget(self.add_item_button)
			main_layout.addLayout(form_layout)


			# List to display batch items
			list_layout = QVBoxLayout()
			self.item_list = QListWidget()
			list_layout.addWidget(self.item_list)
			main_layout.addLayout(list_layout)

			# Set the main layout
			main_widget.setLayout(main_layout)

			# Init with batches from ./batches, all folder names should be valid integers
			try:
				self.batches = sorted(get_all_folders("batches"), key=int)
			except ValueError:
				print("Some folder's in ./batches name is not a valid integer, delete that folder")
				exit(1)
			# If folder empty
			if not self.batches:
				self.create_new_batch()
			self.update_batch_selector()
			self.batch_selector.setCurrentIndex(self.batch_selector.count() - 1)

		def on_batch_switched(self):
			if self.batch_selector.currentText() == "":
				return
			with open(f"batches/{self.batch_selector.currentText()}/info.txt", 'r') as f:
				self.item_list.clear()
				for line in f.readlines():
					self.item_list.addItem(line)

		def add_item(self):
			selected_batch = self.batch_selector.currentText()
			item_id = int(self.item_selector.currentText().split(':')[0])
			item_name = data.items.gameItems[item_id]
			item_amount = int(self.item_name_input.text().strip())
			item_print_amount = int(self.item_description_input.text().strip())

			if selected_batch and item_id and item_amount and item_print_amount:
				item_info = f"{item_name}, {item_amount}x: {item_print_amount} papírků"
				self.item_list.addItem(item_info)

				with open(f"batches/{selected_batch}/info.txt", "a") as f:
					f.write(item_info+'\n')
				with open(f"batches/{selected_batch}/info.txt", "r") as f:
					batch_amount = len(f.readlines())

				# 12 is a code lenght, 3 is 'c' and id, 12-3 = 9
				codes = [f"c{format_number(item_id, 2)}{"".join([chr(random.randrange(ord('a'), ord('z'))) for _ in range(9)])}" for _ in range(item_print_amount)]
				print(codes)
				gen_codes(codes, f"batches/{selected_batch}/codes/{batch_amount}", f"{item_amount}x {item_name}")
				for code in codes:
					insertCode(code, item_id, item_amount)
				self.item_name_input.clear()
				self.item_description_input.clear()
			else:
				QMessageBox.warning(self, "Incomplete Input", "Please fill in both item name and description.")

		def update_batch_selector(self):
			self.batch_selector.clear()
			self.batch_selector.addItems(self.batches)

		def create_new_batch(self):
			new_batch_name = f"{len(self.batches) + 1}"
			Path(f"batches/{new_batch_name}").mkdir(parents=True, exist_ok=True)
			Path(f"batches/{new_batch_name}/codes").mkdir(parents=True, exist_ok=True)
			open(f"batches/{new_batch_name}/info.txt", 'w')

			self.batches.append(new_batch_name)
			self.update_batch_selector()

			self.batch_selector.setCurrentIndex(self.batch_selector.count() - 1)
			QMessageBox.information(self, "New Batch Created", f"{new_batch_name} has been created.")

		def print_build(self):
			selected_batch = self.batch_selector.currentText()
			if selected_batch:
				printBuild(f"batches/{selected_batch}/codes/", "output.html")
			else:
				QMessageBox.warning(self, "No Batch Selected", "Please select a batch to print.")


	app = QApplication([])
	window = MainWindow()
	window.show()
	app.exec()
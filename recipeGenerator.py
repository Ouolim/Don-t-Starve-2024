import json
import os
import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
							   QPushButton, QLineEdit, QComboBox, QScrollArea, QFormLayout,
							   QFrame)

import random
import codeGenerator
import databaseCommands
from data.items import gameItems

class RecipeApp(QWidget):
	def __init__(self):
		super().__init__()
		self.existing_recipes = []
		for row in databaseCommands.fetchRecepies():
			ingredients_bad = json.loads(row[3])
			ingredients = {}
			for id in ingredients_bad:
				ingredients[int(id)] = int(ingredients_bad[id])
			self.existing_recipes.append((*row[0:3], ingredients))

		self.initUI()
		self.refresh_existing_recipes()

	def initUI(self):
		self.setWindowTitle('Recipe Manager')
		self.setGeometry(100, 100, 600, 400)

		main_layout = QVBoxLayout()

		# Print button
		print_btn = QPushButton('Print Recipes')
		print_btn.clicked.connect(self.print_recipes)
		main_layout.addWidget(print_btn)

		# Form layout for recipe input
		form_layout = QFormLayout()

		self.id_selector = QComboBox()
		for id, name in sorted(gameItems.items()):
			self.id_selector.addItem(f"{id}: {name}", id)

		self.amount_input = QLineEdit()
		self.restriction_input = QLineEdit()
		self.restriction_input.setPlaceholderText("Write id of a role that the recipie will be restricted to, leave empty for no restriction")
		form_layout.addRow('Recipe ID:', self.id_selector)
		form_layout.addRow('Amount:', self.amount_input)
		form_layout.addRow('Restriction:', self.restriction_input)

		self.ingredients_layout = QVBoxLayout()


		add_ingredient_btn = QPushButton('Add Ingredient')
		add_ingredient_btn.clicked.connect(self.add_ingredient)

		form_layout.addRow(add_ingredient_btn)
		form_layout.addRow(self.ingredients_layout)

		submit_btn = QPushButton('Submit Recipe')
		submit_btn.clicked.connect(self.submit_recipe)

		form_layout.addRow(submit_btn)

		main_layout.addLayout(form_layout)

		# Scroll area for existing recipes
		self.scroll_area = QScrollArea()
		self.scroll_area.setWidgetResizable(True)

		self.existing_recipes_container = QWidget()
		self.existing_recipes_layout = QVBoxLayout(self.existing_recipes_container)

		self.scroll_area.setWidget(self.existing_recipes_container)

		main_layout.addWidget(self.scroll_area)
		self.setLayout(main_layout)

	def add_ingredient(self):
		ingredient_layout = QHBoxLayout()

		ingredient_selector = QComboBox()
		for id, name in sorted(gameItems.items()):
			ingredient_selector.addItem(f"{id}: {name}", id)

		ingredient_amount = QLineEdit()

		remove_btn = QPushButton('Remove')
		remove_btn.clicked.connect(lambda: self.remove_ingredient(ingredient_layout))

		ingredient_layout.addWidget(ingredient_selector)
		ingredient_layout.addWidget(ingredient_amount)
		ingredient_layout.addWidget(remove_btn)

		self.ingredients_layout.addLayout(ingredient_layout)

	def remove_ingredient(self, layout):
		for i in reversed(range(layout.count())):
			widget = layout.itemAt(i).widget()
			if widget is not None:
				widget.setParent(None)
		self.ingredients_layout.removeItem(layout)

	def submit_recipe(self):
		recipe_id = self.id_selector.currentData()
		amount = self.amount_input.text()
		restriction = self.restriction_input.text()


		ingredients = {}
		for i in range(self.ingredients_layout.count()):
			layout = self.ingredients_layout.itemAt(i)
			if layout is not None:
				widgets = [layout.itemAt(j).widget() for j in range(layout.count())]
				ingredient_id = widgets[0].currentData()
				ingredient_amount = widgets[1].text()
				ingredients[ingredient_id] =  ingredient_amount
		# Generate a unique code for the recipe
		recipe_code = self.generate_recipe_code(recipe_id, amount, ingredients)

		databaseCommands.insertRecepie(recipe_code, recipe_id, amount, json.dumps(ingredients), restriction)

		# Add recipe to the display of existing recipes
		self.add_existing_recipe(recipe_code, recipe_id, amount, ingredients)
		codeGenerator.gen_code_file(recipe_code, f"recipies/{recipe_code}.svg", f"{amount}x {gameItems[recipe_id]}")

		# Sort the existing recipes by ID and refresh the display
		self.existing_recipes.sort(key=lambda x: x[1])  # Sort by recipe ID
		self.refresh_existing_recipes()

	def generate_recipe_code(self, recipe_id, amount, ingredients):
		code = 'r'+codeGenerator.format_number(recipe_id, 2)+''.join([chr(random.randrange(ord('a'),ord('z'))) for _ in range(9)])
		return code

	def get_recipe_by_code(self, code):
		# Implement this function to retrieve a recipe by its code
		for recipe in self.existing_recipes:
			if recipe[0] == code:
				return recipe
		return None

	def add_existing_recipe(self, recipe_code, recipe_id, amount, ingredients):
		self.existing_recipes.append((recipe_code, recipe_id, amount, ingredients))

	def refresh_existing_recipes(self):
		for i in reversed(range(self.existing_recipes_layout.count())):
			widget = self.existing_recipes_layout.itemAt(i).widget()
			if widget is not None:
				widget.setParent(None)

		# Add sorted recipes to the display
		for recipe_code, recipe_id, amount, ingredients in self.existing_recipes:
			recipe_layout = QHBoxLayout()

			recipe_text = f"Code: {recipe_code}, Recipe ID: {recipe_id}, Amount: {amount}, Ingredients: "
			ingredient_texts = [f"{gameItems[id]} ({id}): {ingredients[id]}" for id in ingredients.keys()]
			recipe_text += ", ".join(ingredient_texts)

			recipe_label = QLabel(recipe_text)
			remove_btn = QPushButton(f"Remove {recipe_code}")
			def rem_fn(code):
				return lambda: self.remove_recipe(code)

			remove_btn.clicked.connect(rem_fn(recipe_code))

			recipe_layout.addWidget(recipe_label)
			recipe_layout.addWidget(remove_btn)

			recipe_frame = QFrame()
			recipe_frame.setLayout(recipe_layout)
			self.existing_recipes_layout.addWidget(recipe_frame)

	def remove_recipe(self, code):
		databaseCommands.removeRecepie(code)
		os.remove(f"recipies/{code}.svg")
		self.existing_recipes = [r for r in self.existing_recipes if r[0] != code]
		self.refresh_existing_recipes()


	def print_recipes(self):
		codeGenerator.printBuild('recipies', 'output.html')

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = RecipeApp()
	ex.show()
	sys.exit(app.exec())

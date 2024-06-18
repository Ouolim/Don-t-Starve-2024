from barcode import Code128
from barcode.writer import SVGWriter


def gen_code_file(text: str, filename: str, under_text: str = None):
	"""
	Generates SVG file with 128 barcode
	
	Keyword arguments:
	text -- text to convert to barcode
	filename -- file to save the SVG to
	under_text -- text under the code, filled with text if not used
	"""
	options = {}
	if under_text is not None:
		# text under the code, is set via human option
		options['human'] = under_text

	with open(filename, "wb") as f:
		writer = SVGWriter()
		writer.set_options(options)
		Code128(text, writer=writer).write(f)


def gen_codes(texts, filenamePrefix, under_text=None):
	def format_number(i, n):
		r = str(i)
		return '0' * (n - len(r)) + r

	n = len(str(len(texts)))
	for i in range(len(texts)):
		gen_code_file(texts[i], f'{filenamePrefix}{format_number(i, n)}.svg', under_text)


def printBuild(dir, output):
	import os
	import webbrowser

	# na stranku se vejde 10x4 kodu
	with open(output, 'w') as f:
		# I HATE HTML
		f.write("<style>")
		f.write("body {display: flex; flex-wrap: wrap;}")
		f.write("img {margin: 0 auto;}")
		f.write("""div {border: 1px red; border-style: dotted; width: 38.480mm;height: 23.764mm;  justify-content: 
				center;  display: flex;}""")
		f.write("</style>")

		for i, file in enumerate(os.listdir(dir)):
			f.write(f'<div>')
			f.write(f'<img src = "{os.path.join(dir, file)}"/>')
			f.write(f'</div>')
	webbrowser.open_new_tab(output)


if __name__ == "__main__":
	from pathlib import Path

	Path("test").mkdir(parents=True, exist_ok=True)
	Path("test/multiple_gen_test").mkdir(parents=True, exist_ok=True)

	# example usage
	print("This is a testing usecase")
	gen_code_file('ur_mom_gay', 'test/testCode.svg', 'XD')
	gen_code_file('1111_1111_1111', 'test/1.svg', '1x Dřevo')
	gen_code_file('2222_2222_2222', 'test/2.svg', '1x UstřelPrdel')
	gen_code_file('3111_1131_1111', 'test/3.svg', 'KVAZIMAGICKÝ poděl')
	gen_code_file('4111_1111_1111', 'test/4.svg', 'Došli mi jména')
	gen_code_file('5111_1111_1111', 'test/5.svg', '10x med')
	gen_codes
	gen_codes([11 * str(i) for i in range(60)], 'test/multiple_gen_test/drevo', '1x Dřevo')
	printBuild("test/multiple_gen_test/", "output.html")

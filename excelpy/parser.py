import csv
import multiprocessing
from openpyxl import load_workbook

STOP_CODON = "***STOP***"
DATA_DIR = './data'

queues = {}
processes = []


def csv_writer(filename, queue):
	"""
	"""
	with open(f'{DATA_DIR}/{filename}.csv', "w") as csvFile:
		writer = csv.writer(
			csvFile,
			lineterminator="\n",
			delimiter=",",
			quoting=csv.QUOTE_NONNUMERIC
		)

		while True:
			line = queue.get()

			if line == STOP_CODON:
				return

			print(f'WRITING ({str(line)})')
			writer.writerow(line)


def parse_worksheet(ws):
	"""
	"""
	queue = queues[ws.title]

	for row in ws.rows:
		data = []

		for cell in row:
			print(f'READING ({str(cell.value)})')
			data.append(cell.value)

		queue.put(data)
	queue.put(STOP_CODON)


def parse_workbook(wb):
	"""
	"""
	for ws in wb.worksheets:
		queue = multiprocessing.Queue()
		writer_process = multiprocessing.Process(
			target=csv_writer,
			args=[ws.title, queue]
		)
		writer_process.start()
		processes.append(writer_process)
		queues[ws.title] = queue

		parse_worksheet(ws)


def start():
	"""
	"""
	parse_workbook(load_workbook(
		filename="./test/input.xlsx",
		read_only=True,
		data_only=True
	))

	for process in processes:
		process.join()

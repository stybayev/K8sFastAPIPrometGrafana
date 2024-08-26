import csv
import multiprocessing
import random
import uuid

MIN_ID = 1
MAX_ID = 1000000
NUM_ROWS = 30000000
NUM_PROCESSES = 6


def generate_rows(num_rows: int, queue: multiprocessing.Queue) -> None:
    """
    Генерирует строки и помещает их в очередь
    :param num_rows: количество строк
    :param queue: очередь
    :return:
    """
    rows = []
    for _ in range(num_rows):
        user_id = random.randint(MIN_ID, MAX_ID)
        movie_id = str(uuid.uuid4())
        viewed_frame = random.randint(MIN_ID, MAX_ID)
        rows.append((user_id, movie_id, viewed_frame))
    queue.put(rows)


def write_to_csv(filename: str, num_rows: int, num_processes: int):
    """
    Запись данных в CSV-файл
    :param filename: имя файла
    :param num_rows: количество строк
    :param num_processes: число процессов
    :return:
    """
    # Определяем количество строк на процесс
    rows_per_process = num_rows // num_processes
    processes = []
    queue = multiprocessing.Queue()

    # запускаем процессы
    for _ in range(num_processes):
        process = multiprocessing.Process(target=generate_rows, args=(rows_per_process, queue))
        processes.append(process)
        process.start()

    # собираем данные из процессов
    all_rows = []
    for _ in range(num_processes):
        all_rows.extend(queue.get())

    # ждем завершения всех процессов
    for process in processes:
        process.join()

    # записываем данные в CSV файл
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['user_id', 'movie_id', 'viewed_frame'])
        writer.writerows(all_rows)


if __name__ == '__main__':
    write_to_csv('locust/output.csv', NUM_ROWS, NUM_PROCESSES)

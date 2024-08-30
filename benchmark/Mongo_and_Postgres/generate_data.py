import csv
import multiprocessing
import random
import shutil
import uuid

NUM_ROWS = 10000000
NUM_PROCESSES = 6
NUM_USERS = 10000
NUM_MOVIES = 10000
users = []
films = []


def generate_likes(num_rows: int, queue: multiprocessing.Queue, list_to_write: str) -> None:
    """
    Генерирует строки и помещает их в очередь
    :param num_rows: количество строк
    :param queue: очередь
    :param list_to_write: None
    :return:
    """
    rows = []
    for _ in range(num_rows):
        user_id = random.choice(users)
        movie_id = random.choice(films)
        like = random.choice([0, 10])
        rows.append((user_id, movie_id, like))
    queue.put(rows)


def generate_uuid(num_rows: int, queue: multiprocessing.Queue, list_to_write: str) -> None:
    """
    Генерирует uuid и помещает в очередь
    :param num_rows: число строк
    :param queue: очередь
    :param list_to_write: массив для сохранения данных
    :return:
    """
    rows = []
    for _ in range(num_rows):
        id_record = str(uuid.uuid4())
        rows.append((id_record,))
    queue.put(rows)


def write_to_csv(filename: str, num_rows: int, num_processes: int, mode, list_to_write: str) -> None:
    """
    Запись данных в CSV-файл
    :param filename: имя файла
    :param num_rows: количество строк
    :param num_processes: число процессов
    :param mode: функция для записи
    :param list_to_write: массив для сохранения данных
    :return:
    """
    # Определяем количество строк на процесс
    rows_per_process = num_rows // num_processes
    processes = []
    queue = multiprocessing.Queue()
    if not list_to_write:
        global films
        global users
        with open('mongo/users.csv') as f_users:
            next(f_users)
            for row in f_users:
                users.append(row.strip())
        with open('mongo/movies.csv') as f_movies:
            next(f_movies)
            for row in f_movies:
                films.append(row.strip())

    # запускаем процессы
    for _ in range(num_processes):
        process = multiprocessing.Process(target=mode, args=(rows_per_process, queue, list_to_write))
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
        if list_to_write == 'users':
            writer.writerow(['user_id'])
        if list_to_write == 'movies':
            writer.writerow(['movie_id'])
        if not list_to_write:
            writer.writerow(['user_id', 'movie_id', 'likes'])
        writer.writerows(all_rows)


if __name__ == '__main__':
    # записываем пользователей
    write_to_csv('mongo/users.csv', NUM_USERS, NUM_PROCESSES, generate_uuid, 'users')
    # записываем фильмы
    write_to_csv('mongo/movies.csv', NUM_MOVIES, NUM_PROCESSES, generate_uuid, 'movies')
    # пишем файл с лайками
    write_to_csv('mongo/likes.csv', NUM_ROWS, NUM_PROCESSES, generate_likes, '')
    shutil.copy('mongo/users.csv', 'postgres/users.csv')
    shutil.copy('mongo/movies.csv', 'postgres/movies.csv')
    shutil.copy('mongo/likes.csv', 'postgres/likes.csv')

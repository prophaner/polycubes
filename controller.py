from model import Database, BUFFER_SIZE
from datetime import datetime
from worker import main


if __name__ == '__main__':
    db = Database()
    size = 11
    workers = -(-db.get_count(size - 1) // BUFFER_SIZE)

    for task in [(size, i * BUFFER_SIZE) for i in range(workers)]:
        start = datetime.now()
        main(*task)
        print(task, datetime.now() - start)

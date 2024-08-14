import argparse
import asyncio
import multiprocessing as mp
import os
import time

from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
from math import ceil

from functions import count_words

parser = argparse.ArgumentParser()
parser.add_argument(
    "filepath",
    type=str,
    help=(
        "Absolute path to text file with resources. "
        "For instance: /home/user/dev/async_course/lesson5/data/gram_file"
    )
)

parser.add_argument("word", type=str, help= "Word")


DEFAULT_WORKERS_NUMBER = 16


@contextmanager
def timer(msg: str):
    start = time.perf_counter()
    yield
    print(f"{msg}: {time.perf_counter() - start:.2f} seconds")


def get_workers_number(max_workers: int = DEFAULT_WORKERS_NUMBER):
    return min(os.cpu_count() or 1, max_workers)


def get_current_line_number(file_path):
    """
    Function to get number of lines and not load whole file.
    I need it for monitoring. I implemented another monitoring solution,
    it counts how many bytes processed and show how many percentages of the file processed.
    It allows to not get lines number and save several seconds.
    """
    file_size = os.path.getsize(file_path)
    line_number = 1
    buffer_size = 1024 * 1024  # 1 MB buffer size

    with open(file_path, "rb") as f:
        f.seek(file_size)
        # Get current cursor position
        current_position = f.tell()

        # Move cursor to beginning of the file
        f.seek(0)

        # read file by chunks until current position
        while f.tell() < current_position:
            # if meet position, read only to current position
            chunk_size = min(buffer_size, current_position - f.tell())
            chunk = f.read(chunk_size)
            line_number += chunk.count(b'\n')

        f.seek(current_position)

    return line_number


def get_file_chunks(file_path: str, workers_number: int) -> list[tuple[int, int]]:
    file_size = os.path.getsize(file_path)
    chunk_size = ceil(file_size / workers_number)

    chunks_info = []
    with open(file_path, mode="rb") as f:

        def is_new_line(position):
            if position == 0:
                return True
            else:
                f.seek(position - 1)
                a = f.read(1)
                return a == b"\n"

        def next_line(position):
            f.seek(position)
            f.readline()
            return f.tell()

        chunk_start = 0
        while chunk_start < file_size:
            chunk_end = min(file_size, chunk_start + chunk_size)

            while not is_new_line(chunk_end):
                chunk_end -= 1

            # Next condition is hardly possible. It can happen when file or chunk_size is too small.
            # Or one line is whole chunk or even more (this also hardly possible with our files
            # structure), etc. I reproduce it with 60 rows file.
            if chunk_start == chunk_end:
                chunk_end = next_line(chunk_end)

            chunks_info.append((chunk_start, chunk_end))
            chunk_start = chunk_end

    return chunks_info


def reduce_words(target: dict, source: dict) -> None:
    for key, value in source.items():
        target[key] = target.get(key, 0) + value


async def monitoring(words_counter, words_counter_lock, total_words):
    while True:
        with words_counter_lock:
            print(f"Progress {words_counter.value} / {total_words}")
            if words_counter.value == total_words:
                break
        await asyncio.sleep(1)


async def main() -> None:
    args = parser.parse_args()
    _file_path = args.filepath
    _word = args.word

    loop = asyncio.get_event_loop()
    workers_number = get_workers_number()

    with timer("Getting lines number"):
        lines_number = get_current_line_number(_file_path)

    with timer("Calculating file chunks indexes"):
        file_chunks = get_file_chunks(_file_path, workers_number)

    with mp.Manager() as manager:
        counter = manager.Value("i", 0)
        counter_lock = manager.Lock()

        monitoring_task = asyncio.create_task(
            monitoring(counter, counter_lock, lines_number)
        )

        with ProcessPoolExecutor(max_workers=workers_number) as executor:
            with timer("Processing data"):
                futures = []
                for chunk in file_chunks:
                    futures.append(
                        loop.run_in_executor(
                            executor, count_words, _file_path, chunk, counter, counter_lock
                        )
                    )

                done, _ = await asyncio.wait(futures)

        try:
            monitoring_task.cancel()
            await monitoring_task
        except asyncio.CancelledError:
            pass

    with timer("Reducing words"):
        words = {}
        for result in done:
            reduce_words(words, result.result())

    print("Total words", len(words))
    print("Total count for word", words[_word])


if __name__ == "__main__":
    with timer("Total:"):
        asyncio.run(main())

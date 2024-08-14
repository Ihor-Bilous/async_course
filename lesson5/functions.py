CHUNK_START_INDEX = 0
CHUNK_END_INDEX = 1


def count_words(file_path: str, chunk: tuple[int, int], words_counter, words_counter_lock):
    local_words_counter = 0
    counter_step = 100_000
    # Step is incredibly important, the process is really slow when step is small.
    # I guess printing a lot of information to console makes a process slower.
    chunk_start = chunk[CHUNK_START_INDEX]
    chunk_end = chunk[CHUNK_END_INDEX]
    words = {}

    with open(file_path, "rb") as f:
        # Here I use `rb` instead of `r`. I don't know if it's add something in our case, I tested
        # several times, and it works the same. Maybe in some other cases/files the same position
        # in bytes and text files can refer to different symbols.

        f.seek(chunk_start)
        for line in f:
            chunk_start += len(line)
            if chunk_start > chunk_end:
                break

            # As I mentioned above I use `rb`, that's why I need decode line here
            _word, _, match_count, _ = line.decode("utf-8").strip().split("\t")

            if _word in words:
                words[_word] += int(match_count)
            else:
                words[_word] = int(match_count)

            # monitoring
            local_words_counter += 1
            if local_words_counter % counter_step == 0:
                local_words_counter = 0
                with words_counter_lock:
                    words_counter.value += counter_step
        with words_counter_lock:
            words_counter.value += local_words_counter

    return words

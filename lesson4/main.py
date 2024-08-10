import asyncio
import enum
import random

PHILOSOPHERS_NUMBER = 5
FORKS_NUMBER = PHILOSOPHERS_NUMBER
PHILOSOPHERS_COMPLETED_MEAL = [False] * 5


class State(enum.Enum):
    READY = "READY"
    THINKING = "THINKING"
    HUNGRY = "HUNGRY"
    EATING = "EATING"
    FINISHING_MEAL = "FINISHING_MEAL"


class Fork(asyncio.Lock):
    def __init__(self, fork_id: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._fork_id = fork_id

    def __str__(self) -> str:
        return f"Fork({self._fork_id})"


class Philosopher:
    def __init__(self, id: int, first_fork: Fork, second_fork: Fork):
        self.id = id
        self.first_fork = first_fork
        self.second_fork = second_fork
        self.state = State.READY

    def __repr__(self) -> str:
        return f"Philosopher(id={self.id}, state={self.state})"

    def __str__(self) -> str:
        return repr(self)

    async def dine(self):
        print(f"{self} has started lunch")
        while True:
            await self.think()
            await self.take_forks()
            # break

    async def think(self):
        self.state = State.THINKING
        delay = _get_random_action_time()
        print(f"{self} is thinking for {delay} seconds")
        await asyncio.sleep(delay)

    async def take_forks(self):
        self.state = State.HUNGRY

        async with self.first_fork:
            print(
                f"{self} has just taken the first {self.first_fork} "
                f"and is waiting for the second one"
            )
            async with self.second_fork:
                print(
                    f"{self} has just taken the second "
                    f"{self.second_fork} and is ready to eat"
                )
                await self.eat()
                self.state = State.FINISHING_MEAL

            print(f"{self} has put down the {self.second_fork}")

        print(
            f"{self} has put down "
            f"the {self.first_fork} and going to start thinking"
        )

        completion_status = PHILOSOPHERS_COMPLETED_MEAL[self.id - 1]
        if not completion_status:
             PHILOSOPHERS_COMPLETED_MEAL[self.id - 1] = True

    async def eat(self) -> None:
        self.state = State.EATING
        delay = _get_random_action_time()
        print(f"{self} is eating for {delay} seconds")
        await asyncio.sleep(delay)


def _get_random_action_time() -> float:
    return random.randint(1000, 5000) / 1000


def _get_forks_indexes(philosopher_index: int, forks_number: int = FORKS_NUMBER) -> list[int]:
    """
    Return ordered list of indexes.
    First fork index will be less than index of second.
    This is an important requirement to avoid DeadLocks.
    It guarantees that one of the philosophers is able to acquire two forks.
    Example of first fork (F) for philosophers (P):
        P1: F1
        P2: F1
        P3: F2
        P4: F3
        P5: F4
    From this example we can see that none of the philosophers on the beginning of the process
    try to acquire F(5), it means that either P(1) or P(5) can acquire two forks.
    Example for the situation when we don't have delays.
    With delays at thinking or eating process it's adding additional conditions when the other
    philosopher can acquire two forks too.
    """
    left_index = philosopher_index
    right_index = (philosopher_index + forks_number - 1) % forks_number
    return sorted([left_index, right_index])


async def main():
    forks = [Fork(i + 1) for i in range(FORKS_NUMBER)]

    philosophers = []
    for i in range(PHILOSOPHERS_NUMBER):
        first_fork_index, second_fork_index = _get_forks_indexes(i, FORKS_NUMBER)
        philosophers.append(
            Philosopher(
                id=i + 1, first_fork=forks[first_fork_index], second_fork=forks[second_fork_index]
            )
        )

    tasks = [asyncio.create_task(philosopher.dine()) for philosopher in philosophers]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        for index, completed in enumerate(PHILOSOPHERS_COMPLETED_MEAL, start=1):
            if completed:
                print(f"Philoshoper(id={index}) has finished eating at least once")
            else:
                print(f"Philoshoper(id={index}) has not finished eating yet")

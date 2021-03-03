import asyncio

import pygame


class AsyncClock:
    def __init__(self, time_func=pygame.time.get_ticks):
        self.time_func = time_func
        self.last_tick = time_func() or 0
        self.last_10_diffs = []
 
    async def tick(self, fps=0):
        current = self.time_func()
        time_diff = current - self.last_tick
        self.last_10_diffs.append(time_diff)
        if len(self.last_10_diffs) >= 10:
            del self.last_10_diffs[0]

        if fps <= 0:
            return time_diff

        end_time = (1.0 / fps) * 1000
        delay = (end_time - time_diff) / 1000

        self.last_tick = current

        if delay < 0:
            delay = 0
 
        await asyncio.sleep(delay)

        return time_diff

    def get_fps(self):
        if len(self.last_10_diffs) >= 5:
            return (len(self.last_10_diffs) / sum(self.last_10_diffs)) * 1000
        else:
            return 0




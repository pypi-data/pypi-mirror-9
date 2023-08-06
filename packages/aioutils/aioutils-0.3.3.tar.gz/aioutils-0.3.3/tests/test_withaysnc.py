#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import asyncio
from aioutils import yielding

@asyncio.coroutine
def f(c):
    yield from asyncio.sleep(random.random()*.1)
    return c

@asyncio.coroutine
def g():
    yield from asyncio.sleep(random.random()*.1)
    return random.randint(3, 6)

def test_mixed_with_asyncio():
    chars = 'abcdefg'
    loop = asyncio.get_event_loop()
    def gen_char(num):
        with yielding() as y:
            for c in chars[:num]:
                print(c)
                y.spawn(f(c))
            yield from y

    @asyncio.coroutine
    def gen_async():
        num = yield from g()
        print(num)
        # asyncio.base_events._raise_stop_error()
        loop.stop()
        print('yielding')
        for c in gen_char(num):
            print('yielded', c)
        loop.run_forever()
        #chars = list(gen_char(num))
        #return chars

    t = gen_async()
    # loop.run_until_complete(t)
    asyncio.async(t)
    loop.run_forever()
    print(t)

if __name__ == '__main__':
    test_mixed_with_asyncio()

aioawait
========

This package implements two primitives (**await** and **spawn**) on top
of asyncio infrastructure of Python 3. This two functions allow us to call
asynchronous functions from synchronous code. 
 
Installation
------------

.. code:: bash

    pip3 install aioawait

Example
-------

.. code:: python

    from asyncio.tasks import coroutine, sleep, async
    from aioawait import await, spawn
    
    @coroutine
    def monitor(name, size, total):
        while True:
            print('\ttotal', name, total)
            yield from sleep(1)
    
    @coroutine
    def counter(name, size, total):
        """sums into total all numbers from 0 to size"""
        m = async(monitor(name, size, total))
    
        # monitor could be called using spawn. eg:
        # m = spawn(monitor(name, size, total))
    
        for n in range(size):
            total[0] += n
            if n % 5 == 0:
                print('sleeping', name, n)
                yield from sleep(2)
            else:
                print('counting', name, n)
                yield
    
        # stops monitor
        m.cancel()
    
        return name, 'done', n, total
    
    class Counter:
        """note that this class has no asynchronous code"""
        
        def __init__(self):
            self.cb = spawn(counter('b', 40, [0]))
    
        @property
        def counter_a(self):
            return await(counter('a', 20, [0]))
    
        @property
        def counter_b(self):
            return await(self.cb)
     
    if __name__ == '__main__':
        c = Counter()
        print(c.counter_a)
        print(c.counter_b)

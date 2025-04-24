import multiprocessing
import threading
import random

closing = False

def createSharedEvents(eventNameArray):
    manager = multiprocessing.Manager()
    newDict = {}
    for v in eventNameArray:
        newDict[v] = [manager.Event(), manager.dict()]
    
    def on_exit():
        global closing
        closing = True
        for v in newDict.values():
            v[0].set()
            v[0].clear()
    import atexit
    atexit.register(on_exit)

    return newDict, manager

class Connection:
    def __init__(self, event, func, once = False):
        self._event = event
        self._func = func
        self.Paused = False
        self.Once = once

    def _Call(self, *args):
        if not self.Paused:
            thread1 = threading.Thread(target=self._func, args=(*args,))
            thread1.start()
            if self.Once:
                self.Disconnect()

    def Disconnect(self):
        self._event._Disconnect(self)

class BindableEvent:
    def __init__(self, shared, key):
        self._listening = True
        self._listeners = []
        self._event = shared[key][0]
        self._shared_data = shared[key][1]
        self._listen_thread = None
        self._listen()

    def Connect(self, function, once: bool = False):
        if not callable(function):
            raise ValueError("Not callable. Provide a function")

        if len(self._listeners) == 0:
            self._listen()

        con = Connection(self, function, once)
        self._listeners.append(con)
        return con

    def Fire(self, *args):
        self._shared_data['args'] = args  # Store the arguments in shared data
        self._event.set()
        self._event.clear()

    def Wait(self):
        self._event.wait()

    def _Disconnect(self, connection):
        if connection in self._listeners:
            self._listeners.remove(connection)
        if len(self._listeners) == 0:
            self.unListen()

    def _ExecuteListeners(self):
        for listener in self._listeners:
            listener._Call(*self._shared_data["args"])  # Pass shared data to listeners

    def _listen(self):
        def loop():
            while self._listening and not closing:
                self._event.wait()
                if self._listening and not closing:
                    self._ExecuteListeners()
                self._event.clear()

        if not self._listen_thread or not self._listen_thread.is_alive():
            self._listen_thread = threading.Thread(target=loop, daemon=True)
            self._listen_thread.start()

    def unListen(self):
        self._listening = False

class ThreadSafeDict:
    def __init__(self):
        self.lock = threading.Lock()
        self.dictionary = {}

    def set(self, key, value):
        with self.lock:
            self.dictionary[key] = value
    
    def setFully(self, value):
        with self.lock:
            self.dictionary = value

    def get(self, key):
        with self.lock:
            return self.dictionary.get(key)
        
    def getFully(self):
        with self.lock:
            return self.dictionary

    def delete(self, key):
        with self.lock:
            if key in self.dictionary:
                del self.dictionary[key]

# Usage example
"""
def listener_function(*shared_data):
    print(f"Listener received shared data: {shared_data}")

def fire_event(shared):
    print(f"Firing events from workers...")
    be = BindableEvent(shared, "a")
    time.sleep(1)
    be.Fire("Hello", "from", "worker")
    be.unListen()

if __name__ == "__main__":
    shared, manager = createSharedEvents(["a", "b"])

    be = BindableEvent(shared, "a")
    be.Connect(listener_function)

    p = multiprocessing.Process(target=fire_event, args=(shared,))
    p.start()

    time.sleep(3)

    # Fire another event
    be.Fire("Main process", "says", "hi")

    time.sleep(3)

    print("Main process finished.")
    be.unListen()
    
    time.sleep(2)
"""
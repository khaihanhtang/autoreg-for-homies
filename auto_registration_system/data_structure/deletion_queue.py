class DeletionQueue:

    def __init__(self):
        # self._file_name_deletion_queue: str = file_name_deletion_queue
        self._deletion_queue: list[(int, int)] | None = None
        self._current_index: int = 0

    def enqueue(self, chat_id: int, message_id):
        if self._deletion_queue is None:
            self._deletion_queue = []

        self._deletion_queue.append((chat_id, message_id))

    def dequeue(self) -> (bool, (int, int)):
        if self._deletion_queue is None:
            return False, (0, 0)

        to_be_returned_chat_id, to_be_returned_message_id = self._deletion_queue[self._current_index]
        self._current_index += 1
        if self._current_index == len(self._deletion_queue):
            self._deletion_queue = None
            self._current_index = 0

        return True, (to_be_returned_chat_id, to_be_returned_message_id)

    # def _dump(self):
    #     unhandled_deletion_queue: list[(int, int)] = []
    #     if self._deletion_queue is not None:
    #         unhandled_deletion_queue = self._deletion_queue[self._current_index:]
    #     json.dump(unhandled_deletion_queue, open(self._file_name_deletion_queue, 'w'))
    #
    # def __del__(self):
    #     print("Writing deletion_queue to file!")
    #     self._dump()
    #     print(f"COMPLETE: deletion_queue has been written to {self._file_name_deletion_queue}!")

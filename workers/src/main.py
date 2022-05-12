from base_worker import BaseWorker
import pika


class EmailWorker(BaseWorker):

    def connect_to_queue(self) -> None:
        pass

    def do_action(self) -> None:
        pass

    def enrich_data(self) -> None:
        pass


def main():
    pass

if __name__ == '__main__':
    main()

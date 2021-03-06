from qtpy.QtCore import Signal
from qtpy.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from xicam.core import msg
from xicam.core.threads import invoke_in_main_thread, QThreadFuture


class SummaryWidget(QWidget):
    open = Signal([str, list])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uid_label = QLabel()
        self.open_individually_button = QPushButton("Open")
        self.open_individually_button.setEnabled(False)
        self.open_individually_button.clicked.connect(self._open_individually)
        self.copy_uid_button = QPushButton("Copy UID to Clipboard")
        self.copy_uid_button.setEnabled(False)
        self.copy_uid_button.clicked.connect(self._copy_uid)
        self.streams = QLabel()
        self.entries = []

        uid_layout = QHBoxLayout()
        uid_layout.addWidget(self.uid_label)
        uid_layout.addWidget(self.copy_uid_button)
        layout = QVBoxLayout()
        layout.addWidget(self.open_individually_button)
        layout.addLayout(uid_layout)
        layout.addWidget(self.streams)
        self.setLayout(layout)

        self._tab_titles = ()

    def cache_tab_titles(self, titles):
        self._tab_titles = titles

    def _copy_uid(self):
        QApplication.clipboard().setText(self.uid)

    def _open_individually(self):
        for entry in self.entries:
            self.open.emit(None, [entry])

    def call_entry(self, entries):
        (entry,) = entries
        return entry()

    def set_entries(self, entries):
        try:
            self.entries.clear()
            self.entries.extend(entries)
            if not entries:
                self.uid_label.setText("")
                self.streams.setText("")
                self.copy_uid_button.setEnabled(False)
                self.open_individually_button.setEnabled(False)
            elif len(entries) == 1:
                future = QThreadFuture(self.call_entry, entries, callback_slot=self.call_entries_finished, showBusy=True)
                future.start()
            else:
                self.uid_label.setText("(Multiple Selected)")
                self.streams.setText("")
                self.copy_uid_button.setEnabled(False)
                self.open_individually_button.setText("Open individually")
                self.open_individually_button.setEnabled(True)
        except Exception as e:
            msg.logError(e)
            msg.showMessage("Unable to get data about selected run")

    def call_entries_finished(self, run):
        invoke_in_main_thread(self._call_entries_result, run)

    def _call_entries_result(self, run):
        self.uid = run.metadata["start"]["uid"]
        self.uid_label.setText(self.uid[:8])
        self.copy_uid_button.setEnabled(True)
        self.open_individually_button.setEnabled(True)
        self.open_individually_button.setText("Open")
        num_events = (run.metadata["stop"] or {}).get("num_events")
        if num_events:
            self.streams.setText("Streams:\n" + ("\n".join(f"{k} ({v} Events)" for k, v in num_events.items())))
        else:
            # Either the RunStop document has not been emitted yet or was never
            # emitted due to critical failure or this is an old document stream
            # from before 'num_events' was added to the schema. Get the list of
            # stream names another way, and omit the Event count.
            self.streams.setText("Streams:\n" + ("\n".join(list(run))))

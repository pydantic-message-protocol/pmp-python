import pytest

from pmp.consumer import SpoolConsumer
from pmp.envelope import Envelope
from pmp.exceptions import FilenameCollisionError
from pmp.naming import parse_filename
from pmp.producer import SpoolProducer


def test_emit_writes_into_pending(tmp_path):
    producer = SpoolProducer(tmp_path / "spool", producer_name="repository-a")
    path = producer.emit("build.completed", {"repository": "example", "successful": True})

    assert path.parent.name == "pending"
    assert path.exists()
    sequence, _, _ = parse_filename(path.name)
    assert sequence == 0


def test_emit_rejects_destination_collision(tmp_path, monkeypatch):
    producer = SpoolProducer(tmp_path / "spool", producer_name="repository-a")
    monkeypatch.setattr("pmp.producer.time.time_ns", lambda: 1_700_000_000_000 * 1_000_000)
    monkeypatch.setattr("pmp.producer.os.getpid", lambda: 4242)

    envelope = Envelope.new(
        message_type="build.completed",
        producer="repository-a",
        sequence=0,
        payload={},
    )
    producer._publish(envelope, 0)
    with pytest.raises(FilenameCollisionError):
        producer._publish(envelope, 0)


def test_produce_then_consume_round_trip(tmp_path):
    spool_dir = tmp_path / "spool"
    producer = SpoolProducer(spool_dir, producer_name="repository-a")
    producer.emit("build.completed", {"repository": "example", "successful": True})

    consumer = SpoolConsumer(spool_dir)
    received = []

    @consumer.handler("build.completed")
    def _handle(envelope):
        received.append(envelope)

    claimed = consumer.claim_one()
    assert claimed is not None
    path, envelope = claimed
    assert path.parent.name == "processing"
    assert envelope.message_type == "build.completed"
    assert envelope.payload == {"repository": "example", "successful": True}

    consumer.dispatch(path, envelope)

    assert received == [envelope]
    assert (spool_dir / "completed" / path.name).exists()
    assert not path.exists()


def test_dispatch_moves_to_failed_on_handler_error(tmp_path):
    spool_dir = tmp_path / "spool"
    producer = SpoolProducer(spool_dir, producer_name="repository-a")
    producer.emit("build.completed", {})

    consumer = SpoolConsumer(spool_dir)

    @consumer.handler("build.completed")
    def _handle(envelope):
        raise RuntimeError("boom")

    path, envelope = consumer.claim_one()
    with pytest.raises(RuntimeError):
        consumer.dispatch(path, envelope)

    assert (spool_dir / "failed" / path.name).exists()


def test_dispatch_moves_to_failed_when_no_handler_registered(tmp_path):
    spool_dir = tmp_path / "spool"
    producer = SpoolProducer(spool_dir, producer_name="repository-a")
    producer.emit("build.completed", {})

    consumer = SpoolConsumer(spool_dir)
    path, envelope = consumer.claim_one()
    consumer.dispatch(path, envelope)

    assert (spool_dir / "failed" / path.name).exists()


def test_claim_one_returns_none_when_pending_is_empty(tmp_path):
    consumer = SpoolConsumer(tmp_path / "spool")
    assert consumer.claim_one() is None


def test_claim_one_orders_by_numeric_sequence(tmp_path):
    spool_dir = tmp_path / "spool"
    producer = SpoolProducer(spool_dir, producer_name="repository-a")
    for _ in range(12):
        producer.emit("build.completed", {})

    consumer = SpoolConsumer(spool_dir)
    order = []
    while True:
        claimed = consumer.claim_one()
        if claimed is None:
            break
        path, envelope = claimed
        order.append(envelope.sequence)
        consumer.complete(path)

    assert order == [f"{i:x}" for i in range(12)]

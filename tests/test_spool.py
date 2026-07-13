from pmp.spool import SPOOL_SUBDIRS, Spool


def test_ensure_layout_creates_five_dirs(tmp_path):
    spool = Spool(tmp_path / "spool")
    spool.ensure_layout()
    for name in SPOOL_SUBDIRS:
        assert (tmp_path / "spool" / name).is_dir()


def test_allocate_sequence_starts_at_zero_and_increments(tmp_path):
    spool = Spool(tmp_path / "spool")
    assert spool.allocate_sequence() == 0
    assert spool.allocate_sequence() == 1
    assert spool.allocate_sequence() == 2


def test_allocate_sequence_persists_across_instances(tmp_path):
    root = tmp_path / "spool"
    Spool(root).allocate_sequence()
    Spool(root).allocate_sequence()
    assert Spool(root).allocate_sequence() == 2

from battery_analysis.main.services.file_service import FileService


class TestFileService:
    def setup_method(self):
        self.service = FileService()

    def test_create_directory(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            import os

            new_dir = os.path.join(tmpdir, "test_subdir")
            success, msg = self.service.create_directory(new_dir)
            assert success is True
            assert os.path.exists(new_dir)

    def test_get_file_size(self):
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test data")
            path = f.name
        size = self.service.get_file_size(path)
        assert size == 9
        os.unlink(path)

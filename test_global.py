import pytest
import GlobalAnomaliesProject as gap

nuovo = gap.GlobalAnomaliesProject()

def test_directories():
    assert nuovo.LAST_DIR == "3_ecmwf_ftp_wfp11"

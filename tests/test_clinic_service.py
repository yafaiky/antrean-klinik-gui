"""Unit test untuk validator tambahan dan layanan bisnis Heptamed Klinik."""

import unittest

from src.services.clinic_service import ClinicService
from src.utils.validators import (
    calculate_age_from_indonesian_date,
    format_thousand,
    validate_nik,
    validate_phone,
)


class TestClinicValidators(unittest.TestCase):
    """Pengujian validator NIK, telepon, dan tanggal lahir Indonesia."""

    def test_validate_nik(self) -> None:
        ok, _ = validate_nik("3275015403960001")
        self.assertTrue(ok)
        ok_short, msg_short = validate_nik("327501540396001")
        self.assertFalse(ok_short)
        self.assertIn("15 digit", msg_short)
        ok_alpha, _ = validate_nik("327501540396000a")
        self.assertFalse(ok_alpha)

    def test_calculate_age_indonesian_date(self) -> None:
        self.assertEqual(calculate_age_from_indonesian_date("14 Maret 1996"), 30)
        self.assertIsNone(calculate_age_from_indonesian_date("tanggal salah"))

    def test_validate_phone_and_format(self) -> None:
        self.assertTrue(validate_phone("0812 3456 7890")[0])
        self.assertFalse(validate_phone("123")[0])
        self.assertEqual(format_thousand(1248), "1.248")


class TestClinicService(unittest.TestCase):
    """Pengujian alur registrasi, antrean poli, filter pasien, dan laporan."""

    def setUp(self) -> None:
        self.svc = ClinicService()

    def test_initial_kpis_match_design(self) -> None:
        p_kpis = self.svc.get_patient_kpis()
        self.assertEqual(p_kpis["total"], 1248)
        self.assertEqual(p_kpis["baru"], 86)
        self.assertEqual(p_kpis["bpjs"], 986)
        self.assertEqual(p_kpis["umum"], 262)

        q_kpis = self.svc.get_queue_kpis()
        self.assertEqual(q_kpis["total"], 6)
        self.assertEqual(q_kpis["menunggu"], 4)
        self.assertEqual(q_kpis["diperiksa"], 1)
        self.assertEqual(q_kpis["selesai"], 1)

    def test_register_and_queue_flow(self) -> None:
        patient, qitem = self.svc.register_patient(
            nik="3275015403960001",
            nama="Salsabila Putri",
            tanggal_lahir="14 Maret 1996",
            usia=30,
            jenis_kelamin="Perempuan",
            telepon="0812 3456 7890",
            alamat="Jl. Melati No. 18, Bandung",
            poli="Poli Umum",
        )
        self.assertEqual(patient.no_rm, "RM-00253")
        self.assertEqual(qitem.no_antrean, "A-004")
        self.assertEqual(qitem.status, "Menunggu")

        self.svc.call_queue_item("A-004")
        active = self.svc.get_active_serving()
        self.assertIsNotNone(active)
        self.assertEqual(active.no_antrean, "A-004")

        self.svc.complete_queue_item("A-004")
        self.assertEqual(qitem.status, "Selesai")

    def test_report_data(self) -> None:
        rep = self.svc.get_report_data("1–18 November 2026", "Semua poli")
        self.assertEqual(rep["total_kunjungan"], 642)
        self.assertEqual(rep["pasien_baru"], 86)
        self.assertEqual(rep["pasien_lama"], 556)
        self.assertEqual(rep["rata_rata"], 36)
        self.assertEqual(len(rep["recap"]), 3)


if __name__ == "__main__":
    unittest.main()

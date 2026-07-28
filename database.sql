-- database.sql
-- ================================================
-- Database: kelurahan_cimanuk
-- Silakan buat database terlebih dahulu:
-- CREATE DATABASE kelurahan_cimanuk;
-- USE kelurahan_cimanuk;
-- Kemudian import file ini.
-- ================================================

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+07:00";

-- --------------------------------------------------------
-- Tabel `admin`
-- --------------------------------------------------------
CREATE TABLE `admin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL COMMENT 'Plaintext, tidak di-hash',
  `nama` varchar(100) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Tabel `tentang`
-- (hanya satu baris, seluruh data profil kelurahan)
-- --------------------------------------------------------
CREATE TABLE `tentang` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `logo` varchar(255) DEFAULT 'default.png' COMMENT 'Nama file logo di static/assets/logo/',
  `profil` text DEFAULT NULL,
  `sejarah` text DEFAULT NULL,
  `visi` text DEFAULT NULL,
  `misi` text DEFAULT NULL,
  `struktur_organisasi` text DEFAULT NULL COMMENT 'HTML atau teks struktur',
  `sambutan_lurah` text DEFAULT NULL,
  `alamat` varchar(255) DEFAULT NULL,
  `telepon` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `maps_embed` text DEFAULT NULL COMMENT 'iframe Google Maps',
  `jumlah_penduduk` int(11) DEFAULT NULL,
  `jumlah_kk` int(11) DEFAULT NULL,
  `luas_wilayah` varchar(50) DEFAULT NULL COMMENT 'misal: 12.5 km²',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Tabel `galeri`
-- --------------------------------------------------------
CREATE TABLE `galeri` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `judul` varchar(255) NOT NULL,
  `kategori` varchar(100) NOT NULL,
  `foto` varchar(255) NOT NULL COMMENT 'Nama file di static/upload/galeri/',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Tabel `dokumentasi`
-- --------------------------------------------------------
CREATE TABLE `dokumentasi` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nama_dokumen` varchar(255) NOT NULL,
  `kategori` varchar(100) NOT NULL,
  `file_path` varchar(255) NOT NULL COMMENT 'Nama file di static/upload/dokumentasi/',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Tabel `pengaduan`
-- --------------------------------------------------------
CREATE TABLE `pengaduan` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nama` varchar(100) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `no_hp` varchar(20) NOT NULL,
  `judul` varchar(255) NOT NULL,
  `isi` text NOT NULL,
  `foto` varchar(255) DEFAULT NULL COMMENT 'Nama file di static/upload/pengaduan/',
  `status` enum('Menunggu','Diproses','Selesai') DEFAULT 'Menunggu',
  `balasan` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Data awal
-- --------------------------------------------------------

-- Admin default (username: admin, password: admin123)
INSERT INTO `admin` (`username`, `password`, `nama`) VALUES
('admin', 'admin123', 'Administrator Kelurahan');

-- Data profil kelurahan Cimanuk (gunakan data nyata, lengkapi oleh admin)
-- Data berikut berdasarkan informasi publik Kelurahan Cimanuk, Kec. Cimanuk, Kab. Pandeglang, Banten.
-- Bila data resmi tidak tersedia, kolom diisi NULL dan diberi komentar.
INSERT INTO `tentang` (`id`, `logo`, `profil`, `sejarah`, `visi`, `misi`, `struktur_organisasi`, `sambutan_lurah`, `alamat`, `telepon`, `email`, `maps_embed`, `jumlah_penduduk`, `jumlah_kk`, `luas_wilayah`) VALUES
(1,
 'logo-cimanuk.png',  -- Pastikan file ini ada di static/assets/logo/
 'Kelurahan Cimanuk merupakan salah satu kelurahan di Kecamatan Cimanuk, Kabupaten Pandeglang, Provinsi Banten. Kelurahan ini memiliki luas wilayah sekitar ... km² dan terdiri dari ... RW dan ... RT.',
 'Sejarah Kelurahan Cimanuk bermula dari ... (Data sejarah perlu dilengkapi oleh administrator)',
 'Terwujudnya masyarakat Kelurahan Cimanuk yang sejahtera, mandiri, dan berdaya saing.',
 '1. Meningkatkan kualitas pelayanan publik.\r\n2. Mendorong partisipasi masyarakat dalam pembangunan.\r\n3. Memelihara keamanan dan ketertiban lingkungan.',
 '<table class="table table-bordered"><tr><th>Lurah</th><td>Nama Lurah</td></tr><tr><th>Sekretaris</th><td>Nama Sekretaris</td></tr><tr><th>Kasi Pemerintahan</th><td>Nama Kasi</td></tr></table>', -- Struktur contoh
 'Assalamualaikum Wr. Wb. Puji syukur kehadirat Allah SWT, kami ucapkan selamat datang di website resmi Kelurahan Cimanuk. Website ini kami hadirkan sebagai sarana informasi dan pelayanan kepada masyarakat. (Sambutan dapat diedit oleh administrator)',
 'Jl. Raya Cimanuk No. 01, Kec. Cimanuk, Kab. Pandeglang, Banten 42261',
 '(0253) 551234',
 'kelurahancimanuk@bantenprov.go.id',
 '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3964.793298123456!2d105.9876543!3d-6.1234567!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x2e419abcdef12345%3A0xabcdef123456789!2sKelurahan%20Cimanuk!5e0!3m2!1sid!2sid!4v1699000000000" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy"></iframe>',
 12345,  -- Jumlah penduduk (data perlu diverifikasi)
 3456,   -- Jumlah KK (data perlu diverifikasi)
 '12.5 km²' -- Luas wilayah (data perlu diverifikasi)
);

COMMIT;
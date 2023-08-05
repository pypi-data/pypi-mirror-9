# This file is dual licensed under the terms of the Apache License, Version
# 2.0, and the BSD License. See the LICENSE file in the root of this repository
# for complete details.

from __future__ import absolute_import, division, print_function

import binascii
import datetime
import os

import pytest

from cryptography import x509
from cryptography.hazmat.backends.interfaces import (
    DSABackend, EllipticCurveBackend, RSABackend, X509Backend
)
from cryptography.hazmat.primitives import hashes, interfaces
from cryptography.hazmat.primitives.asymmetric import ec

from .hazmat.primitives.test_ec import _skip_curve_unsupported
from .utils import load_vectors_from_file


def _load_cert(filename, loader, backend):
    cert = load_vectors_from_file(
        filename=filename,
        loader=lambda pemfile: loader(pemfile.read(), backend),
        mode="rb"
    )
    return cert


@pytest.mark.requires_backend_interface(interface=RSABackend)
@pytest.mark.requires_backend_interface(interface=X509Backend)
class TestRSACertificate(object):
    def test_load_pem_cert(self, backend):
        cert = _load_cert(
            os.path.join("x509", "custom", "post2000utctime.pem"),
            x509.load_pem_x509_certificate,
            backend
        )
        assert isinstance(cert, x509.Certificate)
        assert cert.serial == 11559813051657483483
        fingerprint = binascii.hexlify(cert.fingerprint(hashes.SHA1()))
        assert fingerprint == b"2b619ed04bfc9c3b08eb677d272192286a0947a8"

    def test_load_der_cert(self, backend):
        cert = _load_cert(
            os.path.join("x509", "PKITS_data", "certs", "GoodCACert.crt"),
            x509.load_der_x509_certificate,
            backend
        )
        assert isinstance(cert, x509.Certificate)
        assert cert.serial == 2
        fingerprint = binascii.hexlify(cert.fingerprint(hashes.SHA1()))
        assert fingerprint == b"6f49779533d565e8b7c1062503eab41492c38e4d"

    def test_load_good_ca_cert(self, backend):
        cert = _load_cert(
            os.path.join("x509", "PKITS_data", "certs", "GoodCACert.crt"),
            x509.load_der_x509_certificate,
            backend
        )

        assert cert.not_valid_before == datetime.datetime(2010, 1, 1, 8, 30)
        assert cert.not_valid_after == datetime.datetime(2030, 12, 31, 8, 30)
        assert cert.serial == 2
        public_key = cert.public_key()
        assert isinstance(public_key, interfaces.RSAPublicKey)
        assert cert.version is x509.Version.v3
        fingerprint = binascii.hexlify(cert.fingerprint(hashes.SHA1()))
        assert fingerprint == b"6f49779533d565e8b7c1062503eab41492c38e4d"

    def test_utc_pre_2000_not_before_cert(self, backend):
        cert = _load_cert(
            os.path.join(
                "x509", "PKITS_data", "certs",
                "Validpre2000UTCnotBeforeDateTest3EE.crt"
            ),
            x509.load_der_x509_certificate,
            backend
        )

        assert cert.not_valid_before == datetime.datetime(1950, 1, 1, 12, 1)

    def test_pre_2000_utc_not_after_cert(self, backend):
        cert = _load_cert(
            os.path.join(
                "x509", "PKITS_data", "certs",
                "Invalidpre2000UTCEEnotAfterDateTest7EE.crt"
            ),
            x509.load_der_x509_certificate,
            backend
        )

        assert cert.not_valid_after == datetime.datetime(1999, 1, 1, 12, 1)

    def test_post_2000_utc_cert(self, backend):
        cert = _load_cert(
            os.path.join("x509", "custom", "post2000utctime.pem"),
            x509.load_pem_x509_certificate,
            backend
        )
        assert cert.not_valid_before == datetime.datetime(
            2014, 11, 26, 21, 41, 20
        )
        assert cert.not_valid_after == datetime.datetime(
            2014, 12, 26, 21, 41, 20
        )

    def test_generalized_time_not_before_cert(self, backend):
        cert = _load_cert(
            os.path.join(
                "x509", "PKITS_data", "certs",
                "ValidGeneralizedTimenotBeforeDateTest4EE.crt"
            ),
            x509.load_der_x509_certificate,
            backend
        )
        assert cert.not_valid_before == datetime.datetime(2002, 1, 1, 12, 1)
        assert cert.not_valid_after == datetime.datetime(2030, 12, 31, 8, 30)
        assert cert.version is x509.Version.v3

    def test_generalized_time_not_after_cert(self, backend):
        cert = _load_cert(
            os.path.join(
                "x509", "PKITS_data", "certs",
                "ValidGeneralizedTimenotAfterDateTest8EE.crt"
            ),
            x509.load_der_x509_certificate,
            backend
        )
        assert cert.not_valid_before == datetime.datetime(2010, 1, 1, 8, 30)
        assert cert.not_valid_after == datetime.datetime(2050, 1, 1, 12, 1)
        assert cert.version is x509.Version.v3

    def test_invalid_version_cert(self, backend):
        cert = _load_cert(
            os.path.join("x509", "custom", "invalid_version.pem"),
            x509.load_pem_x509_certificate,
            backend
        )
        with pytest.raises(x509.InvalidVersion) as exc:
            cert.version

        assert exc.value.parsed_version == 7

    def test_version_1_cert(self, backend):
        cert = _load_cert(
            os.path.join("x509", "v1_cert.pem"),
            x509.load_pem_x509_certificate,
            backend
        )
        assert cert.version is x509.Version.v1

    def test_invalid_pem(self, backend):
        with pytest.raises(ValueError):
            x509.load_pem_x509_certificate(b"notacert", backend)

    def test_invalid_der(self, backend):
        with pytest.raises(ValueError):
            x509.load_der_x509_certificate(b"notacert", backend)


@pytest.mark.requires_backend_interface(interface=DSABackend)
@pytest.mark.requires_backend_interface(interface=X509Backend)
class TestDSACertificate(object):
    def test_load_dsa_cert(self, backend):
        cert = _load_cert(
            os.path.join("x509", "custom", "dsa_selfsigned_ca.pem"),
            x509.load_pem_x509_certificate,
            backend
        )
        public_key = cert.public_key()
        assert isinstance(public_key, interfaces.DSAPublicKey)
        if isinstance(public_key, interfaces.DSAPublicKeyWithNumbers):
            num = public_key.public_numbers()
            assert num.y == int(
                "4c08bfe5f2d76649c80acf7d431f6ae2124b217abc8c9f6aca776ddfa94"
                "53b6656f13e543684cd5f6431a314377d2abfa068b7080cb8ddc065afc2"
                "dea559f0b584c97a2b235b9b69b46bc6de1aed422a6f341832618bcaae2"
                "198aba388099dafb05ff0b5efecb3b0ae169a62e1c72022af50ae68af3b"
                "033c18e6eec1f7df4692c456ccafb79cc7e08da0a5786e9816ceda651d6"
                "1b4bb7b81c2783da97cea62df67af5e85991fdc13aff10fc60e06586386"
                "b96bb78d65750f542f86951e05a6d81baadbcd35a2e5cad4119923ae6a2"
                "002091a3d17017f93c52970113cdc119970b9074ca506eac91c3dd37632"
                "5df4af6b3911ef267d26623a5a1c5df4a6d13f1c", 16
            )
            assert num.parameter_numbers.g == int(
                "4b7ced71dc353965ecc10d441a9a06fc24943a32d66429dd5ef44d43e67"
                "d789d99770aec32c0415dc92970880872da45fef8dd1e115a3e4801387b"
                "a6d755861f062fd3b6e9ea8e2641152339b828315b1528ee6c7b79458d2"
                "1f3db973f6fc303f9397174c2799dd2351282aa2d8842c357a73495bbaa"
                "c4932786414c55e60d73169f5761036fba29e9eebfb049f8a3b1b7cee6f"
                "3fbfa136205f130bee2cf5b9c38dc1095d4006f2e73335c07352c64130a"
                "1ab2b89f13b48f628d3cc3868beece9bb7beade9f830eacc6fa241425c0"
                "b3fcc0df416a0c89f7bf35668d765ec95cdcfbe9caff49cfc156c668c76"
                "fa6247676a6d3ac945844a083509c6a1b436baca", 16
            )
            assert num.parameter_numbers.p == int(
                "bfade6048e373cd4e48b677e878c8e5b08c02102ae04eb2cb5c46a523a3"
                "af1c73d16b24f34a4964781ae7e50500e21777754a670bd19a7420d6330"
                "84e5556e33ca2c0e7d547ea5f46a07a01bf8669ae3bdec042d9b2ae5e6e"
                "cf49f00ba9dac99ab6eff140d2cedf722ee62c2f9736857971444c25d0a"
                "33d2017dc36d682a1054fe2a9428dda355a851ce6e6d61e03e419fd4ca4"
                "e703313743d86caa885930f62ed5bf342d8165627681e9cc3244ba72aa2"
                "2148400a6bbe80154e855d042c9dc2a3405f1e517be9dea50562f56da93"
                "f6085f844a7e705c1f043e65751c583b80d29103e590ccb26efdaa0893d"
                "833e36468f3907cfca788a3cb790f0341c8a31bf", 16
            )
            assert num.parameter_numbers.q == int(
                "822ff5d234e073b901cf5941f58e1f538e71d40d", 16
            )


@pytest.mark.requires_backend_interface(interface=EllipticCurveBackend)
@pytest.mark.requires_backend_interface(interface=X509Backend)
class TestECDSACertificate(object):
    def test_load_ecdsa_cert(self, backend):
        _skip_curve_unsupported(backend, ec.SECP384R1())
        cert = _load_cert(
            os.path.join("x509", "ecdsa_root.pem"),
            x509.load_pem_x509_certificate,
            backend
        )
        public_key = cert.public_key()
        assert isinstance(public_key, interfaces.EllipticCurvePublicKey)
        if isinstance(
            public_key, interfaces.EllipticCurvePublicKeyWithNumbers
        ):
            num = public_key.public_numbers()
            assert num.x == int(
                "dda7d9bb8ab80bfb0b7f21d2f0bebe73f3335d1abc34eadec69bbcd095f"
                "6f0ccd00bba615b51467e9e2d9fee8e630c17", 16
            )
            assert num.y == int(
                "ec0770f5cf842e40839ce83f416d3badd3a4145936789d0343ee10136c7"
                "2deae88a7a16bb543ce67dc23ff031ca3e23e", 16
            )
            assert isinstance(num.curve, ec.SECP384R1)

    def test_load_ecdsa_no_named_curve(self, backend):
        _skip_curve_unsupported(backend, ec.SECP256R1())
        cert = _load_cert(
            os.path.join("x509", "custom", "ec_no_named_curve.pem"),
            x509.load_pem_x509_certificate,
            backend
        )
        with pytest.raises(NotImplementedError):
            cert.public_key()

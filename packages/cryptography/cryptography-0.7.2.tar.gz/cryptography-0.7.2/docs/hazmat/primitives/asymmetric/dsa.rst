.. hazmat::

DSA
===

.. currentmodule:: cryptography.hazmat.primitives.asymmetric.dsa

`DSA`_ is a `public-key`_ algorithm for signing messages.

Generation
~~~~~~~~~~

.. function:: generate_private_key(key_size, backend)

    .. versionadded:: 0.5

    Generate a DSA private key from the given key size. This function will
    generate a new set of parameters and key in one step.

    :param int key_size: The length of the modulus in bits. It should be
        either 1024, 2048 or 3072. For keys generated in 2014 this should
        be `at least 2048`_ (See page 41).  Note that some applications
        (such as SSH) have not yet gained support for larger key sizes
        specified in FIPS 186-3 and are still restricted to only the
        1024-bit keys specified in FIPS 186-2.

    :param backend: A
        :class:`~cryptography.hazmat.backends.interfaces.DSABackend`
        provider.

    :return: A :class:`~cryptography.hazmat.primitives.interfaces.DSAPrivateKey`
        provider.

    :raises cryptography.exceptions.UnsupportedAlgorithm: This is raised if
        the provided ``backend`` does not implement
        :class:`~cryptography.hazmat.backends.interfaces.DSABackend`

.. function:: generate_parameters(key_size, backend)

    .. versionadded:: 0.5

    Generate DSA parameters using the provided ``backend``.

    :param int key_size: The length of the modulus in bits. It should be
        either 1024, 2048 or 3072. For keys generated in 2014 this should
        be `at least 2048`_ (See page 41).  Note that some applications
        (such as SSH) have not yet gained support for larger key sizes
        specified in FIPS 186-3 and are still restricted to only the
        1024-bit keys specified in FIPS 186-2.

    :param backend: A
        :class:`~cryptography.hazmat.backends.interfaces.DSABackend`
        provider.

    :return: A :class:`~cryptography.hazmat.primitives.interfaces.DSAParameters`
        provider.

    :raises cryptography.exceptions.UnsupportedAlgorithm: This is raised if
        the provided ``backend`` does not implement
        :class:`~cryptography.hazmat.backends.interfaces.DSABackend`

Signing
~~~~~~~

Using a :class:`~cryptography.hazmat.primitives.interfaces.DSAPrivateKey`
provider.

.. doctest::

    >>> from cryptography.hazmat.backends import default_backend
    >>> from cryptography.hazmat.primitives import hashes
    >>> from cryptography.hazmat.primitives.asymmetric import dsa
    >>> private_key = dsa.generate_private_key(
    ...     key_size=1024,
    ...     backend=default_backend()
    ... )
    >>> signer = private_key.signer(hashes.SHA256())
    >>> data = b"this is some data I'd like to sign"
    >>> signer.update(data)
    >>> signature = signer.finalize()

The ``signature`` is a ``bytes`` object, whose contents is DER encoded as
described in :rfc:`6979`. This can be decoded using
:func:`~cryptography.hazmat.primitives.asymmetric.utils.decode_rfc6979_signature`.

Verification
~~~~~~~~~~~~

Using a :class:`~cryptography.hazmat.primitives.interfaces.DSAPublicKey`
provider.

.. doctest::

    >>> public_key = private_key.public_key()
    >>> verifier = public_key.verifier(signature, hashes.SHA256())
    >>> verifier.update(data)
    >>> verifier.verify()

``verifier()`` takes the signature in the same format as is returned by
``signer.finalize()``.

``verify()`` will raise an :class:`~cryptography.exceptions.InvalidSignature`
exception if the signature isn't valid.

Numbers
~~~~~~~

.. class:: DSAParameterNumbers(p, q, g)

    .. versionadded:: 0.5

    The collection of integers that make up a set of DSA parameters.

    .. attribute:: p

        :type: int

        The public modulus.

    .. attribute:: q

        :type: int

        The sub-group order.

    .. attribute:: g

        :type: int

        The generator.

    .. method:: parameters(backend)

        :param backend: A
            :class:`~cryptography.hazmat.backends.interfaces.DSABackend`
            provider.

        :returns: A new instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.DSAParameters`
            provider.

.. class:: DSAPublicNumbers(y, parameter_numbers)

    .. versionadded:: 0.5

    The collection of integers that make up a DSA public key.

    .. attribute:: y

        :type: int

        The public value ``y``.

    .. attribute:: parameter_numbers

        :type: :class:`~cryptography.hazmat.primitives.dsa.DSAParameterNumbers`

        The :class:`~cryptography.hazmat.primitives.dsa.DSAParameterNumbers`
        associated with the public key.

    .. method:: public_key(backend)

        :param backend: A
            :class:`~cryptography.hazmat.backends.interfaces.DSABackend`
            provider.

        :returns: A new instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.DSAPublicKey`
            provider.

.. class:: DSAPrivateNumbers(x, public_numbers)

    .. versionadded:: 0.5

    The collection of integers that make up a DSA private key.

    .. warning::

        Revealing the value of ``x`` will compromise the security of any
        cryptographic operations performed.

    .. attribute:: x

        :type: int

        The private value ``x``.

    .. attribute:: public_numbers

        :type: :class:`~cryptography.hazmat.primitives.dsa.DSAPublicNumbers`

        The :class:`~cryptography.hazmat.primitives.dsa.DSAPublicNumbers`
        associated with the private key.

    .. method:: private_key(backend)

        :param backend: A
            :class:`~cryptography.hazmat.backends.interfaces.DSABackend`
            provider.

        :returns: A new instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.DSAPrivateKey`
            provider.


.. _`DSA`: https://en.wikipedia.org/wiki/Digital_Signature_Algorithm
.. _`public-key`: https://en.wikipedia.org/wiki/Public-key_cryptography
.. _`FIPS 186-4`: http://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-4.pdf
.. _`at least 2048`: http://www.ecrypt.eu.org/documents/D.SPA.20.pdf

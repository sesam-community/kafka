class CertificateHandler:
    """Write a certificate to disk."""

    def __init__(self, certificate: str, file: str):
        """Constructor.

        :param certificate: A string representation of the certificate.
        :type certificate: str
        :param file: File name for which to write the certificate into.
        :type file: str
        """
        self.certificate = certificate
        self.file = file

    def write(self):
        """Write certificate to disk."""
        open(self.file, "wb").write(bytes(self.certificate, "ascii"))

    def __repr__(self):
        str_repr = \
                f"\nFile       : {self.file}" \
                f"\nCertificate: {self.certificate[-42:]}"  # last 42 chars

        return str_repr


if __name__ == "__main__":
    cert = CertificateHandler("foo-test", "bar.pem")
    print(cert.__doc__)
    print(cert)
    cert.write()

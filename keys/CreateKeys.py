from cryptography import x509
from cryptography.hazmat.backends import default_backend
from getpass import getpass
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes

print("\n\n\n\n")

def generateprivatekey(filename: str, password: str):
    privatekey = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )

    utf8pass = password.encode("utf-8")
    algorithm = serialization.BestAvailableEncryption(utf8pass)

    with open(filename, "wb") as keyfile:
        keyfile.write(
            privatekey.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=algorithm,
            )
        )

    return privatekey

def generatepublickey(privatekey, filename, **kwargs):
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, kwargs["country"]),
            x509.NameAttribute(
                NameOID.STATE_OR_PROVINCE_NAME, kwargs["state"]
            ),
            x509.NameAttribute(NameOID.LOCALITY_NAME, kwargs["locality"]),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, kwargs["org"]),
            x509.NameAttribute(NameOID.COMMON_NAME, kwargs["hostname"]),
        ]
    )

    # Because this is self signed, the issuer is always the subject
    issuer = subject

    # This certificate is valid from now until 30 days
    validfrom = datetime.utcnow()
    validto = validfrom + timedelta(days=30)

    # Used to build the certificate
    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(privatekey.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(validfrom)
        .not_valid_after(validto)
        .add_extension(x509.BasicConstraints(ca=True,
            path_length=None), critical=True)
    )

    # Sign the certificate with the private key
    publickey = builder.sign(
        privatekey, hashes.SHA256(), default_backend()
    )

    with open(filename, "wb") as certfile:
        certfile.write(publickey.public_bytes(serialization.Encoding.PEM))

    return publickey

def generatecsr(privatekey, filename, **kwargs):
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, kwargs["country"]),
            x509.NameAttribute(
                NameOID.STATE_OR_PROVINCE_NAME, kwargs["state"]
            ),
            x509.NameAttribute(NameOID.LOCALITY_NAME, kwargs["locality"]),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, kwargs["org"]),
            x509.NameAttribute(NameOID.COMMON_NAME, kwargs["hostname"]),
        ]
    )

    # Generate any alternative dns names
    alt_names = []
    for name in kwargs.get("alt_names", []):
        alt_names.append(x509.DNSName(name))
    SAN = x509.SubjectAlternativeName(alt_names)

    builder = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(subject)
        .add_extension(SAN, critical=False)
    )

    csr = builder.sign(privatekey, hashes.SHA256(), default_backend())

    with open(filename, "wb") as csrfile:
        csrfile.write(csr.public_bytes(serialization.Encoding.PEM))

    return csr

def signcsr(csr, capublickey, caprivatekey, newfilename):
    validfrom = datetime.utcnow()
    validuntil = validfrom + timedelta(days=30)

    builder = (
        x509.CertificateBuilder()
        .subject_name(csr.subject)
        .issuer_name(capublickey.subject)
        .public_key(csr.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(validfrom)
        .not_valid_after(validuntil)
    )

    for extension in csr.extensions:
        builder = builder.add_extension(extension.value, extension.critical)

    publickey = builder.sign(
        private_key=caprivatekey,
        algorithm=hashes.SHA256(),
        backend=default_backend(),
    )

    with open(newfilename, "wb") as keyfile:
        keyfile.write(publickey.public_bytes(serialization.Encoding.PEM))


def generateshortprivatekey(filename: str, password: str):
    privatekey = rsa.generate_private_key(
        public_exponent=65537, key_size=1024, backend=default_backend()
    )

    utf8pass = password.encode("utf-8")
    algorithm = serialization.BestAvailableEncryption(utf8pass)

    with open(filename, "wb") as keyfile:
        keyfile.write(
            privatekey.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=algorithm,
            )
        )

    return privatekey

def generateshortpublickey(privatekey, filename, **kwargs):
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, kwargs["country"]),
            x509.NameAttribute(
                NameOID.STATE_OR_PROVINCE_NAME, kwargs["state"]
            ),
            x509.NameAttribute(NameOID.LOCALITY_NAME, kwargs["locality"]),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, kwargs["org"]),
            x509.NameAttribute(NameOID.COMMON_NAME, kwargs["hostname"]),
        ]
    )
    issuer = subject

    # This certificate is valid from now until 1 days
    validfrom = datetime.utcnow()
    validto = validfrom + timedelta(days=1)

    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(privatekey.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(validfrom)
        .not_valid_after(validto)
        .add_extension(x509.BasicConstraints(ca=True,
            path_length=None), critical=True)
    )
    publickey = builder.sign(
        privatekey, hashes.SHA256(), default_backend()
    )
    with open(filename, "wb") as certfile:
        certfile.write(publickey.public_bytes(serialization.Encoding.PEM))

    return publickey


Password = str(getpass("Please enter a password for the Certificate Authority:  "))
print("\n")
privatekey = generateprivatekey("ca-private-key.pem", Password)
generatepublickey(
  privatekey,
  filename="ca-public-key.pem",
  country="UK",
  state="Bedfordshire",
  locality="Bedford",
  org="My CA Company",
  hostname="MYca.com",
)


serverpassword = str(getpass("Please enter a password for the Server Certificate:   "))
print("\n")
serverprivatekey = generateprivatekey(
  "server-private-key.pem", serverpassword
)
generatecsr(
  serverprivatekey,
  filename="server-csr.pem",
  country="UK",
  state="Bedfordshire",
  locality="Bedford",
  org="My Server",
  alt_names=["localhost","www.localhost" ,"*"],
  hostname="localhost",
)
csrfile = open("server-csr.pem", "rb")
csr = x509.load_pem_x509_csr(csrfile.read(), default_backend())
capublickeyfile = open("ca-public-key.pem", "rb")
capublickey = x509.load_pem_x509_certificate(
  capublickeyfile.read(), default_backend()
)
caprivatekeyfile = open("ca-private-key.pem", "rb")
caprivatekey = serialization.load_pem_private_key(
  caprivatekeyfile.read(),
  getpass("Please enter the CA private key password:  ").encode("utf-8"),
  default_backend(),
)
signcsr(csr, capublickey, caprivatekey, "server-public-key.pem")
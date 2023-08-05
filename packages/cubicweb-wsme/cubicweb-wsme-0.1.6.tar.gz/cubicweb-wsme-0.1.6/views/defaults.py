from cubes.wsme.types import Base, wsattr, scan


class CWUser(Base):
    __etype__ = 'CWUser'

    __autoattr__ = True
    __autoexclude__ = Base.__autoexclude__ + ('in_state',)

    password = wsattr('upassword')


def registration_callback(vreg):
    scan(vreg, __name__)

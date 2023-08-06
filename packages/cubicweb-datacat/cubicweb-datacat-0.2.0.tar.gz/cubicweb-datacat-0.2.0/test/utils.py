"""cubicweb-datacat test utilities"""
from cubicweb import Binary


def create_file(cnx, data, data_name=None, **kwargs):
    """Create a File entity"""
    data_name = data_name or data.decode('utf-8')
    return cnx.create_entity('File', data=Binary(data),
                             data_name=data_name,
                             data_format=u'text/plain', **kwargs)

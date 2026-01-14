from outline_vpn.outline_vpn import OutlineVPN


# {"apiUrl":"https://57.129.138.22:26835/QCQ_PXe8O5UMMKV0TnIpgw","certSha256":"D1936FA19A5ACBFFDA6EB5F3C9F31ECF3E20FDF3C6D60788920854B121F92FAE"}

# api_url = 'https://57.129.138.22:26835/QCQ_PXe8O5UMMKV0TnIpgw'
# cert_sha256 = 'D1936FA19A5ACBFFDA6EB5F3C9F31ECF3E20FDF3C6D60788920854B121F92FAE'

api_url = 'https://91.196.34.71:19911/iMi9_BEwbaP90iOc0FTP9A'
cert_sha256 = '45475D744E58A210A3842EF260016BDC5EBBE989099350168F12591D87FFC558'

client = OutlineVPN(api_url=api_url, cert_sha256=cert_sha256)


def gb_to_bytes(gb: float):
    bytes_in_gb = 1024 ** 3  # 1 ГБ = 1024^3 байт
    return int(gb * bytes_in_gb)


# a = client.create_key(key_id=None, name='123343242344', data_limit=None)
# print(a.key_id)


# def get_keys():
#     return client.get_keys()

def create_new_key(name: str, key_id: str = None, data_limit_gb: float = None):
    new_key = client.create_key(key_id=key_id, name=name, data_limit=None)
    return new_key.access_url, new_key.key_id

def delete_key(key_id: str):
    delete = client.delete_key(key_id)
    if delete:
        return True

# create_new_key('test')
# vpn_keyscreate_new_key = get_keys()
# for key in vpn_keys:
#     print(key.name)


import rsa

(public_key, private_key) = rsa.newkeys(4096)

pukey = open('publickey.key','wb')
pukey.write(public_key.save_pkcs1('PEM'))
pukey.close()

prikey = open('privatekey.key','wb')
prikey.write(private_key.save_pkcs1('PEM'))
prikey.close()

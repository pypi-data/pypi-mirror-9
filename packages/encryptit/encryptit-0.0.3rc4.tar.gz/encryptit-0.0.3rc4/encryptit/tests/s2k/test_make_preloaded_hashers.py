from nose.tools import assert_equal

from encryptit.hash_algorithms import MD5, SHA1, SHA224, SHA256, SHA384, SHA512

from encryptit.string_to_key_specifiers import make_preloaded_hashers

# You can generate test data by doing eg:
#
# for i in 0 1 2; do dd if=/dev/zero bs=1 count=$i | sha384sum; done
#

MD5_0 = 'd41d8cd98f00b204e9800998ecf8427e'
MD5_1 = '93b885adfe0da089cdf634904fd59f71'
MD5_2 = 'c4103f122d27677c9db144cae1394a66'

SHA1_0 = 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
SHA1_1 = '5ba93c9db0cff93f52b521d7420e43f6eda2784f'
SHA1_2 = '1489f923c4dca729178b3e3233458550d8dddf29'

SHA224_0 = 'd14a028c2a3a2bc9476102bb288234c415a2b01f828ea62ac5b3e42f'
SHA224_1 = 'fff9292b4201617bdc4d3053fce02734166a683d7d858a7f5f59b073'
SHA224_2 = 'ce415cdb385b7a540779f1ed33ae41bac19ac1e55370ac9bc454586d'

SHA256_0 = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
SHA256_1 = '6e340b9cffb37a989ca544e6bb780a2c78901d3fb33738768511a30617afa01d'
SHA256_2 = '96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7'

SHA384_0 = ('38b060a751ac96384cd9327eb1b1e36a21fdb71114be07434c0cc7bf63f6e1d'
            'a274edebfe76f65fbd51ad2f14898b95b')
SHA384_1 = ('bec021b4f368e3069134e012c2b4307083d3a9bdd206e24e5f0d86e13d66366'
            '55933ec2b413465966817a9c208a11717')
SHA384_2 = ('1dd6f7b457ad880d840d41c961283bab688e94e4b59359ea45686581e90fecc'
            'ea3c624b1226113f824f315eb60ae0a7c')

SHA512_0 = ('cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce'
            '47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e')
SHA512_1 = ('b8244d028981d693af7b456af8efa4cad63d282e19ff14942c246e50d9351d22'
            '704a802a71c3580b6370de4ceb293c324a8423342557d4e5c38438f0e36910ee')
SHA512_2 = ('5ea71dc6d0b4f57bf39aadd07c208c35f06cd2bac5fde210397f70de11d439c6'
            '2ec1cdf3183758865fd387fcea0bada2f6c37a4a17851dd1d78fefe6f204ee54')

TEST_DATA = {
    (MD5, 1): [MD5_0],
    (MD5, 2): [MD5_0, MD5_1],
    (MD5, 3): [MD5_0, MD5_1, MD5_2],

    (SHA1, 1): [SHA1_0],
    (SHA1, 2): [SHA1_0, SHA1_1],
    (SHA1, 3): [SHA1_0, SHA1_1, SHA1_2],

    (SHA224, 1): [SHA224_0],
    (SHA224, 2): [SHA224_0, SHA224_1],
    (SHA224, 3): [SHA224_0, SHA224_1, SHA224_2],

    (SHA256, 1): [SHA256_0],
    (SHA256, 2): [SHA256_0, SHA256_1],
    (SHA256, 3): [SHA256_0, SHA256_1, SHA256_2],

    (SHA384, 1): [SHA384_0],
    (SHA384, 2): [SHA384_0, SHA384_1],
    (SHA384, 3): [SHA384_0, SHA384_1, SHA384_2],

    (SHA512, 1): [SHA512_0],
    (SHA512, 2): [SHA512_0, SHA512_1],
    (SHA512, 3): [SHA512_0, SHA512_1, SHA512_2],
}


def test_hashers():
    for (hash_algorithm, num_hashers) in TEST_DATA.keys():
        yield (_check_required_hashers, hash_algorithm, num_hashers)


def _check_required_hashers(hash_algorithm, num_hashers):
    hashers = make_preloaded_hashers(hash_algorithm, num_hashers)
    expected = TEST_DATA[(hash_algorithm, num_hashers)]

    assert_equal(
        expected,
        [h.hexdigest() for h in hashers])
